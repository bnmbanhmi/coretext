# Story 3.2: CLI for coretext status

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to check the operational status and health of the `coretext` daemon via the CLI,
so that I can quickly verify the system is running correctly.

## Acceptance Criteria

1.  **Status Command (`coretext status`)**:
    *   [ ] Command is available via `coretext status`.
    *   [ ] Pings the daemon's `/health` endpoint (default `http://localhost:8000/health`).
    *   [ ] Reads port configuration from `~/.coretext/config.yaml` (or project local `.coretext/config.yaml`).

2.  **Output Information**:
    *   [ ] Displays Daemon Status: "Running" (Green) or "Stopped" (Red) or "Unresponsive" (Yellow).
    *   [ ] Displays Daemon PID and Port.
    *   [ ] Displays "Sync Hook Status": "Active" (Green) or "Paused" (Yellow) (based on `hooks_paused` file presence).
    *   [ ] Displays Coretext Version.

3.  **Error Handling**:
    *   [ ] Gracefully handles connection refused errors (interprets as "Daemon Stopped").
    *   [ ] Checks for stale PID file (PID file exists but process/port not responding).

4.  **UX/Formatting**:
    *   [ ] Uses `Rich` library (Panels, Tables, or bold text) for clear, readable output.

## Tasks / Subtasks

- [ ] **Task 1: Implement Health Check Logic**
    - [ ] Create `check_daemon_health(port: int) -> dict` helper function in `coretext/cli/utils.py` (or `commands.py`).
    - [ ] Use `httpx` (or `requests`) to ping `/health`.
    - [ ] Implement logic to cross-reference with `daemon.pid` file in `.coretext/`.

- [ ] **Task 2: Implement `status` Command**
    - [ ] Add `status` command to `coretext/cli/commands.py`.
    - [ ] Load config to get correct port.
    - [ ] Check for `hooks_paused` file to report hook status.

- [ ] **Task 3: UX Polish**
    - [ ] Design `Rich` output format (e.g., a summary panel).
    - [ ] Ensure "Stopped" state is clearly distinguishable from "Error".

- [ ] **Task 4: Testing**
    - [ ] Add unit tests in `tests/unit/cli/test_status_command.py`.
    - [ ] Mock `httpx` responses for Running/Stopped/Error states.
    - [ ] Mock file system for PID and hook status checks.

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
{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
