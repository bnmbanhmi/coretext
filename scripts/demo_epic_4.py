#!/usr/bin/env python3
import asyncio
import argparse
import sys
import time
import shutil
import random
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Add project root to path if coretext is not installed/found
try:
    import coretext
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent))

from coretext.core.sync.engine import SyncEngine, SyncMode
from scripts.generate_stress_data import generate_stress_data

console = Console()
STRESS_DIR = Path("_stress_demo")

def clean_stress_dir():
    if STRESS_DIR.exists():
        shutil.rmtree(STRESS_DIR)
        console.print(f"[dim]Removed {STRESS_DIR}[/dim]")

def setup_data():
    console.print(Panel("Scenario 1: Stress Data Generation", style="bold blue"))
    if STRESS_DIR.exists():
        if not Confirm.ask(f"{STRESS_DIR} exists. Regenerate?"):
            return
        clean_stress_dir()
    
    console.print("[yellow]Generating 50 files with density 5 (clean)...[/yellow]")
    generate_stress_data(output_dir=str(STRESS_DIR), count=50, link_density=5, broken_link_probability=0)
    console.print(f"[green]✓ Generated data in {STRESS_DIR}[/green]")

def cleanup_data():
    console.print(Panel("Cleanup: Removing Test Data", style="bold blue"))
    if STRESS_DIR.exists():
        clean_stress_dir()
        console.print(f"[green]✓ Removed {STRESS_DIR}[/green]")
    else:
        console.print("[yellow]Stress directory not found. Nothing to clean.[/yellow]")

def run_latency_check():
    console.print(Panel("Scenario 2: Latency Benchmark", style="bold blue"))
    if not STRESS_DIR.exists():
        console.print("[red]Stress data not found. Run Setup first.[/red]")
        return

    console.print("[yellow]Running benchmark...[/yellow]")
    # Using the imported function directly if possible, or subprocess
    # Since benchmark_latency might be a script, let's call it via imported main or subprocess
    # Let's assume we can call the function we imported or subprocess it
    import subprocess
    result = subprocess.run([sys.executable, "scripts/benchmark_latency.py", "--project-root", "."], capture_output=True, text=True)
    console.print(result.stdout)
    if result.returncode == 0:
        console.print("[green]✓ Benchmark complete[/green]")
    else:
        console.print(f"[red]Benchmark failed:[/red]\n{result.stderr}")

def simulate_async_hook():
    console.print(Panel("Scenario 3: Async Git Hook Simulation", style="bold blue"))
    console.print("Simulating a commit with [bold]100 files[/bold] (Threshold is 5).")
    
    # Simulation Logic
    files_changed = 100
    threshold = 5
    
    console.print(f"Files changed: {files_changed} > Threshold: {threshold}")
    
    start_time = time.time()
    console.print("[yellow]Hook triggered...[/yellow]")
    
    # Logic from the hook:
    if files_changed > threshold:
        console.print("[cyan]ℹ Async threshold exceeded. Detaching process...[/cyan]")
        # In real hook: subprocess.Popen(...)
        console.print("[green]✓ Parent process exited immediately (Exit Code 0)[/green]")
        console.print(f"[dim]Time elapsed in blocking path: {time.time() - start_time:.4f}s[/dim]")
        
        console.print("[dim]Background: Syncing continues... (simulated 2s delay)[/dim]")
        time.sleep(2) # Simulate background work
        console.print("[dim]Background: Sync complete.[/dim]")
    else:
        console.print("[red]❌ Test failed: Should have detached.[/red]")

def simulate_fail_open():
    console.print(Panel("Scenario 4: Fail-Open Policy", style="bold blue"))
    console.print("Simulating a [bold]CRITICAL CRASH[/bold] during sync.")
    
    try:
        console.print("[yellow]Starting sync...[/yellow]")
        # Simulate work
        time.sleep(0.5)
        # Raise exception
        raise RuntimeError("CRITICAL DATABASE FAILURE: CONNECTION REFUSED")
    except Exception as e:
        console.print(f"[red]⚠ Sync crashed with error: {e}[/red]")
        console.print("[green]✓ Fail-Open active: Swallowing error and allowing commit.[/green]")
        console.print("[bold green]Exit Code: 0 (Success)[/bold green]")

