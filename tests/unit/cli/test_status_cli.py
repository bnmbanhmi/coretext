import pytest
from typer.testing import CliRunner
from coretext.cli.main import app
from unittest.mock import patch
from pathlib import Path

runner = CliRunner()

@pytest.fixture
def mock_project_root(tmp_path):
    # Setup .coretext/config.yaml
    coretext_dir = tmp_path / ".coretext"
    coretext_dir.mkdir()
    config_file = coretext_dir / "config.yaml"
    config_file.write_text("daemon_port: 8000\nmcp_port: 8001\n")
    return tmp_path

def test_status_command_running(mock_project_root):
    with patch("coretext.cli.commands.check_daemon_health") as mock_health:
        mock_health.return_value = {
            "status": "Running",
            "port": 8001,
            "pid": 1234,
            "version": "0.1.0"
        }
        
        # We need to pass the project-root to the command
        result = runner.invoke(app, ["status", "--project-root", str(mock_project_root)])
        
        assert result.exit_code == 0
        assert "Running" in result.stdout
        assert "1234" in result.stdout
        assert "8001" in result.stdout
        assert "0.1.0" in result.stdout
        assert "Active" in result.stdout

def test_status_command_stopped(mock_project_root):
    with patch("coretext.cli.commands.check_daemon_health") as mock_health:
        mock_health.return_value = {
            "status": "Stopped",
            "port": 8001,
            "pid": None,
            "version": "Unknown"
        }
        
        result = runner.invoke(app, ["status", "--project-root", str(mock_project_root)])
        
        assert result.exit_code == 0
        assert "Stopped" in result.stdout
        assert "N/A" in result.stdout

def test_status_command_paused(mock_project_root):
    # Pause hooks
    pause_file = mock_project_root / ".coretext" / "hooks_paused"
    pause_file.touch()
    
    with patch("coretext.cli.commands.check_daemon_health") as mock_health:
        mock_health.return_value = {
            "status": "Running",
            "port": 8001,
            "pid": 1234,
            "version": "0.1.0"
        }
        
        result = runner.invoke(app, ["status", "--project-root", str(mock_project_root)])
        
        assert result.exit_code == 0
        assert "Paused" in result.stdout

def test_status_command_not_initialized(tmp_path):
    # No .coretext dir
    result = runner.invoke(app, ["status", "--project-root", str(tmp_path)])
    
    assert result.exit_code == 1
    assert "Coretext not initialized" in result.stdout
