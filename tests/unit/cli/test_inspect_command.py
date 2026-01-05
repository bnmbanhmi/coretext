import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from coretext.cli.main import app

runner = CliRunner()

@pytest.fixture
def mock_config(tmp_path):
    config_dir = tmp_path / ".coretext"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    config_file.write_text("daemon_port: 8000\nmcp_port: 8001\n")
    return tmp_path

def test_inspect_node_not_found():
    """Test inspect command when node is not found (404)."""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        with patch("coretext.cli.commands.load_config") as mock_load:
            mock_load.return_value = MagicMock(mcp_port=8001, daemon_port=8000)
            with patch("coretext.cli.commands.check_daemon_health") as mock_health:
                mock_health.return_value = {"server": {"status": "Running"}}
                with patch("httpx.post") as mock_post:
                    mock_post.return_value = MagicMock(status_code=404)
                    
                    result = runner.invoke(app, ["inspect", "nonexistent.md"])
                    
                    assert result.exit_code == 0
                    assert "Node not found" in result.output

def test_inspect_daemon_stopped():
    """Test inspect command when daemon is stopped."""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        with patch("coretext.cli.commands.load_config") as mock_load:
            mock_load.return_value = MagicMock(mcp_port=8001, daemon_port=8000)
            with patch("coretext.cli.commands.check_daemon_health") as mock_health:
                mock_health.return_value = {"server": {"status": "Stopped"}}
                
                result = runner.invoke(app, ["inspect", "somefile.md"])
                
                assert result.exit_code == 1
                assert "Daemon is not running" in result.output

def test_inspect_success_renders_tree():
    """Test inspect command success case and tree rendering."""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        with patch("coretext.cli.commands.load_config") as mock_load:
            mock_load.return_value = MagicMock(mcp_port=8001, daemon_port=8000)
            with patch("coretext.cli.commands.check_daemon_health") as mock_health:
                mock_health.return_value = {"server": {"status": "Running"}}
                with patch("httpx.post") as mock_post:
                    # Mock API response with some dependencies
                    mock_post.return_value = MagicMock(
                        status_code=200,
                        json=lambda: {
                            "dependencies": [
                                {
                                    "node_id": "file:docs/prd.md",
                                    "from_node_id": "file:README.md",
                                    "relationship_type": "depends_on",
                                    "direction": "outgoing"
                                },
                                {
                                    "node_id": "file:docs/architecture.md",
                                    "from_node_id": "file:README.md",
                                    "relationship_type": "depends_on",
                                    "direction": "outgoing"
                                }
                            ]
                        }
                    )
                    
                    result = runner.invoke(app, ["inspect", "file:README.md"])
                    
                    assert result.exit_code == 0
                    assert "file:README.md" in result.output
                    assert "Depends On" in result.output
                    assert "file:docs/prd.md" in result.output
                    assert "file:docs/architecture.md" in result.output

def test_inspect_no_dependencies():
    """Test inspect command when no dependencies are returned."""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        with patch("coretext.cli.commands.load_config") as mock_load:
            mock_load.return_value = MagicMock(mcp_port=8001, daemon_port=8000)
            with patch("coretext.cli.commands.check_daemon_health") as mock_health:
                mock_health.return_value = {"server": {"status": "Running"}}
                with patch("httpx.post") as mock_post:
                    mock_post.return_value = MagicMock(
                        status_code=200,
                        json=lambda: {"dependencies": []}
                    )
                    
                    result = runner.invoke(app, ["inspect", "isolated.md"])
                    
                    assert result.exit_code == 0
                    assert "No dependencies found" in result.output
