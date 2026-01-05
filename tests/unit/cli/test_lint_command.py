from typer.testing import CliRunner
from coretext.cli.main import app
from unittest.mock import patch

runner = CliRunner()

def test_lint_cli_no_issues(tmp_path):
    # Mock config file existence
    config_dir = tmp_path / ".coretext"
    config_dir.mkdir()
    (config_dir / "config.yaml").touch()
    
    with patch("coretext.cli.commands.check_daemon_health") as mock_health, \
         patch("coretext.cli.commands.httpx.post") as mock_post, \
         patch("coretext.cli.commands.load_config") as mock_config:
         
        mock_health.return_value = {"server": {"status": "Running"}}
        mock_config.return_value.mcp_port = 8000
        mock_config.return_value.daemon_port = 8001
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"issues": []}
        
        result = runner.invoke(app, ["lint", "--project-root", str(tmp_path)])
        assert result.exit_code == 0
        assert "No issues found" in result.stdout

def test_lint_cli_with_issues(tmp_path):
    # Mock config file existence
    config_dir = tmp_path / ".coretext"
    config_dir.mkdir()
    (config_dir / "config.yaml").touch()

    with patch("coretext.cli.commands.check_daemon_health") as mock_health, \
         patch("coretext.cli.commands.httpx.post") as mock_post, \
         patch("coretext.cli.commands.load_config") as mock_config:
         
        mock_health.return_value = {"server": {"status": "Running"}}
        mock_config.return_value.mcp_port = 8000
        mock_config.return_value.daemon_port = 8001
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"issues": [
            {"file_path": "bad.md", "line_number": 1, "error_type": "Error", "message": "Bad"}
        ]}
        
        result = runner.invoke(app, ["lint", "--project-root", str(tmp_path)])
        assert result.exit_code == 1
        assert "Lint Issues Found" in result.stdout
        assert "bad.md" in result.stdout

