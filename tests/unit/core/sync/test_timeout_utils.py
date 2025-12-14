import pytest
from unittest.mock import patch, MagicMock, AsyncMock, ANY, call
from pathlib import Path
import asyncio
import sys
import subprocess
import signal

from coretext.core.sync.timeout_utils import run_with_timeout_or_detach, FILE_COUNT_DETACH_THRESHOLD, TIMEOUT_SECONDS, _run_sync_operation, TimeoutError


@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.signal.alarm")
@patch("coretext.core.sync.timeout_utils.signal.signal")
async def test_run_sync_operation_completes(mock_signal, mock_alarm):
    async def simple_coro():
        return "Sync Result"

    # We need to simulate the coroutine completing successfully
    result = await _run_sync_operation(simple_coro(), timeout=1)

    # Verify signal was set and then unset
    mock_signal.assert_called_with(signal.SIGALRM, ANY)
    mock_alarm.assert_any_call(1) # Called with timeout
    mock_alarm.assert_called_with(0) # Called with 0 to cancel
    
    assert result == "Sync Result"

@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.signal.alarm")
@patch("coretext.core.sync.timeout_utils.signal.signal")
@patch("builtins.print")
async def test_run_sync_operation_times_out(mock_print, mock_signal, mock_alarm):
    # Simulate a timeout by having the side effect of the coroutine raise TimeoutError
    # Note: In real life, the signal handler raises this, but for unit test mocking we just simulate the raise
    async def raising_coro():
        raise TimeoutError("Operation timed out")

    result = await _run_sync_operation(raising_coro(), timeout=1)

    mock_alarm.assert_any_call(1)
    mock_alarm.assert_called_with(0)
    mock_print.assert_any_call(f"Warning: Sync operation timed out after {1} seconds (Strict Signal).", file=sys.stderr)
    assert result is None

@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.signal.alarm")
@patch("coretext.core.sync.timeout_utils.signal.signal")
@patch("builtins.print")
async def test_run_sync_operation_raises_exception(mock_print, mock_signal, mock_alarm):
    async def raising_coro():
        raise ValueError("Test Error")

    result = await _run_sync_operation(raising_coro(), timeout=1)

    mock_alarm.assert_any_call(1)
    mock_alarm.assert_called_with(0)
    mock_print.assert_any_call(f"Error: Sync operation failed with unexpected error: Test Error", file=sys.stderr)
    assert result is None


@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.subprocess.Popen")
@patch("coretext.core.sync.timeout_utils.sys.executable", "/usr/bin/python") # Mock sys.executable
@patch("builtins.print")
async def test_run_with_timeout_or_detach_detaches(mock_print, mock_popen, tmp_path: Path):
    project_root = tmp_path
    file_paths = ["file1.md"] * (FILE_COUNT_DETACH_THRESHOLD + 1) # Exceed threshold
    mock_sync_coro_factory = AsyncMock() # This won't be called, but needs to be a valid callable

    await run_with_timeout_or_detach(project_root, file_paths, mock_sync_coro_factory)

    mock_print.assert_any_call(f"Processing {len(file_paths)} files, detaching sync operation...")
    expected_cmd_args = [
        "/usr/bin/python",
        "-m",
        "coretext.cli.main",
        "hook",
        "post-commit",
        "--project-root", str(project_root),
        "--detached",
    ]
    mock_popen.assert_called_once_with(
        expected_cmd_args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    mock_print.assert_any_call("Sync operation detached successfully.")
    mock_sync_coro_factory.assert_not_called()

@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.subprocess.Popen")
@patch("coretext.core.sync.timeout_utils._run_sync_operation")
@patch("builtins.print")
async def test_run_with_timeout_or_detach_runs_with_timeout(
    mock_print, mock_run_sync_op, mock_subprocess_popen, tmp_path: Path
):
    project_root = tmp_path
    file_paths = ["file1.md"] * FILE_COUNT_DETACH_THRESHOLD # At or below threshold
    
    # Define a factory that returns an AsyncMock coroutine
    mock_coro_instance = AsyncMock(return_value="Sync Result")
    mock_sync_coro_factory = MagicMock(return_value=mock_coro_instance)

    # Configure the mock _run_sync_operation to simulate returning a coroutine object
    mock_coroutine_returned_by_run_sync_op = AsyncMock(return_value="Operation completed successfully")
    mock_run_sync_op.return_value = "Operation completed successfully" # awaitable return value

    await run_with_timeout_or_detach(project_root, file_paths, mock_sync_coro_factory)

    # UPDATED ASSERTION: Check for "strict timeout"
    mock_print.assert_any_call(f"Processing {len(file_paths)} files, running sync operation with strict timeout...")
    mock_subprocess_popen.assert_not_called()
    mock_sync_coro_factory.assert_called_once() 

    # mock_asyncio_run.assert_called_once()  # No longer called
    mock_run_sync_op.assert_awaited_once_with(mock_coro_instance)


@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.subprocess.Popen")
@patch("builtins.print")
async def test_run_with_timeout_or_detach_detach_fails(mock_print, mock_popen, tmp_path: Path):
    project_root = tmp_path
    file_paths = ["file1.md"] * (FILE_COUNT_DETACH_THRESHOLD + 1) # Exceed threshold
    mock_sync_coro_factory = AsyncMock()

    mock_popen.side_effect = Exception("Popen failed")

    await run_with_timeout_or_detach(project_root, file_paths, mock_sync_coro_factory)

    mock_print.assert_any_call(f"Processing {len(file_paths)} files, detaching sync operation...")
    mock_print.assert_any_call(f"Error: Failed to detach sync operation: Popen failed", file=sys.stderr)
    mock_popen.assert_called_once()
    mock_sync_coro_factory.assert_not_called()