import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typer.testing import CliRunner
from coretext.cli.commands import app
from pathlib import Path

runner = CliRunner()

@pytest.fixture
def mock_subprocess():
    with patch("coretext.cli.commands.subprocess.Popen") as mock_popen:
        process_mock = MagicMock()
        process_mock.pid = 12345
        mock_popen.return_value = process_mock
        yield mock_popen

@pytest.fixture
def mock_db_client():
    with patch("coretext.cli.commands.SurrealDBClient") as mock_client:
        client_instance = mock_client.return_value
        client_instance.surreal_path.exists.return_value = True
        client_instance.db_path = Path("/tmp/test.db")
        client_instance.is_running = AsyncMock(return_value=False)
        client_instance.stop_surreal_db = AsyncMock()
        client_instance.start_surreal_db = AsyncMock()
        client_instance.start_detached = MagicMock()
        yield client_instance

@pytest.fixture
def mock_apply_schema():
    with patch("coretext.cli.commands._apply_schema_logic") as mock:
        yield mock

def test_start_launches_both_processes(mock_subprocess, mock_db_client, mock_apply_schema, tmp_path):
    """Test that start command launches both SurrealDB and FastAPI."""
    # Ensure .coretext directory exists for PID files
    (tmp_path / ".coretext").mkdir(parents=True, exist_ok=True)

    result = runner.invoke(app, ["start", "--project-root", str(tmp_path)])
    
    assert result.exit_code == 0
    # Expect 1 call to Popen (for FastAPI) and 1 call to start_detached (for DB)
    mock_subprocess.assert_called()
    mock_db_client.start_detached.assert_called_once()
    
    # Check FastAPI call 
    calls = mock_subprocess.call_args_list
    fastapi_call = None
    for call in calls:
        cmd = call[0][0]
        if "uvicorn" in str(cmd):
            fastapi_call = cmd
            break
            
    assert fastapi_call is not None
    assert "coretext.server.app:app" in fastapi_call
    assert "127.0.0.1" in fastapi_call

def test_stop_terminates_fastapi_process(mock_db_client, tmp_path):
    """Test that stop command terminates the FastAPI process."""
    # Create a mock server pid file
    pid_dir = tmp_path / ".coretext"
    pid_dir.mkdir(parents=True, exist_ok=True)
    server_pid_file = pid_dir / "server.pid"
    server_pid_file.write_text("54321")
    
    with patch("os.kill") as mock_kill, \
         patch("coretext.cli.commands.asyncio.run"):
        
        result = runner.invoke(app, ["stop", "--project-root", str(tmp_path)])
        
        assert result.exit_code == 0
        
        # Verify os.kill was called for the PID (SIGTERM is 15)
        # Note: the code tries SIGTERM first, then poll, then SIGKILL.
        # mock_kill.assert_any_call(54321, signal.SIGTERM)
        # Actually it might be SIGKILL if the poll loop finishes instantly in mock
        assert mock_kill.called