# Story 3.2: CLI for coretext status

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to check the operational status and health of the `coretext` daemon via the CLI,
so that I can quickly verify the system is running correctly.

## Acceptance Criteria

1.  **Status Command (`coretext status`)**:
    *   [x] Command is available via `coretext status`.
    *   [x] Pings the daemon's `/health` endpoint (default `http://localhost:8000/health`).
    *   [x] Reads port configuration from `~/.coretext/config.yaml` (or project local `.coretext/config.yaml`).

2.  **Output Information**:
    *   [x] Displays Daemon Status: "Running" (Green) or "Stopped" (Red) or "Unresponsive" (Yellow).
    *   [x] Displays Daemon PID and Port.
    *   [x] Displays "Sync Hook Status": "Active" (Green) or "Paused" (Yellow) (based on `hooks_paused` file presence).
    *   [x] Displays Coretext Version.

3.  **Error Handling**:
    *   [x] Gracefully handles connection refused errors (interprets as "Daemon Stopped").
    *   [x] Checks for stale PID file (PID file exists but process/port not responding).

4.  **UX/Formatting**:
    *   [x] Uses `Rich` library (Panels, Tables, or bold text) for clear, readable output.

## Tasks / Subtasks

- [x] **Task 1: Implement Health Check Logic**
    - [x] Create `check_daemon_health(port: int) -> dict` helper function in `coretext/cli/utils.py` (or `commands.py`).
    - [x] Use `httpx` (or `requests`) to ping `/health`.
    - [x] Implement logic to cross-reference with `daemon.pid` file in `.coretext/`.

- [x] **Task 2: Implement `status` Command**
    - [x] Add `status` command to `coretext/cli/commands.py`.
    - [x] Load config to get correct port.
    - [x] Check for `hooks_paused` file to report hook status.

- [x] **Task 3: UX Polish**
    - [x] Design `Rich` output format (e.g., a summary panel).
    - [x] Ensure "Stopped" state is clearly distinguishable from "Error".

- [x] **Task 4: Testing**
    - [x] Add unit tests in `tests/unit/cli/test_status_command.py`.
    - [x] Mock `httpx` responses for Running/Stopped/Error states.
    - [x] Mock file system for PID and hook status checks.

## Dev Notes

### Architecture & Compliance
*   **IPC Pattern**: The CLI is a separate process from the Daemon. Communication is strictly HTTP for status, plus file system checks for PIDs/Locks as fallback/verification.
*   **Config Source**: Must load `config.yaml` to know which port to ping. Do not hardcode `8000`.
*   **Library Usage**:
    *   `typer`: CLI framework.
    *   `rich`: Output formatting.
    *   `httpx`: HTTP Client (preferred over requests for async capability if needed, though CLI is synchronous here).
    *   `psutil`: Use if needing to verify PID corresponds to `coretext` process (optional, but good for robustness).

### Existing Code Context
*   `coretext/cli/commands.py`: Entry point for commands.
*   `coretext/config.py`: Should have config loading logic (from Story 3.1).
*   `coretext/server/health.py`: Should already exist (from Epic 2 / Story 2.1) exposing `/health`. *Verify this endpoint returns 200 OK*.

### Developer Guardrails
*   **Do not duplicate config logic**: Import `load_config` from `coretext.config` (or wherever it was placed in Story 3.1).
*   **Fail Fast**: If config is missing, report "Coretext not initialized. Run 'coretext init' first."
*   **Visuals**: Keep it clean. Don't dump raw JSON unless `--json` flag is added (optional enhancement).

## Dev Agent Record

### Agent Model Used
gemini-2.0-flash-exp

### Debug Log References
- Verified health check logic with `tests/unit/cli/test_status_command.py`.
- Verified CLI output with `tests/unit/cli/test_status_cli.py`.
- Encountered pre-existing test failures in `tests/unit/cli/test_commands_new.py`, `test_daemon_lifecycle.py`, and `test_daemon_management.py`. These were confirmed to fail even after reverting local changes.

### Completion Notes List
- Implemented `coretext status` command with `Rich` formatting.
- Implemented health check helper in `coretext/cli/utils.py`.
- Updated `/health` endpoint to return version information.
- Added comprehensive unit tests for health check and CLI command.
- **Code Review Fixes (2025-12-30):**
    - Split status reporting for FastAPI Server and SurrealDB Daemon.
    - Added comprehensive health check logic covering both services.
    - Fixed stale PID detection logic (added `os.kill` check).
    - Explicitly added `httpx` to `pyproject.toml`.
    - Corrected port usage to match config (`daemon_port` vs `mcp_port`).

### File List
- `coretext/cli/utils.py` (New)
- `coretext/cli/commands.py` (Modified)
- `coretext/server/health.py` (Modified)
- `coretext/db/migrations.py` (Modified - Lint Fixes)
- `pyproject.toml` (Modified)
- `tests/unit/cli/test_status_command.py` (New)
- `tests/unit/cli/test_status_cli.py` (New)
- `extension.yaml` (Modified)

### Change Log
- 2025-12-30: Implemented `coretext status` command and supporting health check logic.
- 2025-12-30: Fixed critical issues from code review (Split status, Stale PID, Dependency).

### Status
done
