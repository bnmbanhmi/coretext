# Story 2.5: Epic 2 Demo & Verification Fixes

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user (Minh),
I want a verified, end-to-end demo guide for Epic 2, along with any necessary system fixes,
so that I can confidently validate the AI Agent capabilities (MCP server and semantic tools) and ensure the system is ready for Epic 3.

## Acceptance Criteria

1.  **Verified Demo Guide:** A comprehensive `docs/epic-2-demo-guide.md` exists, detailing step-by-step instructions for:
    *   Starting the full `coretext` system (DB + Daemon).
    *   Verifying MCP Server Health (via `curl` or browser).
    *   Verifying `search_topology` tool functionality (semantic search).
    *   Verifying `get_dependencies` tool functionality (graph traversal).
2.  **Sample Data Verification:** The guide includes steps to ensure the knowledge graph is populated (e.g., syncing the `coretext` repo itself) so that queries yield meaningful results.
3.  **Tool Inspection Scripts:** Simple `curl` commands or a Python helper script are provided to easily test the POST endpoints without complex manual JSON construction.
4.  **Fixes & Polish:** Any usability issues or bugs discovered during the manual verification process are identified and fixed (e.g., error messages, missing fields in response).
5.  **MCP Manifest Verification:** verify the `/mcp/manifest` endpoint returns the correct tool definitions.

## Tasks / Subtasks

- [x] **Create Demo Guide:** Draft `docs/epic-2-demo-guide.md` based on the Epic 1 template but focused on MCP tools. (AC: 1)
- [x] **Develop Test Scripts/Commands:** Create reproducible `curl` commands or a `scripts/demo_epic_2.py` script to interact with the API. (AC: 3)
- [x] **End-to-End Verification:**
    - [x] Run `coretext init` / `start`.
    - [x] Sync the repo.
    - [x] Run the test commands.
    - [x] Verify results against expectations.
- [x] **Apply Fixes:** Fix any bugs found during verification. (AC: 4)
- [x] **Verify Manifest:** Check `/mcp/manifest` output. (AC: 5)

## Dev Notes

### Context & Architecture
*   **MCP Server:** Runs on `http://127.0.0.1:8001`.
*   **Endpoints:**
    *   `GET /health`
    *   `GET /mcp/manifest`
    *   `POST /mcp/tools/search_topology`
    *   `POST /mcp/tools/get_dependencies`

### Fixes Applied during Verification
1.  **Singleton Dependencies:** Refactored `dependencies.py` to use singletons for `VectorEmbedder` and `SchemaMapper`, preventing heavy model reloads on every request (fixing 500 errors).
2.  **Sync Engine Robustness:** Fixed missing `asyncio` import and sequentialized embedding generation in `GraphManager.ingest` to avoid PyTorch threading/tensor errors.
3.  **Schema Update:** Made `embedding` field optional with `DEFAULT []` in `migrations.py` to prevent sync failures on records without embeddings.
4.  **Dependency Logic:** Updated `get_dependencies` to include `contains` and `references` relationships and added `type::record()` casting for robust Record ID lookup.
5.  **Node ID Resolution:** Fixed `routes.py` to correctly resolve node type prefixes (e.g. `file:`) using `SchemaMapper` before querying.
6.  **AI Review Fixes:**
    *   **Manifest:** Updated `manifest.py` to preserve full docstrings (including Example I/O) for better Agent context.
    *   **Demo Script:** Improved `scripts/demo_epic_2.py` robustness to skip specific file tests if the file is missing in the graph.
    *   **Dead Code:** Removed unimplemented `GET /tools/{tool_name}` endpoint from `routes.py` to avoid API confusion.
7.  **SurrealDB Library Compatibility:** Updated `GraphManager` to use `query_raw` for multi-statement queries and transactions, ensuring correct response handling for `surrealdb==1.0.7` where `query` only returns the first result set.
8.  **RecordID Serialization:** Implemented `_convert_ids` helper in `GraphManager` to recursively convert SurrealDB `RecordID` objects to strings, fixing Pydantic serialization errors in MCP tool responses.
9.  **Semantic Search Robustness:** Updated `search_topology` query to explicitly filter out `NONE` embeddings (`WHERE embedding != NONE`), preventing SurrealDB errors during vector similarity calculation on nodes without embeddings.

### References
*   [Epic 1 Demo Guide](../../docs/epic-1-demo-guide.md)
*   [Story 1.6](_coretext/implementation-artifacts/1-6-epic-1-demo-and-verification-fixes.md)

## Dev Agent Record

### Agent Model Used
gemini-2.5-flash

### Debug Log References
- Fixed `einops` import error in post-commit hook.
- Resolved `NameError: name 'SchemaMapper' is not defined` in `routes.py`.
- Fixed `SurrealDB Transaction Error (Nodes): Found NONE for field embedding`.

### Completion Notes List
- Created comprehensive `docs/epic-2-demo-guide.md`.
- Created helper script `scripts/demo_epic_2.py`.
- Verified MCP server health and manifest endpoints.
- Verified semantic search and dependency tools with manual fixes.
- Updated `sprint-status.yaml`.

### File List
- docs/epic-2-demo-guide.md
- scripts/demo_epic_2.py
- coretext/server/dependencies.py
- coretext/core/graph/manager.py
- coretext/db/migrations.py
- coretext/server/mcp/routes.py
- coretext/server/mcp/manifest.py
- _coretext/implementation-artifacts/2-5-epic-2-demo-and-verification-fixes.md
