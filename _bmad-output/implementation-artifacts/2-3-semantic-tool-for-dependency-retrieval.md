# Story 2.3: Semantic Tool for Dependency Retrieval

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI agent,
I want a semantic tool to retrieve direct and indirect dependencies for a given node,
so that I can understand the impact of changes or prerequisites for implementation.

## Acceptance Criteria

1.  **Graph Traversal Logic:** The system implements a robust graph traversal mechanism in `coretext/core/graph/manager.py` that can follow `depends_on`, `governed_by`, and `PARENT_OF` relationships.
2.  **Dependency Retrieval:** A `get_dependencies(node_id: str, depth: int = 1)` method is added to `GraphManager` that returns a structured list of related nodes.
3.  **MCP Endpoint:** A `POST /mcp/tools/get_dependencies` endpoint is exposed in `coretext/server/mcp/routes.py`.
4.  **Input Handling:** The tool accepts a `node_identifier` which can be a file path (e.g., `coretext/core/graph/manager.py`) or a specific Node ID.
5.  **Output Format:** The response includes the `node_id`, `relationship_type`, and `direction` (upstream/downstream) for each dependency.
6.  **Performance:** The traversal is optimized using efficient SurrealQL queries (e.g., `SELECT ->depends_on->node FROM ...`).

## Tasks / Subtasks

- [ ] **Core: Graph Manager Expansion** (AC: 1, 2, 6)
  - [ ] Implement `get_dependencies(node_id, depth)` in `coretext/core/graph/manager.py`.
  - [ ] Construct SurrealQL query to traverse outgoing edges (`depends_on`, `governed_by`) and relevant incoming edges if needed (e.g., parent/child).
  - [ ] Handle recursion/depth limit to prevent infinite loops or massive payloads.
- [ ] **Server: MCP Endpoint** (AC: 3, 4, 5)
  - [ ] Add `get_dependencies` route to `coretext/server/mcp/routes.py`.
  - [ ] Define Pydantic models: `GetDependenciesRequest` (with `node_identifier`) and `GetDependenciesResponse`.
  - [ ] Ensure the response model cleanly maps graph concepts for the AI agent.
- [ ] **Testing**
  - [ ] Add unit tests in `tests/unit/core/graph/test_manager.py` for traversal logic.
  - [ ] Add integration tests for the new MCP endpoint.

## Dev Notes

- **SurrealQL Traversal:** Use the arrow syntax `->edge->node` for efficient hopping.
- **Node Identifier:** The system primarily uses `file_path` as the ID for file nodes. Ensure the input handler resolves this correctly (SurrealDB IDs are `table:id`).
- **Depth Control:** Default to depth=1 or 2 to start. Full recursive dependency trees can be large.
- **Dependency Injection:** Continue using the pattern established in Story 2.2 (`dependencies.py`) for injecting `GraphManager` into the router.

### Project Structure Notes

- **Core Logic:** `coretext/core/graph/manager.py`
- **API:** `coretext/server/mcp/routes.py`
- **Models:** Update `coretext/server/mcp/models.py` (or wherever request/response models are kept) if necessary, or define in `routes.py` if simple.

### References

- [SurrealDB Graph Traversal](https://surrealdb.com/docs/surrealql/datamodel/relations)
- [Project Architecture: API Patterns](../planning-artifacts/architecture.md#api-patterns)

## Dev Agent Record

### Agent Model Used
{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Developer Context

### Technical Requirements
*   **Language:** Python 3.10+
*   **Framework:** FastAPI (Server), SurrealDB (Database)
*   **Type Safety:** Strict Pydantic v2 models for all Inputs/Outputs.
*   **Async:** All DB interactions must be asynchronous.

### Architecture Compliance
*   **Gatekeeper Pattern:** All DB access MUST go through `GraphManager`. Do not write raw SQL in the route handler.
*   **MCP Tool Pattern:** The route must be defined as `/mcp/tools/get_dependencies`.
*   **Error Handling:** Use `HTTPException` for "Node not found" or validation errors.

### Library/Framework Requirements
*   **SurrealDB Client:** Use the existing `coretext.db.client` setup.
*   **FastAPI:** Use `APIRouter` in `coretext/server/mcp/routes.py`.

### File Structure Requirements
*   `coretext/core/graph/manager.py`: Business logic for traversal.
*   `coretext/server/mcp/routes.py`: API endpoint definition.
*   `tests/unit/core/graph/test_manager.py`: Tests.

### Testing Requirements
*   **Pytest:** Use `@pytest.mark.asyncio`.
*   **Mocking:** Mock the SurrealDB client in unit tests where possible, or use a test DB fixture for integration tests.

### Previous Story Intelligence (from Story 2.2)
*   **Dependency Injection:** In Story 2.2, we improved `dependencies.py` to allow easier testing of `GraphManager`. Reuse this `get_graph_manager` dependency.
*   **Pydantic Models:** Ensure models used in `routes.py` are properly imported or defined to avoid circular imports.
*   **Async/Await:** Story 2.2 confirmed that embedding generation (CPU bound) needed `asyncio.to_thread`. Graph traversal (IO bound) should just use `await` with the SurrealDB client.

### Git Intelligence Summary
*   **Recent Activity:**
    *   `coretext/core/graph/manager.py` was heavily modified for `search_topology`.
    *   `coretext/server/mcp/routes.py` exists and has `search_topology`.
    *   `coretext/server/dependencies.py` was added/refactored.
    *   Tests were added in `tests/unit/core/graph/`.
*   **Pattern:** The pattern is: Update Manager -> Update Routes -> Update Tests.

### Project Context Reference
*   [Architecture](../planning-artifacts/architecture.md)
*   [Epics](../planning-artifacts/epics.md)

### Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created.
