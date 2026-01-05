import signal
import sys
import subprocess
from pathlib import Path
from typing import List, Callable, Any, Coroutine
from coretext.core.sync.engine import SyncEngine

TIMEOUT_SECONDS = 2  # Updated to match AC (2s)

class TimeoutError(Exception):
    pass

def _timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

async def _run_sync_operation(sync_coro: Coroutine[Any, Any, Any], timeout: float = TIMEOUT_SECONDS) -> Any:
    """
    Runs an async operation with a strict signal-based timeout for CPU-bound tasks.
    NOTE: This only works on Unix-like systems (Linux/macOS) where signal.SIGALRM exists.
    For Windows, a thread-based approach or purely async timeout (weak) would be needed,
    but `signal` is the only way to interrupt a tight CPU loop in Python on Unix.
    """
    # Set the signal handler
    original_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    # Schedule the alarm
    signal.alarm(int(timeout)) # signal.alarm takes integer seconds
    
    try:
        # We await the coroutine. If it does heavy CPU work *between* awaits, 
        # the signal will interrupt it.
        return await sync_coro
    except TimeoutError:
        print(f"Warning: Sync operation timed out after {timeout} seconds (Strict Signal).", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Sync operation failed with unexpected error: {e}", file=sys.stderr)
        return None
    finally:
        # Cancel the alarm
        signal.alarm(0)
        # Restore original handler
        signal.signal(signal.SIGALRM, original_handler)


async def run_with_timeout_or_detach(
    project_root: Path,
    file_paths: List[str],
    sync_coro_factory: Callable[[], Coroutine[Any, Any, Any]]
) -> None:
    """
    Executes an async synchronization operation.
    If the number of files is above a threshold, it detaches the operation using subprocess.
    Otherwise, it runs the operation with a strict timeout.
    """
    if SyncEngine.should_detach(len(file_paths)):
        print(f"[Coretext] Large commit detected ({len(file_paths)} files). Syncing in background...")
        # Detach using subprocess.Popen
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
            # AC 4: Feedback - "Syncing in background..." (already printed above)
        except Exception as e:
            print(f"Error: Failed to detach sync operation: {e}", file=sys.stderr)
            # Fail-open: continue, do not block original commit
    else:
        # AC 1: "If fast, it runs synchronously to provide immediate feedback."
        print(f"Processing {len(file_paths)} files, running sync operation...")
        # Run synchronously with timeout
        sync_coro = sync_coro_factory()
        await _run_sync_operation(sync_coro)

