# Story 3.4: CLI for `coretext lint` (Graph Integrity Check)

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to run an integrity check on the knowledge graph and my Markdown files via the CLI,
so that I can identify and fix any malformed Markdown or broken links before committing.

## Acceptance Criteria

1.  **Lint Command (`coretext lint`)**:
    *   [ ] Command is available via `coretext lint`.
    *   [ ] Triggers a "dry-run" integrity check within the daemon.
    *   [ ] Does NOT modify the persistent graph state in SurrealDB.

2.  **Integrity Checks**:
    *   [ ] **Malformed Markdown**: Identifies files that fail the BMAD parsing rules (FR7).
    *   [ ] **Dangling References**: Identifies Standard Markdown Links (`[Label](./path)`) that point to non-existent files or anchors (FR6).
    *   [ ] **Graph Consistency**: (Optional/Advanced) Identifies "Ghost Nodes" in DB that no longer exist on disk (if not handled by sync).

3.  **Reporting**:
    *   [ ] Displays a summary of issues found (e.g., "3 issues found in 2 files").
    *   [ ] Detailed report includes:
        *   File Path
        *   Line Number (if available/applicable)
        *   Error Type (e.g., "Parse Error", "Broken Link")
        *   Message / Details
    *   [ ] Uses `Rich` for formatted output (e.g., Tables or formatted lists with colors).
    *   [ ] Returns a non-zero exit code if issues are found (for CI/Hook integration).

## Tasks / Subtasks

- [ ] **Task 1: Implement Daemon Linting Logic**
    - [ ] Create `coretext/core/lint/` module (or integrate into `coretext/core/graph/integrity.py`).
    - [ ] Implement `check_markdown_syntax(files)`: reuse `coretext/core/parser/markdown.py`.
    - [ ] Implement `check_referential_integrity()`:
        - Scan all links in parsed models.
        - Verify target nodes exist in the Graph (or on disk).
    - [ ] Ensure this runs in "Read-Only" mode regarding the DB.

- [ ] **Task 2: Create Lint Endpoint**
    - [ ] Add `POST /lint` endpoint to `coretext/server/app.py` (or dedicated router).
    - [ ] Define Pydantic models for the Lint Report response (e.g., `LintReport`, `LintIssue`).

- [ ] **Task 3: Implement `lint` Command**
    - [ ] Add `lint` command to `coretext/cli/commands.py`.
    - [ ] Call daemon endpoint.
    - [ ] Render `LintReport` using `Rich` (Table is likely best: File | Line | Type | Message).
    - [ ] Handle `SystemExit` with code 1 if issues exist.

- [ ] **Task 4: Testing**
    - [ ] Unit tests for `LintManager`/Logic.
    - [ ] Integration test: Mock a file with a broken link and verify `lint` catches it.
    - [ ] Verify exit codes.

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

### File List
