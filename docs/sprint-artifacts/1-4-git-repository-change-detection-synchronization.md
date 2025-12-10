# Story 1.4: Git Repository Change Detection & Synchronization

Status: Ready for Review

## Story

As a developer, I want my local Markdown changes to be automatically synchronized with the `coretext` knowledge graph upon Git commit, so that the graph always reflects the latest project state without manual intervention.

## Acceptance Criteria

*   Given `coretext` is initialized and configured
*   When I run `coretext install-hooks`
*   Then the `pre-commit` and `post-commit` hooks are installed into `.git/hooks/`. (UX Addition)
*   When I make changes to Markdown files within the Git repository and execute `git commit`
*   Then the **Pre-commit Hook** runs in 'Dry-Run/Lint Mode'.
    *   It detects malformed Markdown and dangling links.
    *   If errors are found, it BLOCKS the commit and reports errors.
    *   It does NOT write to SurrealDB. (Strategy Shift: Data Integrity)
*   And after the commit is successfully recorded, the **Post-commit Hook** runs in 'Write Mode'.
    *   It detects the changed files from the just-completed commit.
    *   It updates or creates corresponding graph nodes in SurrealDB. (FR3, FR4)
    *   The Knowledge Graph state is versioned with the new Git commit hash. (FR5)
*   And the Post-commit hook completes within 1 second for typical commits (1-5 files).
*   And if the Post-commit hook predicts processing > 2 seconds, it detaches using `subprocess.Popen` (Simple Async). (Complexity Reduction)
*   And if the hook hangs, strict timeout (2s) kills it, logs a warning, and Fails Open. (Complexity Reduction)

## Tasks / Subtasks

- [x] Implement `coretext/core/sync/engine.py` with dual modes: `dry-run` (lint) and `write` (sync).
- [x] Implement `coretext/cli/commands.py`: Add `install-hooks` command to safely symlink/copy hooks.
- [x] Implement **Pre-commit Logic**: Change detection + `MarkdownParser` validation (No DB writes).
- [x] Implement **Post-commit Logic**: Change detection (HEAD diff) + `GraphManager.ingest` (DB writes).
- [x] Implement **Async/Timeout Logic**: Use `subprocess.Popen` for detachment and strict 2s timeout/fail-open wrapper.
- [x] Integrate with `markdown.py` parser and `graph/manager.py`.
- [x] Implement versioning strategy using Git commit hashes.

## Dev Notes

### Relevant Architecture Patterns and Constraints

*   **Project Structure:** `coretext/core/sync/` for Git hook logic, `coretext/core/parser/` for AST parsing, `coretext/core/graph/manager.py` for DB integration. `coretext/db/` for SurrealDB client.
*   **Dual-Hook Strategy (CRITICAL):**
    *   **Pre-commit:** Safety only. Linting. BLOCK on error. NO DB IO.
    *   **Post-commit:** Synchronization. UPDATE DB. Fail Open.
*   **Performance Requirements:**
    *   `Sync Latency`: < 1000ms target.
    *   `Async Strategy`: Use `subprocess.Popen` to detach if needed. NO complex daemon queue for MVP.
    *   `Timeout`: Strict 2s hard timeout. Kill process if exceeded. Log warning.
*   **Zero-Touch Synchronization:** `sync.py` hooks operate invisibly after `coretext install-hooks`.
*   **State Determinism via Git:** The database state must be a deterministic projection of the file system. Git Commit Hash as the version stamp.
*   **Strict Schema, Loud Failures:** Malformed Markdown must result in a `Parsing Error Node` (in memory during pre-commit) and block the commit.
*   **AST-Based Parsing:** Mandated to preserve semantic boundaries.
*   **"Fail-Open" Policy:** If `sync.py` encounters a crash (in post-commit), it must log the error, display a non-blocking warning, and allow workflow to proceed.
*   **Referential Integrity:** "Dangling Reference" warnings must be triggered during the pre-commit "dry-run".
*   **Technical Stack:** Python 3.10+, Poetry, FastAPI/Typer, SurrealDB, Nomic-Embed-Text-v1.5, GitPython.
*   **Testing Standards:** `Pytest`, `Pytest-Asyncio`. `tests/` folder mirroring project structure.
*   **Naming Conventions:** `snake_case` for variables, `PascalCase` for classes. Absolute imports.

### Source Tree Components to Touch

*   `coretext/core/sync/engine.py` (NEW - Git hook logic)
*   `coretext/core/sync/__init__.py` (NEW)
*   `coretext/cli/commands.py` (Potentially for `coretext sync` or `coretext hook install` commands)
*   `tests/unit/core/sync/test_engine.py` (NEW)
*   `tests/integration/test_sync_integration.py` (NEW)

