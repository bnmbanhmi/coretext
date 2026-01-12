import asyncio
from surrealdb import AsyncSurreal

async def check():
    async with AsyncSurreal("ws://localhost:8010/rpc") as db:
        await db.connect()
        await db.use("coretext", "coretext")
        
        # Check for test_sync.md
        print("Checking for test_sync.md...")
        # Path is relative to project root. _coretext/test_sync.md
        node_id = "node:`_coretext/test_sync.md`" 
        try:
            res = await db.query(f"SELECT * FROM {node_id}")
            print(f"Node result: {res}")
        except Exception as e:
            print(f"Error selecting node: {e}")

        # Check for edges from this node
        print("Checking edges...")
        try:
            edges = await db.query(f"SELECT * FROM contains WHERE in = {node_id}")
            print(f"Contains edges: {edges}")
        except Exception as e:
             print(f"Error checking edges: {e}")

if __name__ == "__main__":
    asyncio.run(check())
