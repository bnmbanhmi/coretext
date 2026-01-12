# Story 3.4: CLI for `coretext lint` (Graph Integrity Check)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to run an integrity check on the knowledge graph and my Markdown files via the CLI,
so that I can identify and fix any malformed Markdown or broken links before committing.

## Acceptance Criteria

1.  **Lint Command (`coretext lint`)**:
    *   [x] Command is available via `coretext lint`.
    *   [x] Triggers a "dry-run" integrity check within the daemon.
    *   [x] Does NOT modify the persistent graph state in SurrealDB.

2.  **Integrity Checks**:
    *   [x] **Malformed Markdown**: Identifies files that fail the BMAD parsing rules (FR7).
    *   [x] **Dangling References**: Identifies Standard Markdown Links (`[Label](./path)`) that point to non-existent files or anchors (FR6).
    *   [x] **Graph Consistency**: (Optional/Advanced) Identifies "Ghost Nodes" in DB that no longer exist on disk (if not handled by sync).

3.  **Reporting**:
    *   [x] Displays a summary of issues found (e.g., "3 issues found in 2 files").
    *   [x] Detailed report includes:
        *   File Path
        *   Line Number (if available/applicable)
        *   Error Type (e.g., "Parse Error", "Broken Link")
        *   Message / Details
    *   [x] Uses `Rich` for formatted output (e.g., Tables or formatted lists with colors).
    *   [x] Returns a non-zero exit code if issues are found (for CI/Hook integration).

## Tasks / Subtasks

- [x] **Task 1: Implement Daemon Linting Logic**
    - [x] Create `coretext/core/lint/` module (or integrate into `coretext/core/graph/integrity.py`).
    - [x] Implement `check_markdown_syntax(files)`: reuse `coretext/core/parser/markdown.py`.
    - [x] Implement `check_referential_integrity()`:
        - Scan all links in parsed models.
        - Verify target nodes exist in the Graph (or on disk).
    - [x] Ensure this runs in "Read-Only" mode regarding the DB.

- [x] **Task 2: Create Lint Endpoint**
    - [x] Add `POST /lint` endpoint to `coretext/server/app.py` (or dedicated router).
    - [x] Define Pydantic models for the Lint Report response (e.g., `LintReport`, `LintIssue`).

- [x] **Task 3: Implement `lint` Command**
    - [x] Add `lint` command to `coretext/cli/commands.py`.
    - [x] Call daemon endpoint.
    - [x] Render `LintReport` using `Rich` (Table is likely best: File | Line | Type | Message).
    - [x] Handle `SystemExit` with code 1 if issues exist.

- [x] **Task 4: Testing**
    - [x] Unit tests for `LintManager`/Logic.
    - [x] Integration test: Mock a file with a broken link and verify `lint` catches it.
    - [x] Verify exit codes.

- [x] **Review Follow-ups (AI)**
    - [x] [AI-Review][High] Missing Anchor Validation [coretext/core/parser/markdown.py]
    - [x] [AI-Review][Medium] Fragile Project Root Detection [coretext/server/routers/lint.py]
    - [x] [AI-Review][Medium] CLI/Server Path Synchronization [coretext/cli/commands.py]

## Dev Notes

### Architecture & Compliance
*   **Daemon-Centric**: The heavy lifting (parsing, graph querying) happens in the Daemon. The CLI just presents the report.
*   **Reuse**: Heavily reuse `coretext/core/parser/markdown.py` logic. If it raises exceptions, catch them and convert to `LintIssue` objects instead of crashing.
*   **Performance**: If checking the whole graph is slow, consider scoping (not required for MVP, but keep in mind).

### Previous Story Intelligence (from Story 3.3)
*   **Path Handling**: Ensure file paths in the report are relative to the project root for readability (user doesn't need full absolute paths).
*   **Async Testing**: Continue using the fixed patterns for `AsyncMock` and `pytest-asyncio` markers. Avoid the pitfalls encountered in 3.3.
*   **Rich**: Use `Console` object consistently.

### Project Structure Notes
*   **Linter Logic**: `coretext/core/lint/manager.py` (New module recommended for separation of concerns).
*   **Models**: `coretext/core/lint/models.py` (for `LintReport`, `LintIssue`).
*   **Server**: `coretext/server/routers/lint.py` (New router).

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List
- Task 1: Implemented `LintManager` in `coretext/core/lint/manager.py` which reuses `MarkdownParser` to detect syntax errors and broken links (referential integrity). Added `LintReport` and `LintIssue` models.
- Task 2: Added `POST /lint` endpoint in `coretext/server/routers/lint.py` and registered it in `app.py`.
- Task 3: Added `lint` command to `coretext/cli/commands.py` using Rich for formatting.
- Task 4: Verified implementation with unit and integration tests covering logic, router, and CLI.

### File List
- coretext/core/lint/__init__.py
- coretext/core/lint/manager.py
- coretext/core/lint/models.py
- coretext/server/app.py
- coretext/server/routers/lint.py
- tests/unit/core/lint/test_lint_manager.py
- tests/unit/server/test_lint_router.py
- tests/unit/cli/test_lint_command.py

## Change Log
- 2025-12-31: Implemented linting logic, API endpoint, and CLI command. All tests passed.
- 2025-12-31: Code Review Fixes - Implemented robust anchor validation, fixed project root handling between CLI and Server.

## Status

done