import typer
import asyncio
import stat
import subprocess
import sys
import os
import signal
import socket
import time
import httpx
from typing import List, Optional
from pathlib import Path
from surrealdb import AsyncSurreal
from coretext.db.client import SurrealDBClient
from coretext.db.migrations import SchemaManager
from coretext.core.parser.schema import DEFAULT_SCHEMA_MAP_CONTENT, SchemaMapper
from coretext.config import DEFAULT_CONFIG_CONTENT, load_config

# Moved imports to module level for better testability and consistency
from coretext.core.sync.engine import SyncEngine, SyncMode
from coretext.core.sync.git_utils import get_staged_files, get_staged_content, get_last_commit_files, get_head_content, get_current_commit_hash
from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.manager import GraphManager
from coretext.core.templates.manager import TemplateManager

from coretext.cli.utils import check_daemon_health, get_hooks_paused_path, build_dependency_tree
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from coretext.core.sync.timeout_utils import run_with_timeout_or_detach
from coretext.core.network import is_port_in_use

PAUSE_FILE_NAME = "hooks_paused"

app = typer.Typer()

@app.command()
def status(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Checks the operational status and health of the CoreText daemon.
    """
    console = Console()
    
    config_path = project_root / ".coretext" / "config.yaml"
    if not config_path.exists():
        console.print(Panel("[red]Coretext not initialized.[/red] Run 'coretext init' first.", title="Error"))
        raise typer.Exit(code=1)
        
    config = load_config(project_root)
    # Check health of both components
    health_info = check_daemon_health(server_port=config.mcp_port, db_port=config.daemon_port, project_root=project_root)
    
    # -- Server Status --
    server_status = health_info["server"]["status"]
    server_color = "green" if server_status == "Running" else "red" if server_status == "Stopped" else "yellow"
    
    # -- DB Status --
    db_status = health_info["database"]["status"]
    db_color = "green" if db_status == "Running" else "red" if db_status == "Stopped" else "yellow"
    
    # -- Hook Status --
    hooks_paused_file = get_hooks_paused_path(project_root)
    hook_status = "Paused" if hooks_paused_file.exists() else "Active"
    hook_color = "yellow" if hook_status == "Paused" else "green"
    
    table = Table(show_header=False, box=None)
    table.add_row("Server Status:", f"[{server_color}]{server_status}[/{server_color}]")
    table.add_row("Server Port:", str(health_info["server"]["port"]))
    table.add_row("Server PID:", str(health_info["server"]["pid"]) if health_info["server"]["pid"] else "N/A")
    table.add_row("Server Version:", health_info["server"]["version"])
    table.add_section()
    table.add_row("Database Status:", f"[{db_color}]{db_status}[/{db_color}]")
    table.add_row("Database Port:", str(health_info["database"]["port"]))
    table.add_row("Database PID:", str(health_info["database"]["pid"]) if health_info["database"]["pid"] else "N/A")
    table.add_section()
    table.add_row("Sync Hook Status:", f"[{hook_color}]{hook_status}[/{hook_color}]")
    
    console.print(Panel(table, title="CoreText Status", expand=False))

@app.command()
def lint(
    files: Optional[List[str]] = typer.Argument(None, help="List of files to lint. If empty, lints all files."),
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Runs integrity checks (linting) on Markdown files via the daemon.
    """
    console = Console()
    
    config_path = project_root / ".coretext" / "config.yaml"
    if not config_path.exists():
        console.print(Panel("[red]Coretext not initialized.[/red] Run 'coretext init' first.", title="Error"))
        raise typer.Exit(code=1)
        
    config = load_config(project_root)
    
    health_info = check_daemon_health(server_port=config.mcp_port, db_port=config.daemon_port, project_root=project_root)
    if health_info["server"]["status"] != "Running":
        console.print(Panel("[red]Daemon is not running.[/red] Run 'coretext start' first.", title="Error"))
        raise typer.Exit(code=1)
        
    try:
        with console.status("[bold green]Running lint check..."):
            payload = {"files": files} if files else {}
            payload["project_root"] = str(project_root.resolve())
            
            response = httpx.post(
                f"http://localhost:{config.mcp_port}/lint",
                json=payload,
                timeout=30.0
            )
            
        if response.status_code == 200:
            report = response.json()
            issues = report.get("issues", [])
            
            if not issues:
                console.print("[bold green]✅ No issues found.[/bold green]")
                raise typer.Exit(code=0)
            
            # Display issues using Rich Table
            table = Table(title=f"Lint Issues Found: {len(issues)}")
            table.add_column("File", style="cyan")
            table.add_column("Line", style="magenta")
            table.add_column("Type", style="yellow")
            table.add_column("Message", style="white")
            
            for issue in issues:
                table.add_row(
                    issue["file_path"],
                    str(issue["line_number"]),
                    issue["error_type"],
                    issue["message"]
                )
                
            console.print(table)
            console.print(f"[bold red]Found {len(issues)} issues.[/bold red]")
            raise typer.Exit(code=1)
            
        else:
            console.print(f"[red]Error {response.status_code}:[/red] {response.text}")
            raise typer.Exit(code=1)
            
    except httpx.RequestError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        raise typer.Exit(code=1)

@app.command()
def init(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project."),
    surreal_version: str = typer.Option("2.0.4", "--surreal-version", "-s", help="Version of SurrealDB to download.")
):
    """
    Initializes the CoreText project.
    Downloads the platform-specific SurrealDB binary and ensures necessary directories exist.
    """
    typer.echo("Initializing CoreText project...")

    db_client = SurrealDBClient(project_root=project_root)
    
    # AC 1: Create default config.yaml
    config_path = project_root / ".coretext" / "config.yaml"
    if not config_path.exists():
        typer.echo(f"Creating default configuration at {config_path}...")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(DEFAULT_CONFIG_CONTENT)
        typer.echo("Default configuration created.")
    else:
        typer.echo("Configuration file already exists. Skipping creation.")

    # AC 2: Download and cache embedding model
    typer.echo("Downloading and caching embedding model (nomic-embed-text-v1.5)...")
    try:
        from sentence_transformers import SentenceTransformer
        # Use a global cache directory for the model to avoid re-downloading per project
        cache_dir = Path.home() / ".coretext" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        # nomic-embed-text-v1.5 requires trust_remote_code=True
        SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True, cache_folder=str(cache_dir))
        typer.echo(f"Embedding model cached successfully in {cache_dir}.")
    except Exception as e:
        typer.echo(f"Warning: Failed to download/cache embedding model: {e}", err=True)
        typer.echo("You may need an internet connection for the first initialization.", err=True)

    # AC 3: Download SurrealDB binary
    typer.echo(f"Downloading SurrealDB binary (version: {surreal_version})...")
    try:
        asyncio.run(db_client.download_surreal_binary(version=surreal_version))
        typer.echo(f"SurrealDB binary downloaded to {db_client.surreal_path}")
    except Exception as e:
        typer.echo(f"Error downloading SurrealDB binary: {e}", err=True)
        raise typer.Exit(code=1)

    # AC 4: Ensure surreal.db parent directory exists
    typer.echo(f"Ensuring SurrealDB database file directory exists at {db_client.db_path.parent}...")
    db_client.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # AC 5: Create default schema_map.yaml if it doesn't exist
    schema_map_path = project_root / ".coretext" / "schema_map.yaml"
    if not schema_map_path.exists():
        typer.echo(f"Creating default schema_map.yaml at {schema_map_path}...")
        schema_map_path.parent.mkdir(parents=True, exist_ok=True)
        schema_map_path.write_text(DEFAULT_SCHEMA_MAP_CONTENT)
        typer.echo("Default schema_map.yaml created.")
    else:
        typer.echo("schema_map.yaml already exists. Skipping creation.")

    # Ensure hooks are unpaused on init
    pause_file = project_root / ".coretext" / PAUSE_FILE_NAME
    if pause_file.exists():
        pause_file.unlink()

    if typer.confirm("Do you want to start the coretext daemon now?", default=True):
        try:
            start(project_root=project_root)
        except Exception as e:
            typer.echo(f"Error starting CoreText daemon: {e}", err=True)
            raise typer.Exit(code=1)

    typer.echo("CoreText project initialized successfully.")

