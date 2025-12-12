# tests/unit/cli/test_commands.py

import pytest
from typer.testing import CliRunner
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from coretext.cli.commands import app as commands_app 

runner = CliRunner()

@pytest.fixture
def mock_db_client():
    with patch("coretext.cli.commands.SurrealDBClient", autospec=True) as mock_client_cls:
        mock_client_instance = mock_client_cls.return_value
        # Mocking instance methods
        mock_client_instance.download_surreal_binary = AsyncMock()
        mock_client_instance.db_path = MagicMock()
        mock_client_instance.db_path.parent.mkdir = MagicMock()
        mock_client_instance.surreal_path = Path("/mock/surreal")
        
        # We need db_path to not be a plain MagicMock if we want to use it in f-strings or logic sometimes,
        # but here it's used for .parent.mkdir which is fine.
        
        yield mock_client_instance

def test_init_command_success_new_schema_map(tmp_path: Path, mock_db_client: AsyncMock):
    # Ensure no schema_map exists
    # tmp_path is a new directory
    
    result = runner.invoke(commands_app, ["init", "--project-root", str(tmp_path)], input="n\n")
    
    if result.exit_code != 0:
        print(result.stdout)
        print(result.exception)

    assert result.exit_code == 0
    assert "Initializing CoreText project..." in result.stdout
    assert "Creating default schema_map.yaml" in result.stdout
    assert "Default schema_map.yaml created." in result.stdout

    mock_db_client.download_surreal_binary.assert_awaited_once_with(version="1.4.1")
    mock_db_client.db_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # Verify file was created on real filesystem (tmp_path)
    schema_map_path = tmp_path / ".coretext" / "schema_map.yaml"
    assert schema_map_path.exists()
    assert "node_types" in schema_map_path.read_text()

def test_init_command_success_existing_schema_map(tmp_path: Path, mock_db_client: AsyncMock):
    # Create a dummy existing schema_map.yaml
    (tmp_path / ".coretext").mkdir()
    (tmp_path / ".coretext" / "schema_map.yaml").write_text("existing content")

    result = runner.invoke(commands_app, ["init", "--project-root", str(tmp_path)], input="n\n")
    
    if result.exit_code != 0:
        print(result.stdout)
        print(result.exception)

    assert result.exit_code == 0
    assert "schema_map.yaml already exists. Skipping creation." in result.stdout
    
    mock_db_client.download_surreal_binary.assert_awaited_once_with(version="1.4.1")
    
    # Verify content was NOT changed
    schema_map_path = tmp_path / ".coretext" / "schema_map.yaml"
    assert schema_map_path.read_text() == "existing content"