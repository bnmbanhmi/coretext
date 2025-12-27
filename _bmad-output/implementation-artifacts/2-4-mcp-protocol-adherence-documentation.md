# Story 2.4: MCP Protocol Adherence & Documentation

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a `coretext` system,
I want strictly adhere to the MCP protocol and generate accurate tool definitions,
so that AI agents can reliably discover and utilize its capabilities.

## Acceptance Criteria

1.  **Tool Documentation:** All exposed MCP tools (`search_topology`, `get_dependencies`, etc.) are well-documented with comprehensive docstrings and example I/O in the code.
2.  **Manifest Generation:** The server generates a valid MCP manifest (JSON) defining all available tools, their descriptions, and input schemas.
3.  **Error Handling:** The API strictly adheres to the standard `HTTPException` for errors, ensuring consistent error responses for the agent.
4.  **Discovery Endpoint:** An endpoint (e.g., `GET /mcp/manifest` or `GET /mcp/tools`) is available to retrieve the tool definitions.

## Tasks / Subtasks

- [ ] **Task 1: Standardize Tool Documentation** (AC: 1)
  - [ ] Review `coretext/server/mcp/routes.py`.
  - [ ] Ensure `search_topology` and `get_dependencies` have google-style docstrings.
  - [ ] Ensure Pydantic input/output models have `description` fields for every attribute.
- [ ] **Task 2: Implement Manifest Generation** (AC: 2, 4)
  - [ ] Create `coretext/server/mcp/manifest.py` (or utility) to inspect FastAPI routes.
  - [ ] Implement logic to extract tool name, description, and JSON schema from the route and its Pydantic models.
  - [ ] Add `GET /mcp/manifest` endpoint in `routes.py` returning the list of tools.
- [ ] **Task 3: Verify & Standardize Error Handling** (AC: 3)
  - [ ] Audit existing endpoints for generic 500 errors.
  - [ ] Ensure specific 4xx errors (400 Bad Request, 404 Not Found) are used with clear `detail` messages.
- [ ] **Task 4: Testing**
  - [ ] Unit test for manifest generation logic.
  - [ ] Integration test calling `/mcp/manifest` and verifying output structure.

## Dev Notes

- **OpenAPI Integration:** You can leverage `app.openapi()` or `fastapi.openapi.utils.get_openapi` to get the raw schema, but the MCP manifest might need a simplified or specific format.
- **Manifest Format:** Unless a specific external standard is mandated, use a clean JSON structure:
  ```json
  {
    "tools": [
      {
        "name": "tool_name",
        "description": "...",
        "input_schema": { ... }
      }
    ]
  }
  ```
- **Reflection:** Use Python's `inspect` or FastAPI's internal route handling to dynamically generate this list, avoiding manual maintenance of the manifest.

### Project Structure Notes

- **Routes:** `coretext/server/mcp/routes.py`
- **Models:** `coretext/server/mcp/models.py` (if split) or inline.
- **Tests:** `tests/unit/server/mcp/test_manifest.py` (New file).

### References

- [FastAPI OpenAPI Utils](https://fastapi.tiangolo.com/advanced/extending-openapi/)
- [Project Architecture: Documentation Patterns](../planning-artifacts/architecture.md#documentation-patterns)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

### File List
