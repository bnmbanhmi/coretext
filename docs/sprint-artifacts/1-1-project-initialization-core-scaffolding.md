# Story 1.1: Project Initialization & Core Scaffolding

Status: ready-for-dev

## Story

As a developer,
I want to initialize the `coretext` project environment,
so that I have the core scaffold and dependencies in place to begin development.

## Acceptance Criteria

1.  Given I am in the project root directory
2.  When I run the initial scaffolding commands
3.  Then a Poetry project named `coretext` is created.
4.  And `fastapi[standard]`, `typer`, `pydantic`, `surrealdb`, `python-multipart`, `uvicorn`, `gitpython`, `sentence-transformers` are added as dependencies.
5.  And the basic project structure (`cli/`, `server/`, `core/`, `db/`) is laid out as defined in Architecture.md.
6.  And an extension.yaml manifest file is created at the root level for Gemini CLI integration.

## Tasks / Subtasks

- [ ] Create new Poetry project named `coretext`
- [ ] Add core dependencies: `fastapi[standard]`, `typer`, `pydantic`, `surrealdb`, `python-multipart`, `uvicorn`, `gitpython`, `sentence-transformers`
- [ ] Create basic project structure: `cli/`, `server/`, `core/`, `db/` with `__init__.py` files
- [ ] Setup `pyproject.toml` with basic project metadata
- [ ] Create `extension.yaml` for Gemini CLI integration

## Dev Notes

### Relevant Architecture Patterns and Constraints (from architecture.md and project_context.md)

*   **Language & Runtime:** Python 3.10+ (mandatory for modern type hinting PEP 604 `X | Y`, leveraged by Pydantic v2).
*   **Monorepo-ish Structure:** A single Python package `coretext/` containing both `cli/` (Typer) and `server/` (FastAPI) modules.
*   **Styling Solution:** `Rich` (used by Typer for beautiful, colored CLI output).
*   **Build Tooling:** `Poetry` (for strict dependency management and packaging).
*   **Testing Framework:** `Pytest` and `Pytest-Asyncio` (essential for async components).
*   **Development Experience:** Local-First (no Docker, `coretext init` will download platform-specific `surreal` binary).
*   **Type Safety:** Strict usage of Pydantic v2.x (Strict mode) for all data moving between Files <-> DB <-> API. Use `model_validate` (v2) not `parse_obj` (v1).
*   **Naming:** `snake_case` for everything except Classes (`PascalCase`).
*   **Imports:** Absolute imports only (`from coretext.core.graph import ...`).

### Source Tree Components to Touch (from architecture.md)

*   `coretext/` (root package directory)
*   `coretext/__init__.py`
*   `coretext/main.py`
*   `coretext/config.py`
*   `coretext/cli/__init__.py`
*   `coretext/cli/main.py`
*   `coretext/cli/commands.py` (for `init` command)
*   `coretext/server/__init__.py`
*   `coretext/server/app.py`
*   `coretext/core/__init__.py` (and sub-directories `graph/`, `sync/`, `parser/`, `vector/`)
*   `coretext/db/__init__.py`
*   `pyproject.toml`
*   `extension.yaml` (new file at project root)

### Testing Standards Summary (from architecture.md and project_context.md)

*   **Location:** `tests/` folder at root.
*   **Async:** Use `@pytest.mark.asyncio` for async tests.
*   **Structure:** Mirrors source (e.g., `tests/unit/core/graph/test_manager.py`).

## Dev Agent Record

### Context Reference

- `docs/epics.md`
- `docs/prd.md`
- `docs/architecture.md`
- `.coretext/project_context.md`

### Agent Model Used

gemini-2.5-flash

### Completion Notes List

Ultimate context engine analysis completed - comprehensive developer guide created

### File List