### Testing Standards Summary

*   **Unit Tests:** For `coretext/core/sync/engine.py` covering file change detection, parsing integration, and DB synchronization calls.
*   **Integration Tests:** Simulate `git commit` hooks and verify DB state changes and performance.
*   **Mocking:** Mock `gitpython` calls and SurrealDB interactions where appropriate.
*   **Performance Tests:** Verify sync latency meets NFRs.

### Project Structure Notes

*   New module `coretext/core/sync/` to house the synchronization engine.

### Previous Story Intelligence

*   **Story 1.1 (Project Initialization & Core Scaffolding):** Provided the foundational Python project structure, dependencies (including `gitpython`), and established naming/coding conventions.
*   **Story 1.2 (SurrealDB Management & Schema Application):** Set up the SurrealDB instance, schema application, and the `GraphManager` as the sole gatekeeper for DB writes. Story 1.4 will extensively use `GraphManager.ingest()`.
*   **Story 1.3 (BMAD Markdown Parsing to Graph Nodes):** Developed the AST-based Markdown parser (`coretext/core/parser/markdown.py`) and canonical path normalization. This parser will be directly integrated into the sync engine to process changed Markdown files into graph nodes and edges. The "Loud Failures" and `ParsingErrorNode` from this story are crucial for handling malformed input during synchronization.

### Git Intelligence Summary

Recent commits indicate the successful completion and review of Story 1.3 (BMAD Markdown Parsing to Graph Nodes), confirming the stability of the parsing and graph node creation logic. This provides a solid foundation for integrating these capabilities into the Git synchronization process.

### Latest Technical Information

*   **GitPython (v3.1.45):** The latest stable version supports Python 3.7+ (compatible with our project's Python 3.10+). Key changes include enhanced typing and modifications to diff object handling (no `---` and `+++` headers, use `a_path`, `b_path`). This information is relevant for correctly implementing Git change detection using GitPython.

### Project Context Reference

*   `docs/epics.md`
*   `docs/prd.md`
*   `docs/architecture.md`
*   `.coretext/project_context.md`
*   `docs/sprint-artifacts/1-1-project-initialization-core-scaffolding.md`
*   `docs/sprint-artifacts/1-2-surrealdb-management-schema-application.md`
*   `docs/sprint-artifacts/1-3-bmad-markdown-parsing-to-graph-nodes.md`

### Dev Agent Record

### Agent Model Used

gemini-2.5-flash

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created
- Implemented `coretext/core/sync/engine.py` with `SyncEngine` and `SyncMode`.
- Created unit tests `tests/unit/core/sync/test_engine.py` covering dry-run and write modes.
- Implemented `coretext/core/sync/git_utils.py` for Git change detection.
- Created unit tests `tests/unit/core/sync/test_git_utils.py` for Git utilities.
- Implemented `coretext/cli/commands.py` `install_hooks` command to install Git hooks.
- Implemented `coretext/cli/commands.py` `hook pre-commit` logic for dry-run/linting of staged Markdown files.
- Created unit tests `tests/unit/cli/test_hooks.py` covering `install_hooks` and `pre-commit` hook.
- Moved `SyncEngine`, `SyncMode`, `get_staged_files`, `get_staged_content`, `MarkdownParser` imports to module level in `coretext/cli/commands.py` for better testability.
- Implemented `coretext/cli/commands.py` `post_commit_hook` logic for write/sync of committed Markdown files to SurrealDB.
- Implemented `coretext/core/sync/timeout_utils.py` for async operation detachment and timeout management.
- Created unit tests `tests/unit/core/sync/test_timeout_utils.py` for timeout and detachment logic.
- Updated `post_commit_hook` to use `run_with_timeout_or_detach` and added `--detached` flag.
- Added `commit_hash` field to `BaseNode` and `BaseEdge` models.
- Updated `SyncEngine` to propagate `commit_hash` to graph entities.
- Updated `post_commit_hook` to retrieve and pass `commit_hash`.

### File List

- `coretext/core/sync/__init__.py`
- `coretext/core/sync/engine.py`
- `coretext/core/sync/git_utils.py`
- `coretext/core/sync/timeout_utils.py`
- `coretext/cli/commands.py`
- `coretext/core/graph/models.py`
- `tests/unit/core/sync/test_engine.py`
- `tests/unit/core/sync/test_git_utils.py`
- `tests/unit/core/sync/test_timeout_utils.py`
- `tests/unit/cli/test_hooks.py`
