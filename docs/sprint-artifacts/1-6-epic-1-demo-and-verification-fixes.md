# Story 1.6: Epic 1 Demo & Verification Fixes

Status: Done

## Story

As a user (Minh),
I want a verified, end-to-end demo guide for Epic 1, along with the necessary system fixes to make it work,
so that I can confidently validate the core knowledge graph functionality before moving to Epic 2.

## Acceptance Criteria

1.  **Verified Demo Guide:** A comprehensive `docs/epic-1-demo-guide.md` exists, detailing step-by-step instructions for initialization, git hook installation, synchronization verification, and cleanup.
2.  **CLI Stop Command:** The `coretext stop` command is implemented and functional, allowing users to cleanly shut down the daemon as instructed in the guide.
3.  **Schema Robustness:** The database schema for edge tables (`contains`, `parent_of`, `references`) is updated to be `SCHEMALESS` to handle SurrealDB 2.0 `RELATE` behavior correctly (preventing `Found NONE for field...` errors).
4.  **GraphManager Resilience:** `GraphManager.ingest` handles string-based errors from SurrealDB client robustly and injects missing fields (like `order`) if necessary for legacy schema compatibility.
5.  **Reference Link Validation:** The demo guide and system verify that `references` edges (File -> File links) are correctly created and queryable.

## Tasks / Subtasks

- [x] Create `docs/epic-1-demo-guide.md` with explicit SurrealDB queries (`node:⟨id⟩`).
- [x] Implement `coretext stop` command in `coretext/cli/commands.py`.
- [x] Update `coretext/db/migrations.py` to define edge tables as `TYPE RELATION SCHEMALESS`.
- [x] Fix `GraphManager.ingest` to inject default `order=0` for `contains` edges.
- [x] Improve error handling in `GraphManager` to catch string-based errors from `surrealdb` client.
- [x] Verify end-to-end sync of `references` edges (File links).

## Dev Notes

### Major Fixes & Discoveries

*   **SurrealDB 2.0 Syntax:**
    *   **Record IDs:** Complex IDs with special chars or strings must use angle brackets: `node:⟨demo.md⟩`. Queries like `WHERE id = 'demo.md'` fail because of type mismatch (RecordID vs String).
    *   **Schema Strictness:** `DEFINE TABLE ... TYPE RELATION` without `SCHEMALESS` enforces strict existence checks on `in`/`out` records inside transactions, which caused `Found NONE for field in...` errors during batched ingestion. Switching to `SCHEMALESS` resolved this while maintaining the `RELATION` type for graph semantics.
*   **Transaction Handling:**
    *   The `surrealdb` Python client sometimes returns a generic string message (`The query was not executed due to a failed transaction`) instead of a structured error object when a transaction fails. Logic was added to catch this.
*   **Git Content Retrieval:**
    *   Verified that `get_head_content` correctly retrieves content from `HEAD` for the post-commit hook, ensuring parity with the file on disk for the parser.

## Dev Agent Record

### Context Reference

- `docs/epic-1-demo-guide.md`
- `chat_history/1_epic_retrospective.md`

### Agent Model Used

gemini-2.5-flash

### Completion Notes List

- Created comprehensive demo guide.
- Implemented requested `stop` command.
- Resolved blocking schema issues preventing edge creation.
- Verified full graph sync (Nodes + Edges + References).

### File List

- `docs/sprint-artifacts/1-6-epic-1-demo-and-verification-fixes.md`
- `docs/epic-1-demo-guide.md`
- `coretext/cli/commands.py`
- `coretext/db/migrations.py`
- `coretext/core/graph/manager.py`
