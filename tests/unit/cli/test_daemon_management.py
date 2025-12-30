import pytest
import os
import signal
from unittest.mock import patch, MagicMock, AsyncMock
from typer.testing import CliRunner
from coretext.cli.commands import app
from pathlib import Path

runner = CliRunner()

@pytest.fixture
def mock_project_root(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    dot_coretext = project_root / ".coretext"
    dot_coretext.mkdir()
    return project_root

@patch("coretext.cli.commands.subprocess.Popen")
@patch("coretext.cli.commands.SurrealDBClient")
@patch("coretext.cli.commands._apply_schema_logic", new_callable=AsyncMock)
def test_start_uses_config_ports(mock_apply_schema, mock_surreal_client, mock_popen, mock_project_root):
    # Setup config
    config_path = mock_project_root / ".coretext" / "config.yaml"
    config_path.write_text("daemon_port: 9000\nmcp_port: 9001\n")
    
    # Setup SurrealDBClient mock
    mock_db_instance = mock_surreal_client.return_value
    mock_db_instance.is_running = AsyncMock(return_value=False)
    mock_surreal_path = MagicMock(spec=Path)
    mock_surreal_path.exists.return_value = True
    mock_surreal_path.__str__.return_value = "/mock/bin/surreal"
    mock_db_instance.surreal_path = mock_surreal_path
    mock_db_instance.db_path = mock_project_root / ".coretext" / "surreal.db"
    mock_db_instance.start_detached = MagicMock()
    
    # Mock Popen to return a process with a PID (for FastAPI)
    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_popen.return_value = mock_proc
    
    # Run command
    result = runner.invoke(app, ["start", "--project-root", str(mock_project_root)])
    
    assert result.exit_code == 0
    
    # Verify start_detached call for SurrealDB
    mock_db_instance.start_detached.assert_called_once_with(port=9000)
    
    # Verify Popen call for FastAPI
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    cmd = args[0]
    assert "--port" in cmd
    assert "9001" in cmd

@patch("coretext.cli.commands.os.kill")
@patch("coretext.cli.commands.SurrealDBClient")
def test_stop_cleans_up_pids(mock_surreal_client, mock_kill, mock_project_root):
    # Setup PID files
    daemon_pid_file = mock_project_root / ".coretext" / "daemon.pid"
    daemon_pid_file.write_text("1234")
    server_pid_file = mock_project_root / ".coretext" / "server.pid"
    server_pid_file.write_text("5678")
    
    # Setup SurrealDBClient mock
    mock_db_instance = mock_surreal_client.return_value
    mock_db_instance.stop_surreal_db = AsyncMock()
    
    # Run command
    result = runner.invoke(app, ["stop", "--project-root", str(mock_project_root)])
    
    assert result.exit_code == 0
    
    # Verify os.kill for server
    mock_kill.assert_any_call(5678, signal.SIGTERM)
    
    # Verify stop_surreal_db call
    mock_db_instance.stop_surreal_db.assert_called_once()
    
    # Verify PID files are gone (server_pid is unlinked by stop, daemon_pid is unlinked by stop_surreal_db in SurrealDBClient)
    assert not server_pid_file.exists()