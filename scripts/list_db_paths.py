import asyncio
from surrealdb import AsyncSurreal
from coretext.config import load_config
from pathlib import Path

async def list_paths():
    config = load_config(Path.cwd())
    async with AsyncSurreal(config.surreal_url) as db:
        await db.connect()
        await db.use(config.surreal_ns, config.surreal_db)
        
        tables = ["node", "contains", "parent_of", "references"]
        for t in tables:
            result = await db.query(f"SELECT count() FROM {t};")
            print(f"Table {t} count: {result}")
            
            if "node" in t:
                data = await db.query(f"SELECT path, node_type FROM {t} LIMIT 5;")
                print(f"Sample {t} data: {data}")


if __name__ == "__main__":
    asyncio.run(list_paths())
