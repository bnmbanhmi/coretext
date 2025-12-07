# Story 1.2: SurrealDB Management & Schema Application

Status: ready-for-dev

## Story

As a `coretext` system,
I want to manage a local SurrealDB instance and apply the graph schema automatically,
so that the knowledge graph has a persistent and structured storage.

## Acceptance Criteria

1. Given the `coretext` project is initialized
2. When `coretext init` is executed
3. Then the platform-specific `surreal` binary is downloaded to `~/.coretext/bin/`.
4. And a `surreal.db` file is created or found in `.coretext/` (in the project root).
5. And on daemon startup, the SurrealDB schema (defined by Pydantic models mapped via `schema_map.yaml`) is automatically applied.
6. And `GraphManager` class is implemented to be the sole gatekeeper for DB writes.

## Tasks / Subtasks

- [x] Implement `coretext/db/client.py` for SurrealDB connection and binary management (AC 3, 4)
  - [x] Implement download logic for platform-specific `surreal` binary
  - [x] Implement process management to start/stop SurrealDB
- [x] Implement `coretext/db/migrations.py` for schema definition (AC 5)
  - [x] Define SurrealQL schema definitions for nodes and edges
  - [x] Implement logic to apply schema on startup
- [x] Implement Pydantic models for Graph Entities (AC 5)
  - [x] Create `coretext/core/graph/models.py` with `Node`, `Edge` base classes
- [x] Implement `coretext/core/graph/manager.py` (AC 6)
  - [x] Implement `GraphManager` class pattern
  - [x] Implement basic CRUD operations (create, read, update, delete)
- [x] Implement `schema_map.yaml` loading logic (AC 5)
  - [x] Create default `schema_map.yaml` in `.coretext/`
  - [x] Implement parser to map BMAD concepts to DB schema
- [x] Update `coretext/cli/commands.py` to include `init` logic (AC 2)

## Dev Notes

### Relevant Architecture Patterns and Constraints

*   **Database:** SurrealDB (Local-first, Embedded). NO Docker.
*   **Binary Management:** `coretext init` must download the binary to `~/.coretext/bin/` (User Home).
*   **Data Storage:** `surreal.db` must be stored in `.coretext/` (Project Root).
*   **Schema Strategy:** "Schema Projection". Decoupled internal Pydantic models <-> `schema_map.yaml`.
*   **Access Control:** `GraphManager` class is the ONLY place where DB writes happen.
*   **Naming:** `snake_case` for DB tables/fields. `PascalCase` for Pydantic models.
*   **Async:** All DB operations must be `async/await`.
*   **Type Safety:** Strict Pydantic v2 usage (`model_validate`).
*   **IPC:** Daemon manages the SurrealDB process.

### Source Tree Components to Touch

*   `coretext/db/client.py` (NEW)
*   `coretext/db/migrations.py` (NEW)
*   `coretext/db/__init__.py`
*   `coretext/core/graph/manager.py` (NEW)
*   `coretext/core/graph/models.py` (NEW)
*   `coretext/core/graph/__init__.py`
*   `coretext/cli/commands.py` (Update for `init`)
*   `.coretext/schema_map.yaml` (NEW)
*   `tests/unit/core/graph/test_manager.py` (NEW)
*   `tests/unit/db/test_client.py` (NEW)

### Testing Standards Summary

*   **Mocking:** Mock the `surreal` binary download and process start for unit tests.
*   **Integration:** Use `pytest-asyncio` for DB tests.
*   **Safety:** Ensure tests do not overwrite the user's actual `~/.coretext/` data or project `.coretext/` data (use temp dirs).

### Project Structure Notes

*   **User Config:** `~/.coretext/` (Home directory) stores the binary and global config.
*   **Project Config:** `.coretext/` (Project root) stores `surreal.db` and `schema_map.yaml`.
*   **Conflicts:** Ensure that the local `.coretext` folder is git-ignored (except maybe config/schema if meant to be shared, but DB definitely ignored). The `schema_map.yaml` should probably be committed if it's part of the project def, but `surreal.db` should be in `.gitignore`.

### References

*   [Epic 1.2](../epics.md#story-12-surrealdb-management--schema-application)
*   [Architecture - Data Architecture](../architecture.md#data-architecture)
*   [Architecture - Project Structure](../architecture.md#complete-project-directory-structure)

## Dev Agent Record

### Context Reference

- `docs/epics.md`
- `docs/prd.md`
- `docs/architecture.md`
- `docs/sprint-artifacts/1-1-project-initialization-core-scaffolding.md`

### Agent Model Used

gemini-2.5-flash

### Debug Log References

### Completion Notes List

### File List
