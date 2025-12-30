# Story 3.1: CLI for coretext init and Daemon Management

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to initialize `coretext` and manage its background daemon process via the CLI,
so that I can easily set up and control the system.

## Acceptance Criteria

1.  **Initialization (`coretext init`)**:
    *   Downloads the platform-specific SurrealDB binary to `~/.coretext/bin/` (if not present).
    *   Downloads and caches the embedding model (`nomic-embed-text-v1.5`) locally using `sentence-transformers` (if not present).
    *   Creates `~/.coretext/config.yaml` with default settings (if not present).
    *   Creates `~/.coretext/schema_map.yaml` with default schema mapping (if not present).
    *   Prompts to start the daemon immediately.

2.  **Daemon Management (`coretext start`)**:
    *   Starts the SurrealDB process in the background.
    *   Starts the FastAPI server (`coretext.server.app`) in the background.
    *   Creates `daemon.pid` and `server.pid` files in `.coretext/` for process tracking.
    *   Unpauses git hooks (removes `hooks_paused` file).

3.  **Daemon Termination (`coretext stop`)**:
    *   Stops the SurrealDB process and FastAPI server using PIDs.
    *   Pauses git hooks (creates `hooks_paused` file) to prevent hooks from failing while daemon is down.
    *   Cleans up PID files.

4.  **Configuration**:
    *   `~/.coretext/config.yaml` is the source of truth for user preferences (e.g., port, logging level).

## Tasks / Subtasks

- [ ] **Task 1: Enhance `coretext init`**
    - [ ] Add logic to download and cache `nomic-embed-text-v1.5` using `sentence_transformers` in `coretext/cli/commands.py` (or a helper).
    - [ ] Implement creation of `~/.coretext/config.yaml` with default values (e.g., `daemon_port: 8000`, `mcp_port: 8001`).
- [ ] **Task 2: Refine `coretext start` / `stop`**
    - [ ] Ensure `start` uses values from `config.yaml` if available.
    - [ ] Verify PID handling and process termination is robust (handles stale PIDs).
- [ ] **Task 3: Verify & Polish**
    - [ ] Check `coretext/db/client.py` binary download logic (already exists, ensure robustness).
    - [ ] Ensure `install_hooks` (existing) aligns with the daemon lifecycle (pause/unpause).

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
*   Checked existing `coretext/cli/commands.py`.
*   Checked existing `coretext/db/client.py`.

### Completion Notes List
*   Story created based on existing partial implementation. Focus is on filling gaps (model, config).
*   Confirmed dependencies in `pyproject.toml`.

### File List
*   `coretext/cli/commands.py`
*   `coretext/db/client.py`
*   `coretext/config.py` (Potential new file for default config definition)
