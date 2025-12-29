#!/usr/bin/env python3
import requests
import json
import sys
from rich.console import Console
from rich.table import Table

console = Console()
BASE_URL = "http://127.0.0.1:8001"

def check_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            console.print("[green]✅ Server is healthy[/green]")
            return True
        else:
            console.print(f"[red]❌ Server returned {response.status_code}[/red]")
            return False
    except requests.exceptions.ConnectionError:
        console.print("[red]❌ Could not connect to server. Is it running?[/red]")
        console.print("Try: poetry run coretext start")
        return False

def check_manifest():
    console.print("\n[bold]Fetching MCP Manifest...[/bold]")
    try:
        response = requests.get(f"{BASE_URL}/mcp/manifest")
        if response.status_code == 200:
            manifest = response.json()
            console.print(json.dumps(manifest, indent=2))
            return True
        else:
            console.print(f"[red]❌ Manifest fetch failed: {response.status_code}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def search_topology(query="authentication"):
    console.print(f"\n[bold]Searching Topology for: '{query}'...[/bold]")
    payload = {"query": query}
    try:
        response = requests.post(f"{BASE_URL}/mcp/tools/search_topology", json=payload)
        if response.status_code == 200:
            results = response.json()
            console.print(json.dumps(results, indent=2))
        else:
            console.print(f"[red]❌ Search failed: {response.status_code} - {response.text}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def get_dependencies(node_id):
    console.print(f"\n[bold]Getting Dependencies for: '{node_id}'...[/bold]")
    payload = {"node_identifier": node_id}
    try:
        response = requests.post(f"{BASE_URL}/mcp/tools/get_dependencies", json=payload)
        if response.status_code == 200:
            results = response.json()
            console.print(json.dumps(results, indent=2))
        else:
            console.print(f"[red]❌ Dependency fetch failed: {response.status_code} - {response.text}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def main():
    console.print("[bold blue]Coretext Epic 2 Demo Script[/bold blue]")
    
    if not check_health():
        sys.exit(1)
        
    check_manifest()
    
    # Example queries
    search_topology("authentication")
    search_topology("Verification")
    search_topology("graph")
    
    # Try to find a file to inspect dependencies on
    get_dependencies("node:`demo_epic_2.md`")
    get_dependencies("file:demo_epic_2.md")

if __name__ == "__main__":
    main()
