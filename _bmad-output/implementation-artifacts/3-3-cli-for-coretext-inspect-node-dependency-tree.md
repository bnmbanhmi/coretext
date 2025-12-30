# Story 3.3: CLI for `coretext inspect <node>` (Dependency Tree)

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to inspect the dependency tree for a specific project node (e.g., a file or header) via the CLI,
so that I can understand its relationships within the knowledge graph.

## Acceptance Criteria

1.  **Inspect Command (`coretext inspect`)**:
    *   [ ] Command is available via `coretext inspect <node_id>`.
    *   [ ] Accepts `<node_id>` argument (can be a File Path or a specific Node ID).
    *   [ ] Queries the Daemon's MCP tool endpoint (e.g., `/mcp/tools/get_dependencies`).

2.  **Graph Traversal & Retrieval**:
    *   [ ] Daemon receives the request and uses `GraphManager` to traverse relationships.
    *   [ ] Retrieves direct dependencies (`depends_on`).
    *   [ ] Retrieves parent/child relationships (`PARENT_OF`, `CONTAINS`).
    *   [ ] Retrieves governance links (`governed_by`).

3.  **Output Visualization**:
    *   [ ] Displays a text-based tree using `Rich` (`rich.tree.Tree`).
    *   [ ] Root of the tree is the inspected node.
    *   [ ] Branches represent relationship types (e.g., "Depends On", "Contains").
    *   [ ] Leaves are the related nodes (formatted with ID and optional Type/Label).

4.  **Error Handling**:
    *   [ ] Handles "Node Not Found" gracefully (suggests ensuring file is indexed).
    *   [ ] Handles "Daemon Not Running" gracefully (same pattern as `status`).

## Tasks / Subtasks

- [ ] **Task 1: Verify/Enhance Daemon Endpoint**
    - [ ] Verify `POST /mcp/tools/get_dependencies` exists and returns structured graph data.
    - [ ] **Crucial:** Ensure the endpoint can handle `file_path` resolution if the user provides a relative path (e.g., `./docs/prd.md` vs absolute or internal ID).

- [ ] **Task 2: Implement `inspect` Command**
    - [ ] Add `inspect` command to `coretext/cli/commands.py`.
    - [ ] Use `httpx` to call the daemon endpoint.
    - [ ] Implement logic to handle CLI arguments.

- [ ] **Task 3: Implement Rich Tree Visualization**
    - [ ] Create a helper in `coretext/cli/utils.py` (e.g., `build_dependency_tree(data) -> Tree`).
    - [ ] Map graph relationship types to visual branches.
    - [ ] Apply color coding (e.g., Red for `governed_by`, Green for `depends_on`).

- [ ] **Task 4: Testing**
    - [ ] Add unit tests in `tests/unit/cli/test_inspect_command.py`.
    - [ ] Mock daemon responses with sample graph data.
    - [ ] Verify tree construction logic.

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

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
