import pytest
from unittest.mock import patch, AsyncMock
from typer.testing import CliRunner
from coretext.cli.commands import app

runner = CliRunner()

@pytest.fixture
def mock_home_dir(tmp_path):
    # Mock Path.home() to return a temporary directory
    with patch("pathlib.Path.home", return_value=tmp_path):
        yield tmp_path

@patch("coretext.cli.commands.SentenceTransformer")
@patch("coretext.cli.commands.SurrealDBClient")
def test_init_downloads_model_and_creates_config(mock_surreal_client, mock_sentence_transformer, mock_home_dir):
    # Setup mocks
    mock_db_instance = mock_surreal_client.return_value
    mock_db_instance.db_path = mock_home_dir / "project" / ".coretext" / "surreal.db"
    mock_db_instance.surreal_path = mock_home_dir / ".coretext" / "bin" / "surreal"
    # Use AsyncMock for async methods
    mock_db_instance.download_surreal_binary = AsyncMock()
    
    # Create a project root
    project_root = mock_home_dir / "project"
    project_root.mkdir()
    
    # Run command
    # We pass project_root. Input "n" for "Do you want to start the daemon?"
    result = runner.invoke(app, ["init", "--project-root", str(project_root)], input="n\n")
    
    # Assertions
    if result.exit_code != 0:
        print(result.stdout)
    assert result.exit_code == 0
    
    # Verify Model Download
    # This expects SentenceTransformer to be imported in coretext.cli.commands
    mock_sentence_transformer.assert_called_with(
        "nomic-ai/nomic-embed-text-v1.5", 
        trust_remote_code=True, 
        cache_folder=str(mock_home_dir / ".coretext" / "cache")
    )
    
    # Verify Config Creation
    config_path = project_root / ".coretext" / "config.yaml"
    assert config_path.exists()
    content = config_path.read_text()
    assert "daemon_port: 8000" in content
    assert "mcp_port: 8001" in content

    # Verify Output
    assert "Downloading and caching embedding model" in result.stdout
    assert "Creating default configuration" in result.stdout
