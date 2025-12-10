from asyncio import TimeoutError, wait_for
from pathlib import Path
from typing import List, Callable, Any, Coroutine
import asyncio
import sys
import subprocess
import os

# Define threshold for detachment
FILE_COUNT_DETACH_THRESHOLD = 5
TIMEOUT_SECONDS = 1

async def _run_sync_operation(sync_coro: Coroutine[Any, Any, Any], timeout: float = TIMEOUT_SECONDS) -> Any:
    """Runs an async operation with a timeout."""
    try:
        return await wait_for(sync_coro, timeout=timeout)
    except TimeoutError:
        print(f"Warning: Sync operation timed out after {timeout} seconds.", file=sys.stderr)
        # Fail-open: return a failure result or None
        return None # Indicate failure due to timeout
    except Exception as e:
        print(f"Error: Sync operation failed with unexpected error: {e}", file=sys.stderr)
        return None # Indicate failure due to unexpected error


def run_with_timeout_or_detach(
    project_root: Path,
    file_paths: List[str],
    sync_coro_factory: Callable[[], Coroutine[Any, Any, Any]]
) -> None:
    """
    Executes an async synchronization operation.
    If the number of files is above a threshold, it detaches the operation using subprocess.
    Otherwise, it runs the operation with a strict timeout.
    """
    if len(file_paths) > FILE_COUNT_DETACH_THRESHOLD:
        print(f"Processing {len(file_paths)} files, detaching sync operation...")
        # Detach using subprocess.Popen
        # The subcommand should re-invoke the post-commit hook logic.
        # This requires the post-commit hook to be invokable via CLI args.
        try:
            cmd_args = [
                sys.executable,  # python interpreter
                "-m",
                "coretext.cli.main", # main entry point
                "hook",
                "post-commit",
                "--project-root", str(project_root),
                "--detached", # Signal that this is the detached process
            ]
            
            subprocess.Popen(cmd_args, 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL,
                             start_new_session=True # Detach from current session
                            )
            print("Sync operation detached successfully.")
        except Exception as e:
            print(f"Error: Failed to detach sync operation: {e}", file=sys.stderr)
            # Fail-open: continue, do not block original commit
    else:
        print(f"Processing {len(file_paths)} files, running sync operation with timeout...")
        # Run synchronously with timeout
        # Create a coroutine using the factory
        sync_coro = sync_coro_factory()
        asyncio.run(_run_sync_operation(sync_coro))