def check_pid_running(pid_file: Path) -> bool:
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)
            return True
        except (ValueError, OSError):
            return False
    return False

@app.command()
def start(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Starts the CoreText daemon (SurrealDB and FastAPI server) in the background.
    """
    # Unpause hooks
    pause_file = project_root / ".coretext" / PAUSE_FILE_NAME
    if pause_file.exists():
        pause_file.unlink()
        typer.echo("CoreText hooks unpaused.")

    config = load_config(project_root)
    db_client = SurrealDBClient(project_root=project_root)
    
    # Robustness checks
    server_pid_file = project_root / ".coretext" / "server.pid"
    
    db_running = asyncio.run(db_client.is_running())
    server_running = check_pid_running(server_pid_file)
    
    if db_running and server_running:
        typer.echo("CoreText daemon and server are already running.")
        if not typer.confirm("Do you want to attempt restarting?", default=False):
            return

    if not db_client.surreal_path.exists():
         typer.echo("SurrealDB binary not found. Please run 'coretext init' first.", err=True)
         raise typer.Exit(code=1)

    # Start SurrealDB
    if not db_running:
        typer.echo(f"Starting SurrealDB from {db_client.surreal_path}...")
        try:
            if is_port_in_use(config.daemon_port):
                typer.echo(f"Warning: Port {config.daemon_port} is already in use. DB start might fail.", err=True)
            
            db_client.start_detached(port=config.daemon_port)
            
            # Wait for DB to be up
            retries = 10
            while retries > 0:
                if is_port_in_use(config.daemon_port):
                    break
                time.sleep(0.5)
                retries -= 1
            
            if retries == 0:
                typer.echo("Warning: SurrealDB process started but port is not yet open. It might be initializing...", err=True)
            else:
                 typer.echo(f"SurrealDB started on port {config.daemon_port}.")

        except Exception as e:
            typer.echo(f"Error starting SurrealDB: {e}", err=True)
            raise typer.Exit(code=1)
    else:
        typer.echo("SurrealDB is already running.")

    # Start FastAPI Server
    if not server_running:
        typer.echo("Starting FastAPI server...")
        try:
            if is_port_in_use(config.mcp_port):
                 typer.echo(f"Warning: Port {config.mcp_port} is already in use. Server start might fail.", err=True)

            fastapi_cmd = [
                 sys.executable, "-m", "uvicorn", 
                 "coretext.server.app:app", 
                 "--host", "127.0.0.1", 
                 "--port", str(config.mcp_port)
            ]
            
            proc_server = subprocess.Popen(
                fastapi_cmd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            server_pid_file.parent.mkdir(parents=True, exist_ok=True)
            server_pid_file.write_text(str(proc_server.pid))
            
            # Wait for Server to be up
            retries = 10
            while retries > 0:
                if is_port_in_use(config.mcp_port):
                    break
                time.sleep(0.5)
                retries -= 1
                
            if retries == 0:
                 typer.echo("Warning: FastAPI server process started but port is not yet open.", err=True)
            else:
                 typer.echo(f"FastAPI server started on port {config.mcp_port}.")

        except Exception as e:
            typer.echo(f"Error starting FastAPI server: {e}", err=True)
            raise typer.Exit(code=1)
    else:
        typer.echo("FastAPI server is already running.")
        
    # AC6: Automatically apply schema after daemon starts
    typer.echo("Applying schema automatically...")
    try:
        # Give a little more time for the socket to be fully ready for HTTP/WS protocol
        time.sleep(1)
        asyncio.run(_apply_schema_logic(project_root))
        typer.echo("Schema applied successfully during initialization.")
    except Exception as e:
        typer.echo(f"Warning: Failed to apply schema automatically after daemon start: {e}", err=True)
        typer.echo("Please run 'coretext apply-schema' manually if schema was not applied.", err=True)

@app.command()
def stop(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Stops the CoreText daemon (SurrealDB and FastAPI server).
    """
    typer.echo("Stopping CoreText daemon...")
    
    # Pause hooks
    pause_file = project_root / ".coretext" / PAUSE_FILE_NAME
    if not pause_file.parent.exists():
        pause_file.parent.mkdir(parents=True, exist_ok=True)
    pause_file.touch()
    typer.echo("CoreText hooks paused.")

    # Stop FastAPI Server
    server_pid_file = project_root / ".coretext" / "server.pid"
    if server_pid_file.exists():
        try:
            pid = int(server_pid_file.read_text().strip())
            typer.echo(f"Stopping FastAPI server (PID {pid})...")
            os.kill(pid, signal.SIGTERM)
            # Wait a bit for it to stop
            for _ in range(20):
                try:
                    os.kill(pid, 0)
                    asyncio.run(asyncio.sleep(0.1))
                except OSError:
                    break
            else:
                # Force kill if still running
                os.kill(pid, signal.SIGKILL)
            typer.echo("FastAPI server stopped.")
        except (ProcessLookupError, ValueError, OverflowError):
            typer.echo("FastAPI server process not found (already stopped?).")
        except Exception as e:
            typer.echo(f"Warning: Failed to stop FastAPI server: {e}", err=True)
        finally:
            if server_pid_file.exists():
                server_pid_file.unlink()

    db_client = SurrealDBClient(project_root=project_root)
    try:
        asyncio.run(db_client.stop_surreal_db())
        typer.echo("CoreText daemon stopped.")
    except Exception as e:
        typer.echo(f"Error stopping CoreText daemon: {e}", err=True)
        raise typer.Exit(code=1)

async def _apply_schema_logic(project_root: Path):
    """
    Internal logic to apply the schema from .coretext/schema_map.yaml to the local SurrealDB.
    Starts the DB temporarily if not running.
    """
    client = SurrealDBClient(project_root=project_root)
    config = load_config(project_root)
    
    # Ensure DB is up
    started_by_us = False
    if not await client.is_running(): # Check if it's already running
         typer.echo("SurrealDB is not running, attempting to start temporarily for schema application.", err=True)
         await client.start_surreal_db(port=config.daemon_port)
         started_by_us = True

    # Retry loop for connection
    max_retries = 10
    url = f"ws://localhost:{config.daemon_port}/rpc"
    for i in range(max_retries):
        try:
            async with AsyncSurreal(url) as db:
                await db.use("coretext", "coretext") # Namespace, Database
                
                migration = SchemaManager(db, project_root)
                await migration.apply_schema()
                typer.echo("Schema applied successfully.")
                break # Success
        except Exception as e:
            if i == max_retries - 1:
                typer.echo(f"Error applying schema after {max_retries} attempts: {e}", err=True)
                raise
            await asyncio.sleep(0.5)
    
    if started_by_us:
        typer.echo("Stopping temporary SurrealDB server after schema application.")
        await client.stop_surreal_db()

@app.command()
def apply_schema(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Applies the schema from .coretext/schema_map.yaml to the local SurrealDB.
    Starts the DB temporarily if not running.
    """
    typer.echo("Applying database schema...")
    try:
        asyncio.run(_apply_schema_logic(project_root))
    except Exception:
        raise typer.Exit(code=1)

@app.command()
def new(
    template_name: Optional[str] = typer.Argument(None, help="Name of the template to use."),
    output_path: Optional[str] = typer.Argument(None, help="Path where the new file should be created."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file if it exists."),
    list_templates: bool = typer.Option(False, "--list", "-l", help="List available templates.")
):
    """
    Generates a new Markdown file from a BMAD template.
    """
    console = Console()
    
    # Check if we should just list templates
    if list_templates or (template_name is None and output_path is None):
        try:
            templates = TemplateManager.list_templates()
            table = Table(title="Available Templates")
            table.add_column("Template Name", style="cyan")
            for t in templates:
                table.add_row(t)
            console.print(table)
            raise typer.Exit()
        except Exception as e:
            if isinstance(e, typer.Exit):
                raise
            console.print(f"[red]Error listing templates: {e}[/red]")
            raise typer.Exit(code=1)

    if template_name is None:
        console.print("[red]Error: Template name is required.[/red]")
        raise typer.Exit(code=1)

    if output_path is None:
        console.print("[red]Error: Output path is required.[/red]")
        raise typer.Exit(code=1)

    try:
        content = TemplateManager.get_template_content(template_name)
    except FileNotFoundError:
        console.print(f"[red]Error: Template '{template_name}' not found.[/red]")
        console.print("Run 'coretext new --list' to see available templates.")
        raise typer.Exit(code=1)

    target_path = Path(output_path)
    
    # Check for existing file
    if target_path.exists() and not force:
        console.print(f"[red]Error: File '{target_path}' already exists.[/red]")
        console.print("Use --force to overwrite.")
        raise typer.Exit(code=1)

    # Ensure directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        target_path.write_text(content, encoding="utf-8")
        console.print(f"[green]Successfully created '{target_path}' using template '{template_name}'.[/green]")
    except Exception as e:
        console.print(f"[red]Error writing file: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def ping():
    typer.echo("pong")

@app.command()
def install_hooks(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Installs Git hooks for coretext synchronization.
    """
    git_dir = project_root / ".git"
    if not git_dir.exists():
        typer.echo("Error: .git directory not found. Is this a git repository?", err=True)
        raise typer.Exit(code=1)
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    python_exec = sys.executable

    # Pre-commit hook
    pre_commit_path = hooks_dir / "pre-commit"
    pre_commit_content = f"""#!/bin/sh
# CoreText Pre-commit Hook
# generated by coretext install-hooks

"{python_exec}" -m coretext.cli.main hook pre-commit
"""
    pre_commit_path.write_text(pre_commit_content)
    pre_commit_path.chmod(pre_commit_path.stat().st_mode | stat.S_IEXEC)
    typer.echo(f"Installed pre-commit hook to {pre_commit_path}")
    
    # Post-commit hook
    post_commit_path = hooks_dir / "post-commit"
    post_commit_content = f"""#!/bin/sh
# CoreText Post-commit Hook
# generated by coretext install-hooks

"{python_exec}" -m coretext.cli.main hook post-commit &
"""
    post_commit_path.write_text(post_commit_content)
    post_commit_path.chmod(post_commit_path.stat().st_mode | stat.S_IEXEC)
    typer.echo(f"Installed post-commit hook to {post_commit_path}")

# Hook commands group
hook_app = typer.Typer()
app.add_typer(hook_app, name="hook", help="Git hook commands.")

@hook_app.command("pre-commit")
def pre_commit_hook(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p")
):
    """
    Executed by Git pre-commit hook. Runs in dry-run/lint mode.
    """
    if (project_root / ".coretext" / PAUSE_FILE_NAME).exists():
        return

    # 1. Change detection
    try:
        files = get_staged_files(project_root)
    except Exception as e:
        typer.echo(f"Warning: Could not detect staged files: {e}", err=True)
        return

    if not files:
        return

    typer.echo(f"Checking {len(files)} staged Markdown files...")
    
    parser = MarkdownParser(project_root=project_root)
    # No DB needed for dry run
    engine = SyncEngine(parser=parser, graph_manager=None, project_root=project_root)
    
    # Content provider lambda
    def content_provider(file_path_str: str) -> str:
        return get_staged_content(project_root, file_path_str)

    async def _run():
        result = await engine.process_files(files, mode=SyncMode.DRY_RUN, content_provider=content_provider)
        return result

    try:
        result = asyncio.run(_run())
        
        if not result.success:
            typer.echo("❌ CoreText Pre-commit Check FAILED:", err=True)
            for error in result.errors:
                typer.echo(f"  - {error}", err=True)
            raise typer.Exit(code=1)
        
        typer.echo("✅ CoreText Pre-commit Check PASSED.")
    except Exception as e:
        if isinstance(e, typer.Exit):
            raise
        typer.echo(f"Unexpected error in pre-commit hook: {e}", err=True)
        raise typer.Exit(code=1)


@hook_app.command("post-commit")
def post_commit_hook(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p"),
    detached: bool = typer.Option(False, "--detached", help="Internal flag for detached subprocess calls.")
):
    """
    Executed by Git post-commit hook. Runs in write/sync mode.
    Wrapper to run async logic.
    """
    if (project_root / ".coretext" / PAUSE_FILE_NAME).exists():
        if not detached: # Only verify on main process to avoid noise
             pass # Silent exit
        return

    asyncio.run(_post_commit_hook_logic(project_root, detached))

async def _post_commit_hook_logic(project_root: Path, detached: bool):
    """
    Actual async logic for post-commit hook.
    """
    if detached:
        # This is the detached process, execute sync logic directly
        typer.echo("Running CoreText post-commit hook (detached process)...")
    else:
        typer.echo("Running CoreText post-commit hook...")

    # Set up DB client
    db_client = SurrealDBClient(project_root=project_root)
    config = load_config(project_root)
    
    try:
        files = get_last_commit_files(project_root)
    except Exception as e:
        typer.echo(f"Warning: Could not detect last commit files: {e}", err=True)
        # Fail-Open: continue without processing files
        if detached: # If detached, it should exit.
             raise typer.Exit(code=0)
        return

    if not files:
        typer.echo("No Markdown files changed in last commit to synchronize.")
        if detached: # If detached, it should exit.
            raise typer.Exit(code=0)
        return

    typer.echo(f"Synchronizing {len(files)} Markdown files from last commit...")

    async def _run_sync_logic(): # Renamed _run_sync to _run_sync_logic to avoid name clash
        started_db_by_us = False
        
        # Get current commit hash
        current_commit_hash = get_current_commit_hash(project_root)
        if not current_commit_hash:
            typer.echo("Warning: Could not retrieve current Git commit hash. Synchronization will proceed without versioning.", err=True)
        
        try:
            # Attempt to start DB if not running
            # In post-commit, we should aim for quick connection, not blocking startup.
            # This is a simplified approach; a robust solution would use a daemonized DB.
            if not await db_client.is_running():
                typer.echo("SurrealDB is not running, attempting to start for synchronization.", err=True)
                await db_client.start_surreal_db(port=config.daemon_port)
                started_db_by_us = True

            # Connect to SurrealDB
            async with AsyncSurreal(f"ws://localhost:{config.daemon_port}/rpc") as db:
                await db.use("coretext", "coretext")

                schema_map_path = project_root / ".coretext" / "schema_map.yaml"
                schema_mapper = SchemaMapper(schema_map_path)
                
                graph_manager = GraphManager(db, schema_mapper)
                parser = MarkdownParser(project_root=project_root)
                engine = SyncEngine(parser=parser, graph_manager=graph_manager, project_root=project_root)

                # Content provider lambda: uses HEAD content for deterministic sync
                def content_provider(file_path_str: str) -> str:
                    return get_head_content(project_root, file_path_str)

                result = await engine.process_files(files, mode=SyncMode.WRITE, content_provider=content_provider, commit_hash=current_commit_hash)
                
                if not result.success:
                    typer.echo("⚠️ CoreText Post-commit Synchronization FAILED:", err=True)
                    for error in result.errors:
                        typer.echo(f"  - {error}", err=True)
                    # Fail-Open: do not block commit, log error and exit gracefully
                    raise typer.Exit(code=0) # Changed to raise
                else:
                    typer.echo("✅ CoreText Post-commit Synchronization COMPLETE.")
                
        except Exception as e:
            typer.echo(f"❌ Unexpected error during post-commit synchronization: {e}", err=True)
            raise typer.Exit(code=0) # Changed to raise
        finally:
            if started_db_by_us:
                typer.echo("Stopping SurrealDB server started for synchronization.")
                await db_client.stop_surreal_db()

    if detached:
        # If detached, run the logic directly
        await _run_sync_logic()
        # Force exit to kill any lingering threads (e.g. PyTorch)
        os._exit(0)
    else:
        # Decide whether to detach or run with timeout
        await run_with_timeout_or_detach(project_root, files, _run_sync_logic)
        # Even the parent process should exit hard if it initialized heavy libs
        os._exit(0)

@app.command()
def inspect(
    node_id: str = typer.Argument(..., help="Node ID or File Path to inspect."),
    depth: int = typer.Option(1, "--depth", "-d", help="Traversal depth."),
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Inspects the dependency tree of a specific node by querying the daemon.
    """
    console = Console()
    
    config_path = project_root / ".coretext" / "config.yaml"
    if not config_path.exists():
        console.print(Panel("[red]Coretext not initialized.[/red] Run 'coretext init' first.", title="Error"))
        raise typer.Exit(code=1)
        
    config = load_config(project_root)
    
    # Check if daemon is running
    health_info = check_daemon_health(server_port=config.mcp_port, db_port=config.daemon_port, project_root=project_root)
    if health_info["server"]["status"] != "Running":
        console.print(Panel("[red]Daemon is not running.[/red] Run 'coretext start' first.", title="Error"))
        raise typer.Exit(code=1)
        
    try:
        with console.status(f"[bold green]Inspecting {node_id}..."):
            response = httpx.post(
                f"http://localhost:{config.mcp_port}/tools/get_dependencies",
                json={"node_identifier": node_id, "depth": depth},
                timeout=10.0
            )
            
        if response.status_code == 200:
            data = response.json()
            dependencies = data.get("dependencies", [])
            
            if not dependencies:
                console.print(f"No dependencies found for [bold blue]{node_id}[/bold blue] (depth {depth}).")
                return
                
            tree = build_dependency_tree(node_id, dependencies)
            console.print(tree)
        elif response.status_code == 404:
            console.print(f"[red]Node not found:[/red] {node_id}. Ensure the file is indexed.")
        else:
            console.print(f"[red]Error {response.status_code}:[/red] {response.text}")
            
    except httpx.RequestError as e:
        console.print(f"[red]Connection error:[/red] {e}")