import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from coretext.cli.commands import app
from pathlib import Path
import os
import signal

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
        # is_running needs to be awaitable? No, existing code calls asyncio.run(db_client.stop_surreal_db())
        # So stop_surreal_db must be async.
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
    # Expect 2 calls to Popen: one for DB, one for FastAPI
    assert mock_subprocess.call_count == 2
    
    # Check FastAPI call (should be the second one usually, or order doesn't matter much but let's check content)
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
         patch("coretext.cli.commands.asyncio.run") as mock_asyncio_run:
        
        result = runner.invoke(app, ["stop", "--project-root", str(tmp_path)])
        
        assert result.exit_code == 0
        
        # Verify os.kill was called for the PID
        mock_kill.assert_called_with(54321, signal.SIGTERM)
        
        # Verify pid file is removed
        assert not server_pid_file.exists()

