**🔥 CODE REVIEW FINDINGS, Minh!**

**Story:** 4-4-graph-self-healing-integrity-checks.md
**Git vs Story Discrepancies:** 0 found
**Issues Found:** 2 High, 2 Medium, 1 Low

## 🔴 CRITICAL ISSUES

1.  **Broken Dangling Edge Logic (`GraphManager.prune_dangling_edges`)**:
    *   **Finding**: The query `DELETE {table} WHERE out = NONE ...` verifies if the `out` field *itself* is empty/null. It does **not** detect "ghost edges" where `out` contains a RecordID (e.g., `node:deleted_item`) that points to a non-existent record.
    *   **Impact**: The primary goal of "Automatic Pruning" fails. Ghost edges will persist.
    *   **Fix**: Use dereferencing to check for existence: `DELETE {table} WHERE out.id IS NONE OR in.id IS NONE;` (or `WHERE count(out) = 0`).

2.  **Hardcoded Database URL in `app.py`**:
    *   **Finding**: `run_startup_maintenance` hardcodes `AsyncSurreal("ws://localhost:8000/rpc")`.
    *   **Impact**: Fails if the user configures a different port or host in `config.yaml`. Violates "Configuration Management" and "Single Source of Truth".
    *   **Fix**: Use `load_config().db.url` (or equivalent) to get the connection string.

## 🟡 MEDIUM ISSUES

3.  **Redundant DB Connection in Startup**:
    *   **Finding**: The startup task creates a *new, separate* DB connection instead of reusing the application's connection pool or dependency injection system.
    *   **Impact**: Inefficient resource usage and potential race conditions/locking issues during startup.

4.  **Unit Tests Validation Gap**:
    *   **Finding**: `test_prune_dangling_edges_logic` mocks the DB and asserts that the *flawed query* (checking `out = NONE`) is generated. It validates that the code produces the wrong SQL, effectively cementing the bug.
    *   **Fix**: Update tests to expect the correct dereferencing syntax.

## 🟢 LOW ISSUES

5.  **Hardcoded Business Logic in GraphManager**:
    *   **Finding**: `_prepare_edge_data` contains `if edge.edge_type == "contains" ...`. This leaks domain logic into the generic manager.
