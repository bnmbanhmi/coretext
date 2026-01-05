import asyncio
import time
import statistics
from surrealdb import AsyncSurreal
from coretext.server.dependencies import get_schema_mapper, get_vector_embedder
from coretext.core.graph.manager import GraphManager

async def benchmark():
    print("Initializing benchmark...")
    
    # Connect to DB
    from coretext.config import load_config
    from pathlib import Path
    
    config = load_config(Path.cwd())
    
    db = AsyncSurreal(config.surreal_url)
    try:
        await db.connect()
        await db.use(config.surreal_ns, config.surreal_db)
    except Exception as e:
        print(f"Failed to connect to SurrealDB: {e}")
        print("Please ensure the coretext daemon is running.")
        return

    # Initialize components
    try:
        schema_mapper = get_schema_mapper()
        # Pre-load embedder
        print("Loading embedder (this may take a moment)...")
        embedder = get_vector_embedder()
        # Force load model to warm it up
        await embedder.encode("warmup")
    except Exception as e:
        print(f"Failed to initialize components: {e}")
        await db.close()
        return
    
    graph_manager = GraphManager(db, schema_mapper, embedder)

    print("\n--- Benchmarking search_topology ---")
    query = "authentication logic"
    latencies = []
    # Warmup
    await graph_manager.search_topology(query, limit=5)
    
    for _ in range(20):
        start = time.perf_counter()
        await graph_manager.search_topology(query, limit=5)
        latencies.append((time.perf_counter() - start) * 1000)
    
    print_stats("search_topology", latencies)

    print("\n--- Benchmarking get_dependencies ---")
    # Find a node to query. Try to find a file node.
    # search_topology returns nodes with embeddings.
    results = await graph_manager.search_topology("import", limit=5)
    
    node_id = None
    if results:
         node_id = results[0]['id']
    
    if not node_id:
        print("No suitable nodes found to test get_dependencies (search returned empty).")
        # Try to fallback to a likely existing ID if search fails?
        # But search shouldn't fail if DB has data.
    else:
        print(f"Testing with node: {node_id}")
        
        # Warmup
        await graph_manager.get_dependencies(node_id, depth=1)

        latencies = []
        for _ in range(20):
            start = time.perf_counter()
            await graph_manager.get_dependencies(node_id, depth=1)
            latencies.append((time.perf_counter() - start) * 1000)
        
        print_stats("get_dependencies", latencies)

    await db.close()

def print_stats(name, latencies):
    if not latencies:
        print(f"{name}: No data")
        return
    # Python 3.8+ statistics.quantiles
    try:
        # inclusive method is default in 3.10+? 
        # Actually quantiles returns n-1 cut points.
        qs = statistics.quantiles(latencies, n=20)
        p95 = qs[-1] # 19th cut point is 95%
    except AttributeError:
        # Fallback for older python if needed (project says 3.10+ so we are good)
        sorted_lat = sorted(latencies)
        p95 = sorted_lat[int(0.95 * len(latencies))]

    avg = statistics.mean(latencies)
    print(f"{name}: Avg={avg:.2f}ms, P95={p95:.2f}ms")

if __name__ == "__main__":
    asyncio.run(benchmark())
