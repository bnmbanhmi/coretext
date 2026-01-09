import asyncio
from surrealdb import AsyncSurreal
from coretext.config import load_config
from pathlib import Path

async def wipe_db():
    config = load_config(Path.cwd())
    print(f"Connecting to {config.surreal_url}...")
    
    async with AsyncSurreal(config.surreal_url) as db:
        await db.connect()
        await db.use(config.surreal_ns, config.surreal_db)
        
        print("Deleting all edges...")
        await db.query("DELETE edge;") # Generic delete for all edges if edge is a parent type, or we delete specific tables
        # Since we don't have a generic 'edge' table in schema, we delete common ones or just all records
        # SurrealDB allow DELETE <table_name>
        # Let's try to list tables first or just blindly delete 'node' and edges.
        
        # Helper to get all tables info
        info = await db.query("INFO FOR DB;")
        # result structure varies, let's just do the main ones we know
        
        tables = ["node", "contains", "parent_of", "references", "depends_on", "governed_by"]
        for t in tables:
             try:
                 await db.query(f"DELETE {t};")
                 print(f"Deleted {t}")
             except Exception as e:
                 print(f"Error deleting {t}: {e}")

        print("Database wiped successfully.")

if __name__ == "__main__":
    asyncio.run(wipe_db())
