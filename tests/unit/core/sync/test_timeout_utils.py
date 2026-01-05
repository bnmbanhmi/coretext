import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from coretext.core.sync.timeout_utils import run_with_timeout_or_detach
import sys

@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.SyncEngine")
@patch("coretext.core.sync.timeout_utils._run_sync_operation")
@patch("coretext.core.sync.timeout_utils.subprocess.Popen")
async def test_run_with_timeout_or_detach_detach(mock_popen, mock_run_sync, mock_sync_engine, tmp_path: Path):
    # Setup
    files = ["f1.md", "f2.md", "f3.md", "f4.md", "f5.md", "f6.md"]
    mock_sync_engine.should_detach.return_value = True
    
    sync_factory = MagicMock()

    # Execute
    await run_with_timeout_or_detach(tmp_path, files, sync_factory)

    # Assert
    mock_sync_engine.should_detach.assert_called_once_with(6)
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    assert args[0][0] == sys.executable
    assert "--detached" in args[0]
    assert kwargs["start_new_session"] is True
    
    mock_run_sync.assert_not_called()
    sync_factory.assert_not_called()

@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.SyncEngine")
@patch("coretext.core.sync.timeout_utils._run_sync_operation")
@patch("coretext.core.sync.timeout_utils.subprocess.Popen")
async def test_run_with_timeout_or_detach_sync(mock_popen, mock_run_sync, mock_sync_engine, tmp_path: Path):
    # Setup
    files = ["f1.md"]
    mock_sync_engine.should_detach.return_value = False
    
    sync_factory = MagicMock()
    coro = AsyncMock()
    sync_factory.return_value = coro

    # Execute
    await run_with_timeout_or_detach(tmp_path, files, sync_factory)

    # Assert
    mock_sync_engine.should_detach.assert_called_once_with(1)
    mock_popen.assert_not_called()
    
    sync_factory.assert_called_once()
    mock_run_sync.assert_awaited_once_with(coro)

