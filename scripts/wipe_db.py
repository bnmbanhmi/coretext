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
        
        # Get all table names dynamically using INFO FOR DB
        try:
            info = await db.query("INFO FOR DB;")
            # info structure depends on client version/response format
            # Typical response: [{'result': {'tables': {'node': 'DEFINE TABLE node ...', ...}}}]
            
            tables_to_delete = []
            if isinstance(info, list) and len(info) > 0:
                res = info[0]
                if isinstance(res, dict) and 'result' in res:
                    tables_info = res['result'].get('tables', {})
                    tables_to_delete = list(tables_info.keys())
            
            if not tables_to_delete:
                # Fallback list if discovery fails
                tables_to_delete = ["node", "contains", "parent_of", "references", "depends_on", "governed_by"]
            
            print(f"Found tables: {tables_to_delete}")
            
            for t in tables_to_delete:
                try:
                    await db.query(f"DELETE {t};")
                    print(f"Deleted {t}")
                except Exception as e:
                    print(f"Error deleting {t}: {e}")

            print("Database wiped successfully.")
        except Exception as e:
            print(f"Error during wipe: {e}")

if __name__ == "__main__":
    asyncio.run(wipe_db())
