# Story 3.3: CLI for `coretext inspect <node>` (Dependency Tree)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to inspect the dependency tree for a specific project node (e.g., a file or header) via the CLI,
so that I can understand its relationships within the knowledge graph.

## Acceptance Criteria

1.  **Inspect Command (`coretext inspect`)**:
    *   [x] Command is available via `coretext inspect <node_id>`.
    *   [x] Accepts `<node_id>` argument (can be a File Path or a specific Node ID).
    *   [x] Queries the Daemon's MCP tool endpoint (e.g., `/mcp/tools/get_dependencies`).

2.  **Graph Traversal & Retrieval**:
    *   [x] Daemon receives the request and uses `GraphManager` to traverse relationships.
    *   [x] Retrieves direct dependencies (`depends_on`).
    *   [x] Retrieves parent/child relationships (`PARENT_OF`, `CONTAINS`).
    *   [x] Retrieves governance links (`governed_by`).

3.  **Output Visualization**:
    *   [x] Displays a text-based tree using `Rich` (`rich.tree.Tree`).
    *   [x] Root of the tree is the inspected node.
    *   [x] Branches represent relationship types (e.g., "Depends On", "Contains").
    *   [x] Leaves are the related nodes (formatted with ID and optional Type/Label).

4.  **Error Handling**:
    *   [x] Handles "Node Not Found" gracefully (suggests ensuring file is indexed).
    *   [x] Handles "Daemon Not Running" gracefully (same pattern as `status`).

## Tasks / Subtasks

- [x] **Task 1: Verify/Enhance Daemon Endpoint**
    - [x] Verify `POST /mcp/tools/get_dependencies` exists and returns structured graph data.
    - [x] **Crucial:** Ensure the endpoint can handle `file_path` resolution if the user provides a relative path (e.g., `./docs/prd.md` vs absolute or internal ID).

- [x] **Task 2: Implement `inspect` Command**
    - [x] Add `inspect` command to `coretext/cli/commands.py`.
    - [x] Use `httpx` to call the daemon endpoint.
    - [x] Implement logic to handle CLI arguments.

- [x] **Task 3: Implement Rich Tree Visualization**
    - [x] Create a helper in `coretext/cli/utils.py` (e.g., `build_dependency_tree(data) -> Tree`).
    - [x] Map graph relationship types to visual branches.
    - [x] Apply color coding (e.g., Red for `governed_by`, Green for `depends_on`).

- [x] **Task 4: Testing**
    - [x] Add unit tests in `tests/unit/cli/test_inspect_command.py`.
    - [x] Mock daemon responses with sample graph data.
    - [x] Verify tree construction logic.

## Dev Notes

### Architecture & Compliance
*   **Separation of Concerns:** The CLI does **zero** graph traversal logic. It only renders what the Daemon returns.
*   **Data Contract:** The Daemon (MCP Tool) returns a JSON structure. The CLI consumes it.
    *   *Expected JSON format:* `{"node": {...}, "relationships": {"depends_on": [...], "governed_by": [...]}}` (or similar).
*   **Endpoint Usage:** Reuse the `get_dependencies` tool created in Story 2.3.
    *   *Ref:* `coretext/server/mcp/tools.py` (or `routes.py`).

### Learnings from Previous Story (3.2 - Status)
*   **IPC:** Use `httpx` for communication.
*   **Config:** Load port from `config.yaml`.
*   **Helpers:** Reuse `coretext/cli/utils.py` for common CLI utilities if applicable.
*   **Robustness:** Handle connection errors just like `coretext status`.

### Project Structure Notes
*   **CLI:** `coretext/cli/commands.py`
*   **Utils:** `coretext/cli/utils.py`
*   **Tests:** `tests/unit/cli/`

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Fixed numerous pre-existing test failures related to `AsyncMock` and `asyncio.run` in CLI tests.
- Resolved `einops` dependency issue in the virtualenv.
- Standardized `GraphManager` query result handling for SurrealDB python client.

### Completion Notes List

- ✅ Implemented `coretext inspect <node_id>` command.
- ✅ Added path normalization for CLI arguments (handles `./` and `../`).
- ✅ Implemented `Rich` tree visualization with relationship-specific color coding.
- ✅ Enhanced `get_dependencies` tool to include `from_node_id` for tree reconstruction.
- ✅ Updated `extension.yaml` with the new command.
- ✅ Verified all ACs with new unit tests and full regression suite.

### File List

- `coretext/cli/commands.py` (Modified: added `inspect` command)
- `coretext/cli/utils.py` (Modified: added `build_dependency_tree`)
- `coretext/server/mcp/routes.py` (Modified: path normalization, model update)
- `coretext/core/graph/manager.py` (Modified: `get_dependencies` update, robust query handling)
- `extension.yaml` (Modified: added `inspect`)
- `tests/unit/cli/test_inspect_command.py` (New: CLI tests)
- `tests/unit/server/mcp/test_routes_path.py` (New: path normalization tests)
- `tests/unit/server/mcp/test_routes.py` (Modified: updated mocks)
- `tests/unit/core/graph/test_manager.py` (Modified: updated mocks/assertions)
- `tests/unit/core/graph/test_manager_ingest.py` (Modified: updated mocks)
- `tests/unit/cli/test_daemon_lifecycle.py` (Modified: fixed async mocks)
- `tests/unit/cli/test_daemon_management.py` (Modified: fixed async mocks)
- `tests/unit/cli/test_commands_new.py` (Modified: fixed async mocks)
- `tests/unit/db/test_client.py` (Modified: fixed tarball mock)
- `tests/integration/server/test_story_2_1.py` (Modified: updated assertions)
- `tests/unit/server/test_health.py` (Modified: updated assertions)
- `tests/unit/server/mcp/test_manifest.py` (Modified: updated assertions)

