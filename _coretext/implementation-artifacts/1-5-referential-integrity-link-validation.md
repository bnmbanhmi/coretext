# Story 1.5: Referential Integrity & Link Validation

Status: Done

## Story

As a `coretext` system,
I want to enforce referential integrity within the knowledge graph,
so that all links and dependencies between documents are valid and consistent.

## Acceptance Criteria

1.  Given Markdown files contain Standard Markdown Links (`[Label](./path)`)
2.  When the parsing and synchronization process runs
3.  Then these links are represented as `PARENT_OF` edges between graph nodes (e.g., H1 -> H2). (FR6)
4.  And `coretext` verifies that linked paths exist as valid graph nodes. (FR6)
5.  And "Dangling Reference" warnings are triggered during a "dry-run" linting phase before commit (via `coretext lint` or similar mechanism). (FR6)

## Tasks / Subtasks

- [x] Enhance `coretext/core/parser/markdown.py` to identify and extract Standard Markdown Links.
- [x] Modify `coretext/core/graph/manager.py` to create and manage graph edges for these links (e.g., `PARENT_OF`).
- [x] Implement validation logic within `coretext/core/sync/engine.py` or a dedicated linter (`coretext/cli/commands.py`) to check for existence of linked nodes during the pre-commit dry-run.
- [x] Integrate reporting of "Dangling Reference" warnings to the user via the CLI (pre-commit hook should block the commit).

## Dev Notes

### Relevant Architecture Patterns and Constraints

-   **Core Task:** Implement detection and reporting of dangling references during a pre-commit dry-run/linting phase.
-   **Parsing:** Must use AST-based parsing for link extraction from Markdown (`coretext/core/parser/markdown.py`).
-   **DB Interaction:** `GraphManager` is the sole gatekeeper for creating/updating graph entities (nodes/edges). Use "Upsert by Path" for nodes.
-   **Error Handling:** Ensure "Loud Failures" with clear reporting of malformed Markdown/links. Pre-commit should block if errors are found for referential integrity.
-   **Location of Logic:** Logic for link extraction in `coretext/core/parser/markdown.py`, graph edge management in `coretext/core/graph/manager.py`, and validation/linting within `coretext/core/sync/engine.py` or `coretext/cli/commands.py`.
-   **Naming/Style:** Adhere to `snake_case` for files/variables, `PascalCase` for classes, absolute imports.

### Source Tree Components to Touch

- `coretext/core/parser/markdown.py` (Enhance to identify and extract Standard Markdown Links)
- `coretext/core/graph/manager.py` (Modify to create and manage graph edges for links)
- `coretext/core/sync/engine.py` (Implement validation logic for pre-commit link validation)
- `coretext/cli/commands.py` (Integrate with linter for reporting warnings/blocking commits)
- `tests/unit/core/parser/test_markdown.py` (New tests for link extraction)
- `tests/unit/core/graph/test_manager.py` (New tests for link edge creation/management)
- `tests/unit/core/sync/test_engine.py` (New tests for pre-commit link validation)

### Testing Standards Summary

-   **Unit Tests:** For `markdown.py` (link extraction), `manager.py` (edge creation), `engine.py` (pre-commit validation).
-   **Integration Tests:** Simulate pre-commit hook with valid and invalid links, verifying blocking behavior and error reporting.

### Project Structure Notes

-   Logic for referential integrity checking will reside in `coretext/core/sync/engine.py` for pre-commit phase and potentially `coretext/cli/commands.py` for a dedicated `lint` command.

### Previous Story Intelligence

From Story 1.4 (`Git Repository Change Detection & Synchronization`):
-   The **Dual-Hook Strategy** is critical: **Pre-commit** is for safety and linting (dry-run, no DB writes, blocks commit on error), while **Post-commit** is for actual DB synchronization (fails open).
-   **Referential Integrity** specifically requires "Dangling Reference" warnings to be triggered during the pre-commit "dry-run," preventing broken graph edges from ever being committed.
-   The core components involved are `coretext/core/sync/engine.py`, `coretext/core/parser/markdown.py`, `coretext/core/graph/manager.py`, and `coretext/cli/commands.py`.

### Git Intelligence Summary

Recent commits show active development and stabilization of the `coretext/core/sync/` engine and associated Markdown parsing and graph node creation logic (Story 1.4). This provides a stable foundation for extending the parser to include link detection and integrating referential integrity checks into the existing pre-commit hook.

### Latest Technical Information

No new external technical information required beyond existing project context and documentation.

### Project Context Reference

-   `docs/epics.md`
-   `docs/prd.md`
-   `docs/architecture.md`
-   `.coretext/project_context.md`
-   `docs/sprint-artifacts/1-4-git-repository-change-detection-synchronization.md`

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

gemini-2.5-flash

### Debug Log References

- Verified `markdown.py` correctly extracts links and handles line numbers.
- Verified `SyncEngine` correctly reports parsing errors (including broken links) in DRY_RUN mode.
- Verified error message is "Dangling Reference".

### Completion Notes List

- Implemented link extraction in `MarkdownParser` including support for inline links and correct line number reporting.
- Links are stored as `PARENT_OF` edges (AC3 compliance).
- `SyncEngine` validation detects dangling references (links to non-existent files) during dry-run.
- Pre-commit hook (using `SyncEngine` dry-run) will block commits with "Dangling Reference" errors.
- Added comprehensive unit tests for parser and validation engine.
- [Code Review Fix] Corrected edge type to `PARENT_OF`.
- [Code Review Fix] Implemented Upsert logic in `GraphManager.ingest`.
- [Code Review Fix] Fixed `GraphManager` ID formatting.
- [Code Review Fix] Fixed `post_commit_hook` exit codes.

### File List
coretext/core/parser/markdown.py
coretext/core/graph/manager.py
coretext/cli/commands.py
tests/unit/core/parser/test_markdown_links.py
tests/unit/core/graph/test_manager.py
tests/unit/core/sync/test_engine_validation.py