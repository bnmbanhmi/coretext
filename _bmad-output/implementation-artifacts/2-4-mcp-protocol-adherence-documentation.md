Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

...

## Tasks / Subtasks

- [x] **Task 1: Standardize Tool Documentation** (AC: 1)
  - [x] Review `coretext/server/mcp/routes.py`.
  - [x] Ensure `search_topology` and `get_dependencies` have google-style docstrings.
  - [x] Ensure Pydantic input/output models have `description` fields for every attribute.
- [x] **Task 2: Implement Manifest Generation** (AC: 2, 4)
  - [x] Create `coretext/server/mcp/manifest.py` (or utility) to inspect FastAPI routes.
  - [x] Implement logic to extract tool name, description, and JSON schema from the route and its Pydantic models.
  - [x] Add `GET /mcp/manifest` endpoint in `routes.py` returning the list of tools.
- [x] **Task 3: Verify & Standardize Error Handling** (AC: 3)
  - [x] Audit existing endpoints for generic 500 errors.
  - [x] Ensure specific 4xx errors (400 Bad Request, 404 Not Found) are used with clear `detail` messages.
- [x] **Task 4: Testing**
  - [x] Unit test for manifest generation logic.
  - [x] Integration test calling `/mcp/manifest` and verifying output structure.

...

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Task 1: Verified and standardized docstrings and Pydantic model descriptions in `coretext/server/mcp/routes.py` to meet MCP requirements. Added `tests/unit/server/mcp/test_documentation.py` to enforce this.
- Task 2: Implemented `generate_manifest` in `coretext/server/mcp/manifest.py` and added `GET /mcp/manifest` endpoint.
- Task 3: Standardized error handling to prevent 500 leaks and return 404/501 appropriately for tool lookups.
- Task 4: Comprehensive test suite added for new functionality.

### File List
- coretext/server/mcp/routes.py (modified)
- coretext/server/mcp/manifest.py (new)
- tests/unit/server/mcp/test_documentation.py (new)
- tests/unit/server/mcp/test_manifest.py (new)
- tests/unit/server/mcp/test_routes.py (modified)
- tests/unit/server/mcp/test_error_handling.py (new)
- tests/unit/server/test_mcp.py (modified)

### Change Log
- 2025-12-27: Completed story 2-4. Implemented MCP manifest generation and standardized tool documentation/error handling.
- 2025-12-28: Fixed issues found during adversarial code review:
  - Added missing Example I/O to tool docstrings (AC 1).
  - Optimized `get_tool` by implementing manifest caching to reduce $O(N)$ scanning on every request.
  - Improved docstring parsing in manifest generation to be more robust (paragraph-based).
  - Enhanced documentation tests to dynamically discover Pydantic models.
