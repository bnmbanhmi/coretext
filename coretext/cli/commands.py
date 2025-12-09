import typer
import asyncio
from pathlib import Path
from surrealdb import Surreal
from coretext.db.client import SurrealDBClient
from coretext.db.migrations import SchemaManager

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
        # This content should ideally come from a template or a default in the parser module
        default_schema_content = """
node_types:
  file:
    db_table: node
    properties:
      path:
        type: str
      title:
        type: str
      summary:
        type: str
  header:
    db_table: node
    properties:
      path:
        type: str
      level:
        type: int
      title:
        type: str
      content_hash:
        type: str

edge_types:
  contains:
    db_table: contains
    source_type: file
    target_type: header
    properties:
      order:
        type: int
  parent_of:
    db_table: parent_of
    source_type: header
    target_type: header
    properties: {}
"""
        schema_map_path.write_text(default_schema_content)
        typer.echo("Default schema_map.yaml created.")
    else:
        typer.echo("schema_map.yaml already exists. Skipping creation.")

    typer.echo("CoreText project initialized successfully.")

@app.command()
def apply_schema(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p", help="Root directory of the project.")
):
    """
    Applies the schema from .coretext/schema_map.yaml to the local SurrealDB.
    Starts the DB temporarily if not running.
    """
    typer.echo("Applying database schema...")
    
    async def _run_apply():
        client = SurrealDBClient(project_root=project_root)
        
        # Ensure DB is up
        started_by_us = False
        if not client.process: # Simple check, ideally we check if port is open
             # For now, let's just try to start it. client.start_surreal_db handles "already running" logic 
             # but check is internal. We rely on the client.
             await client.start_surreal_db()
             # We give it a moment or loop check health (TODO: health check in client)
             await asyncio.sleep(1) # temporary wait for startup
             started_by_us = True

        try:
            # Connect
            async with Surreal("ws://localhost:8000/rpc") as db:
                await db.signin({"user": "root", "pass": "root"})
                await db.use("coretext", "coretext") # Namespace, Database
                
                migration = SchemaManager(db, project_root)
                await migration.apply_schema()
                typer.echo("Schema applied successfully.")
        except Exception as e:
            typer.echo(f"Error applying schema: {e}", err=True)
            raise
        finally:
            if started_by_us:
                await client.stop_surreal_db()

    try:
        asyncio.run(_run_apply())
    except Exception:
        raise typer.Exit(code=1)
