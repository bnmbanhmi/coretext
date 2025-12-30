import httpx
import os
from pathlib import Path
from typing import Any

def get_pid_file_path(project_root: Path) -> Path:
    """Returns the path to the server PID file."""
    return project_root / ".coretext" / "server.pid"

def get_hooks_paused_path(project_root: Path) -> Path:
    """Returns the path to the hooks_paused file."""
    return project_root / ".coretext" / "hooks_paused"

def check_daemon_health(port: int, project_root: Path | None = None) -> dict[str, Any]:
    """
    Checks the health of the daemon by pinging the /health endpoint.
    Cross-references with PID file if project_root is provided.
    """
    status_info = {
        "status": "Stopped",
        "port": port,
        "pid": None,
        "version": "Unknown"
    }
    
    pid_file = None
    if project_root:
        pid_file = get_pid_file_path(project_root)
        if pid_file.exists():
            try:
                status_info["pid"] = int(pid_file.read_text().strip())
            except (ValueError, OSError):
                pass

    try:
        # Pinging the FastAPI health endpoint (usually on mcp_port)
        # Note: Story says "daemon's /health endpoint (default http://localhost:8000/health)"
        # But in Story 3.1 implementation, daemon_port is 8000 (SurrealDB) 
        # and mcp_port is 8001 (FastAPI).
        # Usually /health is on the FastAPI server. 
        # AC 1 says default 8000, let's follow the provided port.
        response = httpx.get(f"http://localhost:{port}/health", timeout=2.0)
        if response.status_code == 200:
            status_info["status"] = "Running"
            data = response.json()
            status_info["version"] = data.get("version", "Unknown")
        else:
            status_info["status"] = "Unresponsive"
    except Exception:
        if status_info["pid"] is not None:
            status_info["status"] = "Unresponsive"
        else:
            status_info["status"] = "Stopped"
        
    return status_info
