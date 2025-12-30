import httpx
import os
from pathlib import Path
from typing import Any

from coretext.db.client import SurrealDBClient

def get_pid_file_path(project_root: Path) -> Path:
    """Returns the path to the server PID file."""
    return project_root / ".coretext" / "server.pid"

def get_hooks_paused_path(project_root: Path) -> Path:
    """Returns the path to the hooks_paused file."""
    return project_root / ".coretext" / "hooks_paused"

def check_process_running(pid: int) -> bool:
    """Checks if a process with the given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False

def check_daemon_health(server_port: int, db_port: int, project_root: Path) -> dict[str, Any]:
    """
    Checks the health of both the FastAPI server and SurrealDB daemon.
    """
    server_pid_file = get_pid_file_path(project_root)
    db_client = SurrealDBClient(project_root=project_root)

    status_info = {
        "server": {
            "status": "Stopped",
            "port": server_port,
            "pid": None,
            "version": "Unknown"
        },
        "database": {
            "status": "Stopped",
            "port": db_port,
            "pid": None,
            "version": "Unknown"
        }
    }

    # --- Check FastAPI Server ---
    if server_pid_file.exists():
        try:
            server_pid = int(server_pid_file.read_text().strip())
            status_info["server"]["pid"] = server_pid
        except (ValueError, OSError):
            pass

    try:
        response = httpx.get(f"http://localhost:{server_port}/health", timeout=2.0)
        if response.status_code == 200:
            status_info["server"]["status"] = "Running"
            data = response.json()
            status_info["server"]["version"] = data.get("version", "Unknown")
        else:
             status_info["server"]["status"] = "Unresponsive"
    except Exception:
        # Check if process exists to distinguish Stopped vs Unresponsive
        if status_info["server"]["pid"] and check_process_running(status_info["server"]["pid"]):
            status_info["server"]["status"] = "Unresponsive"
        else:
             status_info["server"]["status"] = "Stopped"

    # --- Check SurrealDB Daemon ---
    # We can check PID from client first
    db_pid = None
    if db_client.pid_file.exists():
        try:
            db_pid = int(db_client.pid_file.read_text().strip())
            status_info["database"]["pid"] = db_pid
        except (ValueError, OSError):
             pass
    
    # We can try to curl the /status endpoint of SurrealDB if it exposes one, 
    # or just check port connectivity / process existence.
    # SurrealDB exposes /status or /health usually? 
    # For now, we rely on process existence + port check logic or client.is_running
    # A better check is actual HTTP ping to surreal.
    
    try:
         # SurrealDB usually exposes a /health or /status. 
         # Or we can just check if port is open. 
         # Let's use the /health endpoint if available, or just fallback to simple port check
         # For 1.x /health is common.
         db_response = httpx.get(f"http://localhost:{db_port}/health", timeout=2.0)
         if db_response.status_code == 200:
             status_info["database"]["status"] = "Running"
             # Extract version if possible, or leave unknown
         else:
             status_info["database"]["status"] = "Unresponsive"
    except Exception:
        if db_pid and check_process_running(db_pid):
             status_info["database"]["status"] = "Unresponsive"
        else:
             status_info["database"]["status"] = "Stopped"

    return status_info