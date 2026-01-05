import pytest
from unittest.mock import patch, MagicMock
from coretext.cli.utils import check_daemon_health

MOCK_SERVER_PORT = 8001
MOCK_DB_PORT = 8000

@pytest.fixture
def mock_project_root(tmp_path):
    # Setup directories
    (tmp_path / ".coretext").mkdir()
    return tmp_path

@pytest.mark.asyncio
async def test_check_daemon_health_all_running(mock_project_root):
    """Test health check when both server and DB are running."""
    with patch("httpx.get") as mock_get, \
         patch("coretext.cli.utils.check_process_running", return_value=True):
        
        # Mock responses for both calls
        def side_effect(url, timeout):
            resp = MagicMock()
            resp.status_code = 200
            if "8001" in url: # Server
                resp.json.return_value = {"status": "ok", "version": "0.1.0"}
            return resp
            
        mock_get.side_effect = side_effect
        
        status = check_daemon_health(MOCK_SERVER_PORT, MOCK_DB_PORT, mock_project_root)
        
        assert status["server"]["status"] == "Running"
        assert status["server"]["version"] == "0.1.0"
        assert status["database"]["status"] == "Running"

@pytest.mark.asyncio
async def test_check_daemon_health_server_stopped(mock_project_root):
    """Test when server is stopped (conn refused, no PID)."""
    with patch("httpx.get") as mock_get:
        # Mock connection error for server, success for DB
        def side_effect(url, timeout):
            if "8001" in url:
                raise Exception("Connection refused")
            resp = MagicMock()
            resp.status_code = 200
            return resp
            
        mock_get.side_effect = side_effect
        
        status = check_daemon_health(MOCK_SERVER_PORT, MOCK_DB_PORT, mock_project_root)
        
        assert status["server"]["status"] == "Stopped"
        assert status["database"]["status"] == "Running"

@pytest.mark.asyncio
async def test_check_daemon_health_unresponsive_stale_pid(mock_project_root):
    """Test correctly identifying Unresponsive vs Stale PID."""
    # Create PID file
    pid_file = mock_project_root / ".coretext" / "server.pid"
    pid_file.write_text("12345")
    
    # Case 1: Process exists but HTTP fails -> Unresponsive
    with patch("httpx.get", side_effect=Exception("Timeout")), \
         patch("coretext.cli.utils.check_process_running", return_value=True):
        
        status = check_daemon_health(MOCK_SERVER_PORT, MOCK_DB_PORT, mock_project_root)
        assert status["server"]["status"] == "Unresponsive"
        assert status["server"]["pid"] == 12345

    # Case 2: Process does NOT exist -> Stopped (Stale PID ignored/handled)
    with patch("httpx.get", side_effect=Exception("Conn Refused")), \
         patch("coretext.cli.utils.check_process_running", return_value=False):
        
        status = check_daemon_health(MOCK_SERVER_PORT, MOCK_DB_PORT, mock_project_root)
        assert status["server"]["status"] == "Stopped"
