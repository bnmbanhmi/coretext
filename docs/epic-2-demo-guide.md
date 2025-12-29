# Epic 2 Demo Guide: AI Agent Context Retrieval

**Objective:** Verify the MCP server and semantic tools, enabling AI agents to retrieve topologically aware context from the knowledge graph.

**Prerequisites:**
* Epic 1 completed and verified.
* `coretext` daemon running (DB + FastAPI Server).
* `requests` and `rich` python packages installed.

---

## Phase 1: System Startup & Health

**Goal:** Verify the full system (SurrealDB + FastAPI) starts correctly.

1.  **Start the System:**
    ```bash
    poetry run coretext start
    ```
    *   **Verify:** 
        *   Output shows "CoreText daemon started" (DB on 8000).
        *   Output shows "FastAPI server started" (Port 8001).
        *   Output shows "Schema applied successfully".

2.  **Verify Health:**
    ```bash
    curl http://127.0.0.1:8001/health
    ```
    *   **Verify:** Returns `{"status": "OK"}`.

---

## Phase 2: Knowledge Graph Population (Sync)

**Goal:** Ensure the graph has data and embeddings for semantic search.

1.  **Create Demo Content:**
    ```bash
    echo "# Agent Context Retrieval\nThis epic focuses on MCP tools and semantic search." > demo_epic_2.md
    ```

2.  **Sync to Graph:**
    ```bash
    git add demo_epic_2.md
    git commit -m "Add Epic 2 demo content"
    ```
    *   **Verify:** The post-commit hook should run. You can verify the node exists in SurrealDB:
    ```bash
    # Using surreal sql CLI
    echo "SELECT id, node_type, array::len(embedding) FROM node WHERE path = 'demo_epic_2.md';" | surreal sql --endpoint http://localhost:8000 --ns coretext --db coretext --user root --pass root
    ```
    *   **Expectation:** At least one record with `embedding` length 768.

---

## Phase 3: MCP Tool Verification

**Goal:** Verify the AI Agent tools (Manifest, Search, Dependencies).

1.  **Fetch Manifest:**
    ```bash
    curl http://127.0.0.1:8001/mcp/manifest
    ```
    *   **Verify:** Returns a JSON list of tools including `search_topology` and `get_dependencies`.

2.  **Test Semantic Search (`search_topology`):**
    ```bash
    curl -X POST http://127.0.0.1:8001/mcp/tools/search_topology \
         -H "Content-Type: application/json" \
         -d '{"query": "Agent Context", "limit": 3}'
    ```
    *   **Verify:** Returns a list of relevant nodes. `demo_epic_2.md` should be at the top.

3.  **Test Dependency Retrieval (`get_dependencies`):**
    ```bash
    curl -X POST http://127.0.0.1:8001/mcp/tools/get_dependencies \
         -H "Content-Type: application/json" \
         -d '{"node_identifier": "file:demo_epic_2.md", "depth": 1}'
    ```
    *   **Verify:** Returns the structure of the file (e.g., its headers via `contains` relationship).

---

## Phase 4: Automated Demo Script

A helper script is provided to run all the above checks automatically.

1.  **Run the script:**
    ```bash
    python3 scripts/demo_epic_2.py
    ```
    *   **Verify:** The script prints a clean report of health, manifest, and tool outputs.

---

## Troubleshooting

*   **500 Internal Server Error:** Check if SurrealDB is running on port 8000 and the `.coretext/schema_map.yaml` exists.
*   **Empty Search Results:** Ensure the nodes have embeddings. Run `coretext apply-schema` and re-commit a file to trigger sync.
*   **Connection Refused:** Ensure the FastAPI server started on port 8001. Check `ps aux | grep uvicorn`.
