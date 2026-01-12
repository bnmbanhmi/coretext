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

*   **Framework:** MANDATORY usage of `pytest`. Do not write ad-hoc Python test scripts with `sys.exit()`.
*   **Execution:** Run tests via `poetry run pytest`.
*   **Location:** `tests/` folder at root.
*   **Async:** Use `@pytest.mark.asyncio` for async tests.
*   **Structure:** Mirrors source (e.g., `tests/unit/core/graph/test_manager.py`).
*   **Pragmatism:** If a test fails due to *framework limitations* (e.g., `CliRunner` with async), explicitly mark it as `@pytest.mark.skip` with a reason. DO NOT refactor working code to satisfy a broken test harness.

### Code Quality & Style Rules

*   **Naming:** `snake_case` for everything except Classes (`PascalCase`).
*   **Imports:** Absolute imports only (`from coretext.core.graph import ...`).
*   **Docstrings:** Google Style guide.

### Critical Don't-Miss Rules (Anti-Patterns)

*   **NO RAW SQL:** Do not write raw SurrealQL in API routes. Use the `GraphManager`.
*   **NO DOCKER:** Do not suggest Docker commands.
*   **UPSERT ONLY:** Always upsert nodes by `file_path` ID. Never create random UUIDs for file nodes.
*   **LOCAL ONLY:** Do not try to connect to remote SurrealDB instances.
*   **Gemini Manifest:** Always verify `gemini-extension.json` is updated when adding new CLI commands.


## Workflow & Pragmatism (Critical for Token Efficiency)
* **The "Stop-Loss" Rule:** If a specific test or bug fix fails **3 times** despite valid attempts, STOP. Do not loop endlessly. Evaluate if it is a tooling/harness limitation rather than a logic bug.
* **Technical Debt Protocol:**
    * **File:** `docs/technical_debt.md` (Source of Truth for known issues).
    * **Action:** If a non-critical issue (like a test harness quirk) blocks progress, **Log it** in `docs/technical_debt.md`, mark the test as `@pytest.mark.skip` or `@pytest.mark.xfail` with a comment referencing the issue, and **MOVE ON**.
    * **Check First:** Before attempting to fix a stubborn bug, check `docs/technical_debt.md` to see if it's a known "Won't Fix" or "Deferred" item.
* **Documentation First:** Update `docs/sprint-status.yaml` and related Markdown files *before* writing code to ensure context alignment.