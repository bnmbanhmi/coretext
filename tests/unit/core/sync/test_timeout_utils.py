import pytest
from unittest.mock import patch, MagicMock, AsyncMock, ANY, call
from pathlib import Path
import asyncio
import sys
import subprocess # Added import

# Patching these at the module level for timeout_utils.py
from coretext.core.sync.timeout_utils import run_with_timeout_or_detach, FILE_COUNT_DETACH_THRESHOLD, TIMEOUT_SECONDS, _run_sync_operation


@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.wait_for")
async def test_run_sync_operation_completes(mock_wait_for):
    mock_coro = AsyncMock(return_value="Sync Result")
    mock_wait_for.return_value = "Sync Result"

    result = await _run_sync_operation(mock_coro, timeout=1)

    mock_wait_for.assert_awaited_once_with(mock_coro, timeout=1)
    assert result == "Sync Result"

@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.wait_for")
@patch("builtins.print") # Patch print to capture output
async def test_run_sync_operation_times_out(mock_print, mock_wait_for):
    mock_coro = AsyncMock()
    mock_wait_for.side_effect = asyncio.TimeoutError

    result = await _run_sync_operation(mock_coro, timeout=1)

    mock_wait_for.assert_awaited_once_with(mock_coro, timeout=1)
    mock_print.assert_any_call(f"Warning: Sync operation timed out after {1} seconds.", file=sys.stderr)
    assert result is None

@pytest.mark.asyncio
@patch("coretext.core.sync.timeout_utils.wait_for")
@patch("builtins.print") # Patch print to capture output
async def test_run_sync_operation_raises_exception(mock_print, mock_wait_for):
    mock_coro = AsyncMock()
    mock_wait_for.side_effect = ValueError("Test Error")

    result = await _run_sync_operation(mock_coro, timeout=1)

    mock_wait_for.assert_awaited_once_with(mock_coro, timeout=1)
    mock_print.assert_any_call(f"Error: Sync operation failed with unexpected error: Test Error", file=sys.stderr)
    assert result is None


@patch("coretext.core.sync.timeout_utils.subprocess.Popen")
@patch("coretext.core.sync.timeout_utils.sys.executable", "/usr/bin/python") # Mock sys.executable
@patch("builtins.print")
def test_run_with_timeout_or_detach_detaches(mock_print, mock_popen, tmp_path: Path):
    project_root = tmp_path
    file_paths = ["file1.md"] * (FILE_COUNT_DETACH_THRESHOLD + 1) # Exceed threshold
    mock_sync_coro_factory = AsyncMock() # This won't be called, but needs to be a valid callable

    run_with_timeout_or_detach(project_root, file_paths, mock_sync_coro_factory)

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
@patch("coretext.core.sync.timeout_utils.subprocess.Popen") # 4th patch
@patch("coretext.core.sync.timeout_utils.asyncio.run") # 3rd patch
@patch("coretext.core.sync.timeout_utils._run_sync_operation") # 2nd patch
@patch("builtins.print") # 1st patch
async def test_run_with_timeout_or_detach_runs_with_timeout(
    mock_print, mock_run_sync_op, mock_asyncio_run, mock_subprocess_popen, tmp_path: Path # Reordered args
):
    project_root = tmp_path
    file_paths = ["file1.md"] * FILE_COUNT_DETACH_THRESHOLD # At or below threshold
    
    # Define a factory that returns an AsyncMock coroutine
    mock_coro_instance = AsyncMock(return_value="Sync Result")
    mock_sync_coro_factory = MagicMock(return_value=mock_coro_instance)

    # Configure the mock _run_sync_operation to simulate returning a coroutine object
    mock_coroutine_returned_by_run_sync_op = AsyncMock(return_value="Operation completed successfully")
    mock_run_sync_op.return_value = mock_coroutine_returned_by_run_sync_op

    run_with_timeout_or_detach(project_root, file_paths, mock_sync_coro_factory)

    mock_print.assert_any_call(f"Processing {len(file_paths)} files, running sync operation with timeout...")
    mock_subprocess_popen.assert_not_called()
    mock_sync_coro_factory.assert_called_once() # Factory should be called once to get the coroutine

    mock_asyncio_run.assert_called_once() # Just check that asyncio.run was called once
    mock_run_sync_op.assert_called_once_with(mock_coro_instance) # Check that _run_sync_operation was called with the coroutine


@patch("coretext.core.sync.timeout_utils.subprocess.Popen")
@patch("builtins.print")
def test_run_with_timeout_or_detach_detach_fails(mock_print, mock_popen, tmp_path: Path):
    project_root = tmp_path
    file_paths = ["file1.md"] * (FILE_COUNT_DETACH_THRESHOLD + 1) # Exceed threshold
    mock_sync_coro_factory = AsyncMock()

    mock_popen.side_effect = Exception("Popen failed")

    run_with_timeout_or_detach(project_root, file_paths, mock_sync_coro_factory)

    mock_print.assert_any_call(f"Processing {len(file_paths)} files, detaching sync operation...")
    mock_print.assert_any_call(f"Error: Failed to detach sync operation: Popen failed", file=sys.stderr)
    mock_popen.assert_called_once()
    mock_sync_coro_factory.assert_not_called()