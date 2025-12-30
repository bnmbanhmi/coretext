import pytest
from typer.testing import CliRunner
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from coretext.cli.commands import app

runner = CliRunner()

@pytest.fixture
def mock_db_client_new():
    with patch("coretext.cli.commands.SurrealDBClient", autospec=True) as mock_client_cls:
        mock_client_instance = mock_client_cls.return_value
        mock_client_instance.download_surreal_binary = AsyncMock()
        mock_client_instance.start_surreal_db = AsyncMock()
        mock_client_instance.is_running = AsyncMock(return_value=True) # Mock is_running
        mock_client_instance.db_path = MagicMock()
        mock_client_instance.db_path.parent.mkdir = MagicMock()
        mock_client_instance.start_detached = MagicMock()
        
        # Mock surreal_path to pass exists() check and look like a path string
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.__str__.return_value = "/mock/surreal"
        mock_client_instance.surreal_path = mock_path
        
        yield mock_client_instance

@pytest.fixture
def mock_async_surreal():
    with patch("coretext.cli.commands.AsyncSurreal") as mock_cls:
        mock_instance = mock_cls.return_value
        # Setup async context manager
        mock_instance.__aenter__.return_value = AsyncMock()
        mock_instance.__aexit__.return_value = None
        yield mock_cls

@pytest.fixture
def mock_sleep():
    with patch("coretext.cli.commands.asyncio.sleep", new_callable=AsyncMock) as mock:
        yield mock

@patch("coretext.cli.commands.subprocess.Popen")
def test_start_command(mock_popen, mock_db_client_new, mock_async_surreal, mock_sleep):
    # Verify 'start' command exists and runs
    result = runner.invoke(app, ["start"])
    
    assert result.exit_code == 0
    # Adjusting assertion to check for something that IS in the output
    assert "SurrealDB is already running" in result.stdout
    # mock_popen might not be called if server is already running, 
    # but in test we don't mock server_running=True unless we mock check_pid_running
    # By default mock_popen IS called for FastAPI
    assert mock_popen.called

def test_init_prompts_start_no(tmp_path, mock_db_client_new):
    # Verify 'init' prompts and handles 'n'
    result = runner.invoke(app, ["init", "--project-root", str(tmp_path)], input="n\n")
    
    assert result.exit_code == 0
    
    assert "Do you want to start the coretext daemon now?" in result.stdout

@patch("coretext.cli.commands.subprocess.Popen")
def test_init_prompts_start_yes(mock_popen, tmp_path, mock_db_client_new, mock_async_surreal, mock_sleep):
    # Verify 'init' handles 'Y' and triggers start
    result = runner.invoke(app, ["init", "--project-root", str(tmp_path)], input="Y\n")
    
    assert result.exit_code == 0
    
    # Init calls start() which prints "SurrealDB is already running." (because of mock)
    assert "SurrealDB is already running" in result.stdout
    assert mock_popen.called