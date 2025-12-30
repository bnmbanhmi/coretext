import pytest
from unittest.mock import patch, MagicMock
from coretext.cli.utils import check_daemon_health
from pathlib import Path

# Mock config values
MOCK_PORT = 8000

@pytest.fixture
def mock_project_root(tmp_path):
    return tmp_path

@pytest.mark.asyncio
async def test_check_daemon_health_running(mock_project_root):
    """Test health check when daemon is running normally."""
    with patch("httpx.get") as mock_get:
        # Mock successful health response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "version": "0.1.0"}
        mock_get.return_value = mock_response
        
        status = check_daemon_health(port=MOCK_PORT, project_root=mock_project_root)
        
        assert status["status"] == "Running"
        assert status["port"] == MOCK_PORT
        assert status["version"] == "0.1.0"

@pytest.mark.asyncio
async def test_check_daemon_health_stopped_no_connection(mock_project_root):
    """Test health check when connection is refused (Daemon Stopped)."""
    with patch("httpx.get") as mock_get:
        # Mock connection error
        mock_get.side_effect = Exception("Connection refused")
        
        status = check_daemon_health(port=MOCK_PORT, project_root=mock_project_root)
        
        assert status["status"] == "Stopped"

@pytest.mark.asyncio
async def test_check_daemon_health_unresponsive(mock_project_root):
    """Test when PID file exists but connection fails (Unresponsive)."""
    # Create a dummy PID file
    pid_dir = mock_project_root / ".coretext"
    pid_dir.mkdir()
    pid_file = pid_dir / "server.pid"
    pid_file.write_text("12345")
    
    with patch("httpx.get") as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        
        status = check_daemon_health(port=MOCK_PORT, project_root=mock_project_root)
        
        assert status["status"] == "Unresponsive"
        assert status["pid"] == 12345