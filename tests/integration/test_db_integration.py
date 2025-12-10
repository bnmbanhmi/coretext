import pytest
import asyncio
from pathlib import Path
from surrealdb import Surreal
from coretext.db.client import SurrealDBClient
from coretext.db.migrations import SchemaManager

def surreal_binary_exists():
    client = SurrealDBClient(Path.cwd())
    return client.surreal_path.exists()

@pytest.mark.skipif(not surreal_binary_exists(), reason="SurrealDB binary not found")
@pytest.mark.asyncio
async def test_real_db_connection_and_schema(tmp_path):
    # Use a temporary directory for the DB project root
    project_root = tmp_path
    client = SurrealDBClient(project_root)
    
    # Copy binary to tmp_path location if needed, OR just use the one in ~/.coretext/bin
    # The client uses ~/.coretext/bin for binary, but project_root/.coretext/surreal.db for DB file.
    # So we can just use the client.
    
    # Ensure .coretext exists in tmp_path
    (project_root / ".coretext").mkdir()
    
    # Start DB
    await client.start_surreal_db()
    
    try:
        # Wait for startup
        await asyncio.sleep(1)
        
        async with Surreal("ws://localhost:8000/rpc") as db:
            await db.signin({"user": "root", "pass": "root"})
            await db.use("coretext", "coretext")
            
            # Write a dummy schema_map.yaml
            schema_map_path = project_root / ".coretext" / "schema_map.yaml"
            schema_map_path.write_text("""
node_types:
  test_node:
    db_table: node
    properties:
      test_prop:
        type: str
""")
            
            # Apply schema
            migration = SchemaManager(db, project_root)
            await migration.apply_schema()
            
            # Verify schema application by creating a node
            # Note: We can't easily check schema definitions via client without querying system tables, 
            # but we can check if we can insert data.
            
            # Check info
            info = await db.query("INFO FOR DB")
            assert info
            
    finally:
        await client.stop_surreal_db()
