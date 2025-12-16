import typer
import asyncio
import stat
import subprocess
import sys
from pathlib import Path
from typing import Optional # Keep Optional for now, as init uses Path.cwd() which is not Optional
from surrealdb import AsyncSurreal
from coretext.db.client import SurrealDBClient
from coretext.db.migrations import SchemaManager
from coretext.core.parser.schema import DEFAULT_SCHEMA_MAP_CONTENT, SchemaMapper

# Moved imports to module level for better testability and consistency
from coretext.core.sync.engine import SyncEngine, SyncMode
from coretext.core.sync.git_utils import get_staged_files, get_staged_content, get_last_commit_files, get_head_content, get_current_commit_hash
from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.manager import GraphManager

PAUSE_FILE_NAME = "hooks_paused"

app = typer.Typer()

@app.command()
def init(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project."),
    surreal_version: str = typer.Option("1.4.1", "--surreal-version", "-s", help="Version of SurrealDB to download.")
):
    """
    Initializes the CoreText project.
    Downloads the platform-specific SurrealDB binary and ensures necessary directories exist.
    """
    typer.echo("Initializing CoreText project...")

    db_client = SurrealDBClient(project_root=project_root)
    
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

    typer.echo("CoreText project initialized successfully.")

    if typer.confirm("Do you want to start the coretext daemon now?", default=True):
        try:
            # Trigger the start command logic
            # We invoke the logic directly or via subprocess to ensure it runs
            # Since 'start' will detach, we can just call it (if we factor out logic) or call subprocess.
            # But here, we can just call the start command function directly if we move the logic to a helper or just subprocess call here.
            # However, calling another typer command directly is tricky if it relies on context.
            # Let's just execute the start logic here or call the cli command via subprocess?
            # Calling via subprocess `coretext start` assumes coretext is in path.
            # Calling the function `start` directly is better if we just pass arguments.
            start(project_root=project_root)
        except Exception as e:
            typer.echo(f"Error starting CoreText daemon: {e}", err=True)
            raise typer.Exit(code=1)

    typer.echo("CoreText project initialized successfully.")

@app.command()
def start(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Starts the CoreText daemon (SurrealDB) in the background.
    """
    # Unpause hooks
    pause_file = project_root / ".coretext" / PAUSE_FILE_NAME
    if pause_file.exists():
        pause_file.unlink()
        typer.echo("CoreText hooks unpaused.")

    db_client = SurrealDBClient(project_root=project_root)
    if not db_client.surreal_path.exists():
         typer.echo("SurrealDB binary not found. Please run 'coretext init' first.", err=True)
         raise typer.Exit(code=1)

    typer.echo(f"Starting CoreText daemon from {db_client.surreal_path}...")
    
    # Construct command
    cmd = [
        str(db_client.surreal_path),
        "start",
        "--log", "trace",
        "--user", "root",
        "--pass", "root",
        f"rocksdb:{db_client.db_path}",
        "--unauthenticated" # Disable authentication for local development
    ]
    
    try:
        cmd.extend(["--bind", "127.0.0.1:8000"]) # Explicitly bind to localhost:8000

        proc = subprocess.Popen(
            cmd, 
            start_new_session=True, 
            # Remove stdout/stderr redirection to see output directly
            # stdout=subprocess.DEVNULL, 
            # stderr=subprocess.DEVNULL
        )
        
        # Write PID file
        pid_file = project_root / ".coretext" / "daemon.pid"
        pid_file.write_text(str(proc.pid))
        
        typer.echo("CoreText daemon started in background.")
        
        # AC6: Automatically apply schema after daemon starts
        typer.echo("Applying schema automatically...")
        try:
            # We need to wait a moment for the subprocess to fully start and listen
            asyncio.run(asyncio.sleep(2)) # Give it 2 seconds to start
            asyncio.run(_apply_schema_logic(project_root))
            typer.echo("Schema applied successfully during initialization.")
        except Exception as e:
            typer.echo(f"Warning: Failed to apply schema automatically after daemon start: {e}", err=True)
            typer.echo("Please run 'coretext apply-schema' manually if schema was not applied.", err=True)

    except Exception as e:
        typer.echo(f"Error starting CoreText daemon: {e}", err=True)
        raise typer.Exit(code=1)

@app.command()
def stop(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Stops the CoreText daemon.
    """
    typer.echo("Stopping CoreText daemon...")
    
    # Pause hooks
    pause_file = project_root / ".coretext" / PAUSE_FILE_NAME
    if not pause_file.parent.exists():
        pause_file.parent.mkdir(parents=True, exist_ok=True)
    pause_file.touch()
    typer.echo("CoreText hooks paused.")

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
    
    # Ensure DB is up
    started_by_us = False
    if not await client.is_running(): # Check if it's already running
         typer.echo("SurrealDB is not running, attempting to start temporarily for schema application.", err=True)
         await client.start_surreal_db()
         started_by_us = True

    # Retry loop for connection
    max_retries = 10
    for i in range(max_retries):
        try:
            async with AsyncSurreal("ws://localhost:8000/rpc") as db:
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


from coretext.core.sync.timeout_utils import run_with_timeout_or_detach, FILE_COUNT_DETACH_THRESHOLD, TIMEOUT_SECONDS

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
                await db_client.start_surreal_db()
                started_db_by_us = True

            # Connect to SurrealDB
            async with AsyncSurreal("ws://localhost:8000/rpc") as db:
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
    else:
        # Decide whether to detach or run with timeout
        await run_with_timeout_or_detach(project_root, files, _run_sync_logic)

