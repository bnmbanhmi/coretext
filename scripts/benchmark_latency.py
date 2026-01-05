import typer
import asyncio
import httpx
import time
import statistics
from pathlib import Path
from coretext.config import load_config
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def run(
    project_root: Path = typer.Option(Path.cwd(), "--project-root", "-p"),
    iterations: int = typer.Option(50, help="Number of requests to run for statistics"),
    query: str = typer.Option("test", help="Query string for search benchmark")
):
    """
    Benchmarks MCP latency (RTT) for topological search and dependency retrieval.
    Reports P50, P95, and P99 latencies.
    """
    config = load_config(project_root)
    base_url = f"http://localhost:{config.mcp_port}"
    
    # Check health
    try:
        resp = httpx.get(f"{base_url}/health")
        if resp.status_code != 200:
            console.print("[red]Daemon not healthy. Please run 'coretext start'.[/red]")
            raise typer.Exit(1)
    except Exception:
         console.print("[red]Daemon not running. Please run 'coretext start'.[/red]")
         raise typer.Exit(1)

    async def benchmark_search():
        latencies = []
        async with httpx.AsyncClient() as client:
            # Warmup
            await client.post(f"{base_url}/mcp/tools/search_topology", json={"query": query})
            
            with console.status(f"Benchmarking search_topology ({iterations} iter)..."):
                for _ in range(iterations):
                    start = time.perf_counter()
                    await client.post(f"{base_url}/mcp/tools/search_topology", json={"query": query})
                    latencies.append((time.perf_counter() - start) * 1000)
        return latencies

    async def benchmark_dependencies():
        # First get a valid node
        async with httpx.AsyncClient() as client:
            # Try to find a node related to the query, or fallback to file nodes
            resp = await client.post(f"{base_url}/mcp/tools/search_topology", json={"query": "doc"})
            data = resp.json()
            nodes = data.get("nodes", []) if isinstance(data, dict) else []
            
            if not nodes:
                # Try a broader search
                resp = await client.post(f"{base_url}/mcp/tools/search_topology", json={"query": "file"})
                data = resp.json()
                nodes = data.get("nodes", []) if isinstance(data, dict) else []
                
            if not nodes:
                console.print("[yellow]No nodes found to test dependencies (index might be empty).[/yellow]")
                return []
                
            node_id = nodes[0]['id']
            console.print(f"Using node [cyan]{node_id}[/cyan] for dependency benchmark.")
            
            latencies = []
             # Warmup
            await client.post(f"{base_url}/mcp/tools/get_dependencies", json={"node_identifier": node_id})
            
            with console.status(f"Benchmarking get_dependencies ({iterations} iter)..."):
                for _ in range(iterations):
                    start = time.perf_counter()
                    await client.post(f"{base_url}/mcp/tools/get_dependencies", json={"node_identifier": node_id})
                    latencies.append((time.perf_counter() - start) * 1000)
            return latencies

    console.print(f"[bold]Starting Benchmark (RTT to {base_url})[/bold]")
    
    # Run Search
    search_lats = asyncio.run(benchmark_search())
    print_stats("search_topology", search_lats)
    
    # Run Dependencies
    dep_lats = asyncio.run(benchmark_dependencies())
    print_stats("get_dependencies", dep_lats)

def print_stats(name, latencies):
    if not latencies:
        return
    
    p50 = statistics.median(latencies)
    if len(latencies) >= 100:
        quantiles = statistics.quantiles(latencies, n=100)
        p95 = quantiles[94]
        p99 = quantiles[98]
    else:
        # Fallback for small sample size
        sorted_lat = sorted(latencies)
        p95 = sorted_lat[int(0.95 * len(latencies)) - 1]
        p99 = sorted_lat[int(0.99 * len(latencies)) - 1]
    
    table = Table(title=f"{name} Latency (ms)")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("P50", f"{p50:.2f}")
    table.add_row("P95", f"{p95:.2f}")
    table.add_row("P99", f"{p99:.2f}")
    
    console.print(table)

if __name__ == "__main__":
    app()