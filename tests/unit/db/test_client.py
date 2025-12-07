# tests/unit/db/test_client.py
import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from coretext.db.client import SurrealDBClient

@pytest.fixture
def mock_project_root(tmp_path):
    # Create a dummy .coretext directory within the temporary project root
    (tmp_path / ".coretext").mkdir()
    return tmp_path

@pytest.fixture
def mock_surreal_client(mock_project_root):
    with patch("pathlib.Path.home", return_value=mock_project_root):
        client = SurrealDBClient(project_root=mock_project_root)
        yield client

@pytest.mark.asyncio
async def test_download_surreal_binary_success(mock_surreal_client):
    client = mock_surreal_client
    
    # Ensure the bin directory exists for the home path mock
    client.bin_dir.mkdir(parents=True, exist_ok=True)

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read.return_value = b"mock surreal binary content"

    # session.get() returns a context manager, not a coroutine directly
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_context.__aexit__.return_value = None
    
    mock_get = MagicMock(return_value=mock_context)

    with patch("aiohttp.ClientSession.get", new=mock_get):
        # Patch chmod to prevent actual permission changes during test
        with patch("os.chmod") as mock_chmod:
            await client.download_surreal_binary(version="1.4.1")

            expected_url = (
                "https://github.com/surrealdb/surrealdb/releases/download/v1.4.1/"
                f"{client._get_surreal_binary_name()}"
            )
            # Verify get was called with correct URL
            mock_get.assert_called_once_with(expected_url)

            # Assert binary file exists and has content
            assert client.surreal_path.exists()
            assert client.surreal_path.read_bytes() == b"mock surreal binary content"
            mock_chmod.assert_called_once_with(client.surreal_path, 0o755)

@pytest.mark.asyncio
async def test_download_surreal_binary_already_exists(mock_surreal_client):
    client = mock_surreal_client
    
    client.bin_dir.mkdir(parents=True, exist_ok=True)
    client.surreal_path.write_text("existing content")

    mock_get = MagicMock()
    with patch("aiohttp.ClientSession.get", new=mock_get):
        await client.download_surreal_binary(version="1.4.1")
        mock_get.assert_not_called()
    
    assert client.surreal_path.read_text() == "existing content"

@pytest.mark.asyncio
async def test_download_surreal_binary_failure(mock_surreal_client):
    client = mock_surreal_client
    
    client.bin_dir.mkdir(parents=True, exist_ok=True)

    mock_response = AsyncMock()
    mock_response.status = 404

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_context.__aexit__.return_value = None

    mock_get = MagicMock(return_value=mock_context)

    with patch("aiohttp.ClientSession.get", new=mock_get):
        with pytest.raises(RuntimeError, match="Failed to download SurrealDB binary"):
            await client.download_surreal_binary(version="1.4.1")
        
        assert not client.surreal_path.exists()

@pytest.mark.asyncio
async def test_start_surreal_db_success(mock_surreal_client):
    client = mock_surreal_client
    client.bin_dir.mkdir(parents=True, exist_ok=True)
    client.surreal_path.touch() # binary must exist

    mock_proc = AsyncMock()
    mock_proc.returncode = None

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
        await client.start_surreal_db()
        
        expected_args = [
            str(client.surreal_path),
            "start",
            "--log", "trace",
            "--user", "root",
            "--pass", "root",
            f"file:{client.db_path}"
        ]
        mock_exec.assert_awaited_once()
        call_args = mock_exec.await_args
        assert call_args.args[0] == str(client.surreal_path)
        # We can check other args, but exact match of args list is good
        # Note: call_args.args will be tuple of positional args.
        # The first arg is program, rest are arguments.
        # asyncio.create_subprocess_exec(program, *args, ...)
        
        assert call_args.args[0] == str(client.surreal_path)
        assert call_args.args[1:] == tuple(expected_args[1:])
        
        assert client.process == mock_proc

@pytest.mark.asyncio
async def test_start_surreal_db_binary_missing(mock_surreal_client):
    client = mock_surreal_client
    # binary does not exist
    
    with pytest.raises(RuntimeError, match="SurrealDB binary not found"):
        await client.start_surreal_db()

@pytest.mark.asyncio
async def test_start_surreal_db_already_running(mock_surreal_client):
    client = mock_surreal_client
    client.bin_dir.mkdir(parents=True, exist_ok=True)
    client.surreal_path.touch()
    client.process = AsyncMock()
    client.process.returncode = None # Still running

    with patch("asyncio.create_subprocess_exec") as mock_exec:
        await client.start_surreal_db()
        mock_exec.assert_not_called()

@pytest.mark.asyncio
async def test_stop_surreal_db(mock_surreal_client):
    client = mock_surreal_client
    mock_proc = AsyncMock()
    mock_proc.returncode = None
    mock_proc.terminate = MagicMock() # terminate is synchronous
    client.process = mock_proc

    await client.stop_surreal_db()
    
    mock_proc.terminate.assert_called_once()
    mock_proc.wait.assert_awaited_once()
    assert client.process is None

@pytest.mark.asyncio
async def test_stop_surreal_db_not_running(mock_surreal_client):
    client = mock_surreal_client
    client.process = None

    # Should not raise error
    await client.stop_surreal_db()
