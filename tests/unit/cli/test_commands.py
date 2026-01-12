# tests/unit/cli/test_commands.py

import pytest
from typer.testing import CliRunner
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
from pathlib import Path
from coretext.cli.commands import app as commands_app 

runner = CliRunner()

@pytest.fixture
def mock_db_client():
    with patch("coretext.cli.commands.SurrealDBClient", autospec=True) as mock_client_cls:
        mock_client_instance = mock_client_cls.return_value
        
        # Mock async methods
        mock_client_instance.download_surreal_binary = AsyncMock()
        mock_client_instance.is_running = AsyncMock(return_value=False)
        mock_client_instance.start_detached = MagicMock()
        
        # Mock db_path and its parent directory creation
        mock_db_path = MagicMock(spec=Path)
        mock_db_path.parent = MagicMock(spec=Path)
        mock_db_path.parent.mkdir = MagicMock()
        type(mock_client_instance).db_path = PropertyMock(return_value=mock_db_path)
        
        # Mock surreal_path to return a valid-looking path that "exists"
        mock_surreal_path = MagicMock(spec=Path)
        mock_surreal_path.exists.return_value = True
        mock_surreal_path.__str__.return_value = "/mock/surreal/path"
        type(mock_client_instance).surreal_path = PropertyMock(return_value=mock_surreal_path)
        
        yield mock_client_instance

def test_init_command_success_new_schema_map(tmp_path: Path, mock_db_client: AsyncMock):
    # Inputs:
    # 1. "n" -> Docs location (default used later in logic but we say 'no' to custom path or just accept default?)
    #    Actually the prompt is "Where are your documents located? ... [.]". Input "n" means we typed "n".
    #    The next prompt "Directory 'n' does not exist. Create it? [y/N]" -> we send "n".
    # 2. "n" -> "Do you want to start the coretext daemon now? [Y/n]" -> we send "n".
    #
    # Wait, the previous failing test used "n\nn\nn\n". Let's map them exactly to the code:
    # 1. "Where are your documents located?": "n" (User types 'n')
    # 2. "Directory 'n' does not exist. Create it?": "n" (User types 'n')
    # 3. "Do you want to start the coretext daemon now?": "n" (User types 'n')
    # That is 3 'n's. The 4th 'n' in previous fix might have been extra or for safety.
    # Let's use a clear sequence.
    
    # Input sequence: 
    # 1. docs_dir: "." (default, we press Enter? No, Typer prompt needs input or empty string for default?)
    #    Typer prompt with default: sending "\n" accepts default.
    #    Let's try to be explicit: "docs\n" (docs dir), "y\n" (create it), "n\n" (don't start daemon).
    
    # But to match previous logic that was passing with "n\nn\nn\n":
    # It seems it was: "n" (dir name), "n" (don't create), "n" (don't start).
    
    input_seq = "n\nn\nn\n" # kept for consistency with proven passing state
    
    result = runner.invoke(commands_app, ["init", "--project-root", str(tmp_path)], input=input_seq)
    
    if result.exit_code != 0:
        print(result.stdout)
        print(result.exception)

    assert result.exit_code == 0
    assert "Initializing CoreText project..." in result.stdout
    assert "Creating default schema_map.yaml" in result.stdout
    assert "Default schema_map.yaml created." in result.stdout

    mock_db_client.download_surreal_binary.assert_awaited_once_with(version="2.0.4")
    mock_db_client.db_path.parent.mkdir.assert_called_with(parents=True, exist_ok=True)
    
    # Verify file was created on real filesystem (tmp_path)
    schema_map_path = tmp_path / ".coretext" / "schema_map.yaml"
    assert schema_map_path.exists()
    assert "node_types" in schema_map_path.read_text()

def test_init_command_success_existing_schema_map(tmp_path: Path, mock_db_client: AsyncMock):
    # Create a dummy existing schema_map.yaml
    (tmp_path / ".coretext").mkdir()
    (tmp_path / ".coretext" / "schema_map.yaml").write_text("existing content")

    input_seq = "n\nn\nn\n"
    result = runner.invoke(commands_app, ["init", "--project-root", str(tmp_path)], input=input_seq)
    
    if result.exit_code != 0:
        print(result.stdout)
        print(result.exception)

    assert result.exit_code == 0
    assert "schema_map.yaml already exists. Skipping creation." in result.stdout
    
    mock_db_client.download_surreal_binary.assert_awaited_once_with(version="2.0.4")
    
    # Verify content was NOT changed
    schema_map_path = tmp_path / ".coretext" / "schema_map.yaml"
    assert schema_map_path.read_text() == "existing content"

def test_init_command_with_daemon_start(tmp_path: Path, mock_db_client: AsyncMock):
    """Test 'init' command when user chooses to start the daemon."""
    
    # We also need to mock commands.start to avoid actually starting subprocesses/servers
    # The 'init' command calls 'start()' function directly.
    # We can patch 'coretext.cli.commands.start'
    
    with patch("coretext.cli.commands.start") as mock_start_cmd:
        # Input: "n" (dir), "n" (don't create), "y" (Start daemon!)
        input_seq = "n\nn\ny\n"
        
        result = runner.invoke(commands_app, ["init", "--project-root", str(tmp_path)], input=input_seq)
        
        assert result.exit_code == 0
        assert "CoreText project initialized successfully." in result.stdout
        
        # Verify start was called
        mock_start_cmd.assert_called_once()