import asyncio
from surrealdb import AsyncSurreal
from coretext.core.graph.manager import GraphManager
from coretext.core.parser.schema import SchemaMapper
from coretext.core.vector.embedder import VectorEmbedder
from pathlib import Path

async def main():
    print("Connecting to DB...")
    db = AsyncSurreal("ws://localhost:8000/rpc")
    await db.connect()
    # Attempt signin if needed
    # await db.signin({"user": "root", "pass": "root"})
    await db.use("coretext", "coretext")
    print("Connected.")

    schema_mapper = SchemaMapper(Path(".coretext/schema_map.yaml"))
    embedder = VectorEmbedder()
    
    manager = GraphManager(db, schema_mapper, embedder)

    print("Testing search_topology...")
    try:
        results = await manager.search_topology("authentication")
        print("Results:", results)
    except Exception as e:
        print("Error in search_topology:", e)
        import traceback
        traceback.print_exc()

    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
