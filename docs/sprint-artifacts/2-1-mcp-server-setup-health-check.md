# Story 2.1: mcp-server-setup-health-check

Status: Ready for Review

## Story

As a `coretext` developer, 
I want an MCP server set up with health check endpoints, 
so that the Gemini CLI can communicate with it and verify its operational status.

## Acceptance Criteria

1.  **FastAPI Application Scaffold:** A FastAPI application is initialized in `coretext/server/app.py`.
2.  **Localhost Binding:** The server is configured to bind strictly to `127.0.0.1`.
3.  **Health Check Endpoint:** A GET `/health` endpoint exists that returns a 200 OK status with a JSON body `{"status": "OK"}`.
4.  **Security Guardrail:** The `/health` endpoint verifies that the request originates from `127.0.0.1` or `::1`, returning 403 Forbidden otherwise.
5.  **MCP Route Structure:** A modular router structure is established in `coretext/server/mcp/routes.py` and included in the main app with the prefix `/mcp`.
6.  **MCP Endpoint Pattern:** The server exposes an endpoint pattern for tools, e.g., `/mcp/tools/{tool_name}`, even if initially returning a "not implemented" error.
7.  **Docstrings & Schema:** All routes have Google-style docstrings and Pydantic models for I/O to support automatic MCP tool generation.
8.  **Daemon Integration:** The `coretext start` command is updated to launch both the SurrealDB binary AND the FastAPI server as background processes.

## Tasks / Subtasks

- [x] Implement `coretext/server/app.py` as the main FastAPI entry point. (AC: 1, 2)
- [x] Implement `coretext/server/health.py` with localhost-only validation logic. (AC: 3, 4)
- [x] Create `coretext/server/mcp/routes.py` with an `APIRouter` and initial tool stubs. (AC: 5, 6, 7)
- [x] Update `coretext/cli/commands.py` to manage the FastAPI daemon lifecycle. (AC: 8)
  - [x] Add `uvicorn` as a dependency if missing.
  - [x] Update `start` to launch the FastAPI server using `subprocess.Popen` or similar.
  - [x] Update `stop` to terminate the FastAPI server process (using PID tracking).
- [x] Add unit tests for the health check and initial stubs in `tests/unit/server/test_health.py`.

## Dev Context & Guardrails

### Architecture Intelligence
*   **FastAPI APIRouter:** Use `APIRouter` for modularity as specified in `docs/architecture.md`.
*   **Local-First:** Strict binding to `127.0.0.1` is a mandatory security requirement [Source: docs/prd.md#Security].
*   **Docstrings:** Google Style guide docstrings are REQUIRED for all routes to enable downstream automatic MCP manifest generation [Source: docs/architecture.md#Documentation Patterns].
*   **IPC:** Use the established `.coretext/daemon.pid` pattern for process management. Since we now have two processes (SurrealDB and FastAPI), consider using separate PID files (e.g., `surreal.pid` and `server.pid`) or a unified management strategy.

### Previous Story Intelligence (Epic 1)
*   **Daemon Lifecycle:** Story 1.6 established a "hooks paused" marker file `.coretext/hooks_paused`. Ensure the new FastAPI server respects or coordinates with this state if necessary.
*   **SurrealDB Connection:** The server will eventually need to connect to SurrealDB. Ensure it uses `AsyncSurreal("ws://127.0.0.1:8000/rpc")` [Source: coretext/cli/commands.py].

### Technical Specifics
*   **Library:** `fastapi[standard]` (which includes `uvicorn`).
*   **Type Hinting:** Use Python 3.10+ style (e.g., `dict[str, str]`).
*   **Error Handling:** Use `fastapi.HTTPException`.

## Project Context Reference
*   `docs/architecture.md`
*   `docs/prd.md`
*   `docs/epics.md`
*   `coretext/cli/commands.py` (Existing daemon management logic)

## Dev Agent Record

### Context Reference
- docs/project_context.md
- docs/sprint-artifacts/sprint-status.yaml

### Agent Model Used
gemini-2.0-flash

### Completion Notes List
- Initialized story 2.1 draft.
- Configured health check requirements with localhost security.
- Outlined daemon integration tasks.
- Implemented FastAPI app scaffold and health check endpoint.
- Implemented MCP router stub logic.
- Updated CLI `start` and `stop` commands to manage FastAPI daemon.
- Added comprehensive unit and integration tests.

### File List
- docs/sprint-artifacts/2-1-mcp-server-setup-health-check.md
- docs/sprint-artifacts/sprint-status.yaml
- coretext/server/app.py
- coretext/server/health.py
- coretext/server/mcp/routes.py
- coretext/cli/commands.py
- tests/unit/server/test_health.py
- tests/unit/server/test_mcp.py
- tests/unit/cli/test_daemon_lifecycle.py
- tests/integration/server/test_story_2_1.py