def verify_self_healing():
    console.print(Panel("Scenario 5: Self-Healing Graph", style="bold blue"))
    if not STRESS_DIR.exists():
        console.print("[red]Stress data not found. Run Setup first.[/red]")
        return
    
    # Create an isolated file
    orphan_file = STRESS_DIR / "orphan_node.md"
    orphan_file.write_text("# Orphan Node\nThis node has no incoming or outgoing links.\n")
    console.print(f"[yellow]Created isolated file {orphan_file}[/yellow]")

    # 1. Sync current state
    console.print("[yellow]Syncing current state...[/yellow]")
    try:
        subprocess.run(["coretext", "sync", "--dir", str(STRESS_DIR)], check=True)
    except subprocess.CalledProcessError:
        console.print("[red]❌ Sync failed. The graph contains integrity errors.[/red]")
        console.print("[yellow]Tip: Run '1. Setup' again to generate clean stress data.[/yellow]")
        return
    
    # Verify it exists
    res = subprocess.run(["coretext", "inspect", "orphan_node.md"], capture_output=True, text=True)
    if "No node found" in res.stdout:
        console.print("[red]❌ Setup failed: Orphan node not indexed.[/red]")
        return

    # 2. Delete the file
    console.print(f"[yellow]Deleting {orphan_file.name} from filesystem...[/yellow]")
    orphan_file.unlink()
    
    # 3. Sync again (should heal)
    console.print("[yellow]Syncing again (Healing)...[/yellow]")
    subprocess.run(["coretext", "sync", "--dir", str(STRESS_DIR)], check=True)
    
    # 4. Inspect (should be gone)
    console.print(f"[cyan]Verifying {orphan_file.name} is gone from graph...[/cyan]")
    res = subprocess.run(["coretext", "inspect", "orphan_node.md"], capture_output=True, text=True)
    
    # If node is gone, inspect should probably return nothing or error
    if "Node not found" in res.stdout:
         console.print(f"[green]✓ Node {orphan_file.name} successfully removed from graph.[/green]")
    else:
        # Check stdout/stderr for confirmation
        console.print(f"[red]❌ Node {orphan_file.name} still exists or inspection result unclear![/red]\n{res.stdout}")

def main():
    while True:
        console.print("\n[bold magenta]Epic 4 Demo & Verification[/bold magenta]")
        console.print("1. [bold]Setup[/bold] (Generate Stress Data)")
        console.print("2. [bold]Benchmark Latency[/bold]")
        console.print("3. [bold]Verify Async Hook[/bold] (Simulation)")
        console.print("4. [bold]Verify Fail-Open[/bold] (Simulation)")
        console.print("5. [bold]Verify Self-Healing[/bold]")
        console.print("6. [bold]Cleanup[/bold] (Remove Test Data)")
        console.print("0. [bold]Exit[/bold]")
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "0"], default="0")
        
        if choice == "1":
            setup_data()
        elif choice == "2":
            run_latency_check()
        elif choice == "3":
            simulate_async_hook()
        elif choice == "4":
            simulate_fail_open()
        elif choice == "5":
            verify_self_healing()
        elif choice == "6":
            cleanup_data()
        elif choice == "0":
            console.print("[bold]Demo Complete.[/bold]")
            break
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["setup", "async", "fail-open", "self-healing", "cleanup"], help="Run specific scenario non-interactively")
    args = parser.parse_args()

    if args.scenario == "setup":
        setup_data()
    elif args.scenario == "cleanup":
        cleanup_data()
    elif args.scenario == "async":
        simulate_async_hook()
    elif args.scenario == "fail-open":
        simulate_fail_open()
    elif args.scenario == "self-healing":
        verify_self_healing()
    else:
        main()
