## Technology Stack & Versions

*   **Python:** 3.10+
*   **FastAPI:** Latest stable (with `fastapi[standard]`)
*   **Typer:** Latest stable
*   **SurrealDB:** Binary managed by `init`; Client: `surrealdb`
*   **Pydantic:** v2.x (Strict mode)
*   **Embedding:** `sentence-transformers` (nomic-embed-text-v1.5)
*   **Testing:** `pytest`, `pytest-asyncio`

## Critical Implementation Rules

### Language-Specific Rules (Python)

*   **Type Hinting:** Strict usage of Python 3.10+ type hints (e.g., `list[str] | None`). No `List`, `Optional` from `typing`.
*   **Async:** All IO-bound operations (DB, Network) must be `async/await`.
*   **Pydantic:** Use `model_validate` (v2) not `parse_obj` (v1).

### Framework-Specific Rules

*   **FastAPI:**
    *   Routes must have docstrings with example IO.
    *   Use `APIRouter` for modularity in `server/mcp/routes.py`.
*   **Typer:**
    *   Use `Rich` for all CLI output (spinners, tables, error messages).
    *   No `print()` calls; use `console.print()`.
*   **SurrealDB:**
    *   ALL DB writes go through `GraphManager`.
    *   Use strict SurrealQL syntax in queries.

### Testing Rules

*   **Location:** `tests/` folder at root.
*   **Async:** Use `@pytest.mark.asyncio` for async tests.
*   **Structure:** Mirrors source (e.g., `tests/unit/core/graph/test_manager.py`).

### Code Quality & Style Rules

*   **Naming:** `snake_case` for everything except Classes (`PascalCase`).
*   **Imports:** Absolute imports only (`from coretext.core.graph import ...`).
*   **Docstrings:** Google Style guide.

### Critical Don't-Miss Rules (Anti-Patterns)

*   **NO RAW SQL:** Do not write raw SurrealQL in API routes. Use the `GraphManager`.
*   **NO DOCKER:** Do not suggest Docker commands.
*   **UPSERT ONLY:** Always upsert nodes by `file_path` ID. Never create random UUIDs for file nodes.
*   **LOCAL ONLY:** Do not try to connect to remote SurrealDB instances.
*   **Gemini Manifest:** Always verify `extension.yaml` is updated when adding new CLI commands.
