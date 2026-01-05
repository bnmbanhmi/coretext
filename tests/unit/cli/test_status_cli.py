import pytest
from typer.testing import CliRunner
from coretext.cli.main import app
from unittest.mock import patch

runner = CliRunner()

@pytest.fixture
def mock_project_root(tmp_path):
    # Setup .coretext/config.yaml
    coretext_dir = tmp_path / ".coretext"
    coretext_dir.mkdir()
    config_file = coretext_dir / "config.yaml"
    config_file.write_text("daemon_port: 8000\nmcp_port: 8001\n")
    return tmp_path

def test_status_command_split_status(mock_project_root):
    """Test that status command correctly displays split status for Server and DB."""
    with patch("coretext.cli.commands.check_daemon_health") as mock_health:
        mock_health.return_value = {
            "server": {
                "status": "Running",
                "port": 8001,
                "pid": 111,
                "version": "0.1.0"
            },
            "database": {
                "status": "Running", 
                "port": 8000,
                "pid": 222,
                "version": "Unknown"
            }
        }
        
        result = runner.invoke(app, ["status", "--project-root", str(mock_project_root)])
        
        assert result.exit_code == 0
        # Check output contains both sections
        assert "Server Status:" in result.stdout
        assert "Database Status:" in result.stdout
        assert "Running" in result.stdout
        assert "111" in result.stdout
        assert "222" in result.stdout

def test_status_command_partial_failure(mock_project_root):
    """Test status output when one component is down."""
    with patch("coretext.cli.commands.check_daemon_health") as mock_health:
        mock_health.return_value = {
            "server": {
                "status": "Stopped",
                "port": 8001,
                "pid": None,
                "version": "Unknown"
            },
            "database": {
                "status": "Running", 
                "port": 8000,
                "pid": 222,
                "version": "Unknown"
            }
        }
        
        result = runner.invoke(app, ["status", "--project-root", str(mock_project_root)])
        
        assert result.exit_code == 0
        assert "Server Status:" in result.stdout
        assert "Stopped" in result.stdout
        assert "Database Status:" in result.stdout
        assert "Running" in result.stdout