# Story 3.6: Epic 3 Demo & Verification Fixes

Status: Done

## Story

As a user (Minh),
I want a verified, end-to-end demo guide for Epic 3, covering all new CLI tools (`init`, `status`, `inspect`, `lint`, `new`),
so that I can confidently validate the developer workflow integration before we call this epic "done".

## Acceptance Criteria

1.  **Verified Demo Guide:** A comprehensive `docs/epic-3-demo-guide.md` exists, detailing step-by-step instructions for:
    *   Initialization (`coretext init`) and Idempotency checks.
    *   Status checks (`coretext status`).
    *   Template generation (`coretext new`).
    *   Graph linting (`coretext lint`) with both valid and invalid states.
    *   Node inspection (`coretext inspect`) verifying the visualization tree.
2.  **Fixes & Polish:** Any bugs (e.g., path resolution, exit codes, output formatting) found during the demo run are fixed immediately.
3.  **End-to-End Flow:** The guide must demonstrate a logical developer flow: Init -> New -> Lint -> Sync -> Inspect.

## Tasks / Subtasks

- [x] Create `docs/epic-3-demo-guide.md`.
- [x] Execute `coretext init` and verify config/binaries.
- [x] Execute `coretext status` and verify output.
- [x] Execute `coretext new` to create a test file.
- [x] Execute `coretext lint` to check the new file.
- [x] Execute `coretext inspect` on the new file (after sync).
- [x] Fix any issues found.

## Dev Notes

### Verification Report
*   **Init/Start Robustness:**
    *   Fixed `SurrealDBClient` to handle macOS binaries correctly (`.tgz` extension) and updated download logic for v2.0.4 compatibility.
    *   Implemented "Port Guard" in `start_surreal_db` to prevent spawning zombie processes when the port is already in use by another instance.
    *   Updated `coretext init` to default to SurrealDB v2.0.4.
*   **Process Management:**
    *   Addressed a critical race condition where `post-commit` hook would fail to connect to the DB because it tried to start a new instance (due to PID file visibility issues or flaky `is_running` checks) instead of reusing the existing daemon.
    *   The "Port Guard" ensures that if port 8000 is open, the client assumes the DB is running and proceeds to connect, solving the `[Errno 61]` and `no close frame` errors.
*   **Linting:** Verified that `coretext lint` correctly detects broken links in newly created files.
*   **Sync & Inspect:** Confirmed that `post-commit` sync works (after fixes) and updates the graph. Note: `inspect` must wait for the background sync to complete.

### Artifacts
*   `docs/epic-3-demo-guide.md`
*   `coretext/db/client.py` (Patched)
*   `coretext/cli/commands.py` (Updated default version)
*   `coretext/cli/utils.py`
*   `coretext/core/network.py`
