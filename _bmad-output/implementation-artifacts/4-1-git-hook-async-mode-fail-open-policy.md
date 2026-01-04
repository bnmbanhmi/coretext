# Story 4.1: git-hook-async-mode-fail-open-policy

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want `coretext`'s Git hook to operate efficiently without blocking my `git commit` operations, even for large changes or in case of internal errors,
so that my workflow remains uninterrupted.

## Acceptance Criteria

1.  **Async Mode Trigger:**
    *   The `sync.py` (or equivalent hook logic) automatically detects if a sync operation is likely to be "slow" (e.g., > 10 files or predicted > 2 seconds).
    *   If slow, it detaches the sync process to the background and allows the `git commit` to complete immediately.
    *   If fast, it runs synchronously to provide immediate feedback.
2.  **Fail-Open Policy:**
    *   If the hook encounters ANY unhandled exception (crash, DB lock, network error), it must NOT block the git commit.
    *   The error is logged to `.coretext/coretext.log`.
    *   A user-friendly warning is printed to stderr: `[Coretext Warning] Sync failed - queuing for retry` (or similar).
    *   The hook exits with code `0`.
3.  **Background Reliability:**
    *   The detached background process must operate independently (daemonized) and not hang the terminal session.
    *   It must respect the "Port Guard" and existing daemon lifecycle (not spawning conflict processes).
4.  **Feedback:**
    *   When entering Async Mode, display a brief message: `[Coretext] Large commit detected. Syncing in background...`

## Tasks / Subtasks

- [x] **Analysis & Design:**
    - [x] Review `coretext/core/sync/engine.py` and `post-commit` hook structure.
    - [x] Design the "Detach" mechanism using `subprocess.Popen` with independent session.
- [x] **Implement Async Trigger Logic:**
    - [x] Add logic to count changed files in `SyncEngine`.
    - [x] Define threshold constant (e.g., `SYNC_ASYNC_THRESHOLD_FILES = 5`).
- [x] **Implement Background Spawning:**
    - [x] Create a new hidden CLI command (e.g., `coretext internal-sync`) if needed to act as the entry point for the detached process.
    - [x] Implement `subprocess.Popen` call to trigger this command.
- [x] **Implement Fail-Open Wrapper:**
    - [x] Wrap the main hook execution block in a broad `try...except Exception`.
    - [x] in `except`: Log full traceback to file, print generic warning to console, `sys.exit(0)`.
- [x] **Integration Testing:**
    - [x] Test with small commit (Sync).
    - [x] Test with large commit (Async/Background).
    - [x] Test with induced crash (Fail-Open).

## Dev Notes

### Previous Story Intelligence (Critical)

*   **Hook Hangs:** We recently fixed hangs in the `post-commit` hook caused by background threads (specifically `SentenceTransformer`).
    *   **Guideline:** Ensure the background process initializes its own resources cleanly.
    *   **Guideline:** Use `os._exit(0)` in the hook if necessary to force termination of stubborn threads, though a clean subprocess detach is preferred for the async path.
    *   **Env Var:** Keep `TOKENIZERS_PARALLELISM=false` to avoid deadlock risks in forked processes.
*   **Daemon Connection:**
    *   **Port Guard:** The background process must rely on the existing Daemon/Port Guard logic. It should not try to start a *new* daemon instance if one is running.
    *   **Resource Contention:** Ensure the background sync doesn't fight with the interactive CLI for DB locks (SurrealDB handles concurrency, but logic should be robust).

### Architecture & Design Patterns

*   **Fail-Open Pattern:**
    ```python
    try:
        # ... logic ...
    except Exception as e:
        logger.error(f"Fatal hook error: {e}", exc_info=True)
        console.print("[yellow]Coretext sync warning (non-blocking). Check logs.[/yellow]")
        sys.exit(0) # ALWAYS SUCCESS
    ```
*   **Detachment Pattern:**
    Use `subprocess.Popen(..., start_new_session=True)` (on Unix) or specific flags on Windows to ensure the child process outlives the parent hook.

### File Structure Notes

*   **`coretext/cli/commands.py`**: Might need a new `internal-sync` or `sync --background` command to serve as the clean entry point for the detached process.
*   **`coretext/core/sync/engine.py`**: Core logic for threshold checks.

### References

*   [Epic 4: System Reliability & Performance Optimization](../planning-artifacts/epics.md#epic-4-system-reliability--performance-optimization)
*   [Architecture: Fail-Open Policy](../planning-artifacts/architecture.md)

## Dev Agent Record

### Agent Model Used
Gemini-2.0-Flash-Thinking-Exp

### Debug Log References
*   See `docs/technical_debt.md` for any recurring hook issues.

### Completion Notes List
*   Implemented `SyncEngine.should_detach` and `SYNC_ASYNC_THRESHOLD_FILES` constant.
*   Refactored `coretext/core/sync/timeout_utils.py` to use `SyncEngine` logic.
*   Updated `coretext/cli/commands.py` to remove `&` from `post-commit` hook (allowing Python to control detachment).
*   Implemented Fail-Open policy in `post_commit_hook` with `logging` to `.coretext/coretext.log`.
*   Added comprehensive tests for detach logic, timeout utils, and fail-open behavior.

### File List
*   coretext/core/sync/engine.py
*   coretext/cli/commands.py
*   coretext/core/sync/timeout_utils.py
*   tests/unit/core/sync/test_engine.py
*   tests/unit/core/sync/test_detach_logic.py
*   tests/unit/core/sync/test_timeout_utils.py
*   tests/unit/cli/test_hooks.py
*   tests/unit/cli/test_hooks_fail_open.py
