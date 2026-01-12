# Story 3.1: CLI for coretext init and Daemon Management

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to initialize `coretext` and manage its background daemon process via the CLI,
so that I can easily set up and control the system.

## Acceptance Criteria

1.  **Initialization (`coretext init`)**:
    *   [x] Downloads the platform-specific SurrealDB binary to `~/.coretext/bin/` (if not present).
    *   [x] Downloads and caches the embedding model (`nomic-embed-text-v1.5`) locally using `sentence-transformers` (if not present).
    *   [x] Creates `~/.coretext/config.yaml` with default settings (if not present).
    *   [x] Creates `~/.coretext/schema_map.yaml` with default schema mapping (if not present).
    *   [x] Prompts to start the daemon immediately.

2.  **Daemon Management (`coretext start`)**:
    *   [x] Starts the SurrealDB process in the background.
    *   [x] Starts the FastAPI server (`coretext.server.app`) in the background.
    *   [x] Creates `daemon.pid` and `server.pid` files in `.coretext/` for process tracking.
    *   [x] Unpauses git hooks (removes `hooks_paused` file).

3.  **Daemon Termination (`coretext stop`)**:
    *   [x] Stops the SurrealDB process and FastAPI server using PIDs.
    *   [x] Pauses git hooks (creates `hooks_paused` file) to prevent hooks from failing while daemon is down.
    *   [x] Cleans up PID files.

4.  **Configuration**:
    *   [x] `~/.coretext/config.yaml` is the source of truth for user preferences (e.g., port, logging level).

## Tasks / Subtasks

- [x] **Task 1: Enhance `coretext init`**
    - [x] Add logic to download and cache `nomic-embed-text-v1.5` using `sentence_transformers` in `coretext/cli/commands.py` (or a helper).
    - [x] Implement creation of `~/.coretext/config.yaml` with default values (e.g., `daemon_port: 8000`, `mcp_port: 8001`).
- [x] **Task 2: Refine `coretext start` / `stop`**
    - [x] Ensure `start` uses values from `config.yaml` if available.
    - [x] Verify PID handling and process termination is robust (handles stale PIDs).
- [x] **Task 3: Verify & Polish**
    - [x] Check `coretext/db/client.py` binary download logic (already exists, ensure robustness).
    - [x] Ensure `install_hooks` (existing) aligns with the daemon lifecycle (pause/unpause).

## Dev Notes

### Architecture & Compliance
*   **Daemon Lifecycle**: The daemon is composed of two processes: `surreal` (DB) and `uvicorn` (FastAPI/MCP). Both must be managed together.
*   **Local-First**: All artifacts (binaries, models, config) must be stored in `~/.coretext/` (user home) or `.coretext/` (project root) as appropriate. **Correction**: The story says `~/.coretext/` (Global/Home) for binaries and global config?
    *   *Correction/Refinement*: `coretext init` typically sets up *project-local* state `.coretext/` (schema, db) but binaries/models are better in *global* `~/.coretext/` to avoid duplication.
    *   *Decision*: Binaries and Models in `~/.coretext/` (Global Cache). Project-specific DB and Config in `project_root/.coretext/`.
    *   *Note*: The existing code uses `project_root/.coretext/` for DB and PIDs. `~/.coretext/bin` for binaries. This is consistent.
    *   *Model Cache*: `sentence-transformers` default cache is usually `~/.cache/...`. We should explicit set cache folder to `~/.coretext/cache/` to keep everything contained if possible, or just respect default. **Decision**: Let's set `cache_folder=Path.home() / ".coretext" / "cache"` for `SentenceTransformer` to keep it clean.

### Library Requirements
*   `typer`: For CLI commands.
*   `rich`: For output.
*   `surrealdb`: Python client.
*   `sentence_transformers`: For model download (`SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)`).

### Existing Code Analysis
*   `coretext/cli/commands.py` already has `init`, `start`, `stop`.
*   **Missing**: Model download in `init`.
*   **Missing**: `config.yaml` creation in `init`.
*   **Review**: Ensure `start` logic correctly binds to localhost and handles detached processes properly.

### Reference Files
*   `coretext/cli/commands.py`: Main logic location.
*   `coretext/db/client.py`: DB binary handling.

## Dev Agent Record

### Agent Model Used
Gemini-2.0-Flash

### Debug Log References
*   Implemented model download using `SentenceTransformer`.
*   Added `coretext/config.py` for configuration management.
*   Updated `coretext/cli/commands.py` to use `load_config` for ports.
*   Updated `coretext/db/client.py` to support configurable ports.
*   Fixed test harness issues with `AsyncMock` and `Path` mocking.

### Completion Notes List
*   `coretext init` now downloads the `nomic-embed-text-v1.5` model to `~/.coretext/cache`.
*   `coretext init` creates a project-local `.coretext/config.yaml`.
*   `coretext start` and `stop` now respect `daemon_port` and `mcp_port` from the config.
*   Robust PID handling implemented for both SurrealDB and FastAPI server.
*   Unit tests added for `init` and daemon management.
*   Fixed SurrealDB binary download logic for correct archive handling.
*   Consolidated PID management to `SurrealDBClient`.
*   Enhanced `start` command with robust process verification and port checking.
*   Removed redundant success messages in `init`.

### File List
*   `coretext/cli/commands.py`
*   `coretext/db/client.py`
*   `coretext/config.py`
*   `coretext/core/parser/schema.py`
*   `tests/unit/cli/test_init_command.py`
*   `tests/unit/cli/test_daemon_management.py`

## Senior Developer Review (AI)

**Date:** 2025-12-30
**Reviewer:** Minh

### Summary
The implementation was reviewed against the story requirements and found to be functionally complete but lacking in robustness for process management and binary handling. Critical issues regarding stale PID handling and binary naming conventions were identified and fixed.

### Fixes Applied
1.  **SurrealDB Binary Logic:** Refactored `coretext/db/client.py` to handle platform-specific archive formats (tar.gz/zip) and extract the binary correctly, addressing the mismatch with GitHub release assets.
2.  **Process Management:** Consolidated PID logic into `SurrealDBClient` and enhanced `coretext/cli/commands.py` to use `start_detached`. Added a verification loop to ensure processes are actually listening on their ports before reporting success.
3.  **Robustness:** Added checks for `server.pid` in addition to the DB PID to prevent half-started states or port conflicts.
4.  **Cleanup:** Removed redundant user messages for a cleaner CLI experience.

### Outcome
**Approved.** The implementation now meets the robust standards required for a developer tool.
