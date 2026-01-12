# CoreText User Guide: The Missing Context Layer

> **Target Audience:** Architects, Developers, and AI Agents using the `_coretext` knowledge base.

This guide is the definitive manual for operating CoreText in a production environment. It covers the full lifecycle—from initializing the knowledge graph to leveraging AI agents for complex architectural queries.

---

## 1. Core Concepts

CoreText is not just a search tool; it is a **Topological Knowledge Graph**. It understands that your project is a web of dependencies, not a bag of words.

*   **Nodes:** Files (`architecture.md`) and Headers (`## Service Layer`).
*   **Edges:** Relationships like `contains`, `parent_of`, and `references`.
*   **Hybrid Search:** Combines **Vector** (Meaning) + **Graph** (Structure) + **Lexical** (Keywords).

---

## 2. CLI Command Reference ("Outer Loop")

The CoreText CLI (`poetry run coretext`) provides a suite of tools for managing the knowledge graph lifecycle and integrity.

### 2.1. System Lifecycle
*   **`init`**:
    *   *Purpose:* Bootstraps the project. Downloads the SurrealDB binary, fetches the embedding model (nomic-embed-text-v1.5), and creates the `.coretext/config.yaml`.
    *   *Usage:* `poetry run coretext init`
*   **`start`**:
    *   *Purpose:* Launches the background daemon (SurrealDB on port 8010, MCP Server on port 8001). **Must be running for Agent features.**
    *   *Usage:* `poetry run coretext start`
*   **`stop`**:
    *   *Purpose:* Gracefully shuts down the daemon and database.
    *   *Usage:* `poetry run coretext stop`
*   **`status`**:
    *   *Purpose:* Displays a health dashboard. Shows server status, DB connection, and sync hook activity.
    *   *Usage:* `poetry run coretext status`
*   **`ping`**:
    *   *Purpose:* Simple connectivity check. Returns "pong".
    *   *Usage:* `poetry run coretext ping`

### 2.2. Graph Management & Synchronization
*   **`sync`**:
    *   *Purpose:* Manually triggers the indexing process for a directory. Parses Markdown files into graph nodes and vectors.
    *   *Usage:* `poetry run coretext sync --dir _coretext`
*   **`install-hooks`**:
    *   *Purpose:* Installs Git hooks (`pre-commit`, `post-commit`) to automate synchronization on every commit.
    *   *Usage:* `poetry run coretext install-hooks`
*   **`apply-schema`**:
    *   *Purpose:* Force-applies the graph schema defined in `.coretext/schema_map.yaml` to the database.
    *   *Usage:* `poetry run coretext apply-schema`
*   **`wipe`**:
    *   *Purpose:* DANGEROUS. Clears all data from the local graph database.
    *   *Usage:* `poetry run coretext wipe --force`

### 2.3. Quality Assurance & Content Creation
*   **`lint`**:
    *   *Purpose:* Scans Markdown files for broken links and dangling references. Enforces "Referential Integrity".
    *   *Usage:* `poetry run coretext lint` (or pass specific files)
*   **`new`**:
    *   *Purpose:* Generates new documents from standardized BMAD templates (e.g., Stories, Epics).
    *   *Usage:* `poetry run coretext new story _coretext/my-story.md`
    *   *List Templates:* `poetry run coretext new --list`

### 2.4. Exploration & Analysis
*   **`inspect`**:
    *   *Purpose:* Visualizes the dependency tree of a specific file or node in the terminal.
    *   *Usage:* `poetry run coretext inspect "node:_coretext/planning-artifacts/architecture.md" --depth 2`
*   **`query`**:
    *   *Purpose:* Performs a powerful **Hybrid Search** (Vector + Graph + Regex) directly from the CLI.
    *   *Usage:* `poetry run coretext query "Hybrid Search" --regex "(?i)surrealdb" --depth 1`

### 2.5. Integration
*   **`adapter`**:
    *   *Purpose:* Starts the MCP Stdio Adapter. This bridges standard input/output JSON-RPC messages to the local HTTP daemon, enabling integration with tools like the Gemini CLI.
    *   *Usage:* Internal use by Gemini extension.

---

## 3. Gemini CLI Extension ("Inner Loop")

This is where CoreText shines. By connecting an MCP-compliant agent (like Gemini CLI), you unlock "Thick Tools" that allow the AI to traverse your project's structure.

### 3.1. How it Works
The extension links the `gemini` command to your local CoreText installation. It registers:
1.  **Commands:** Wrappers for CLI tools (e.g., `gemini coretext status` calls `poetry run coretext status`).
2.  **MCP Server:** A bridge that exposes "Thick Tools" (`search_topology`, `query_knowledge`) to the LLM.

### 3.2. Setup
1.  **Ensure Daemon is Running:** `poetry run coretext start`
2.  **Link Extension:** `gemini extensions link .`
3.  **Verify:** `gemini mcp list` (Should show `Connected`).

### 3.3. Available MCP Tools (The "Inner Loop")
These tools are designed for high-precision context retrieval. They run on the daemon to leverage cached embeddings and persistent DB connections.

*   **`search_topology` (Semantic Search)**
    *   *Function:* Performs cosine similarity search on vector embeddings to find "Anchor Nodes".
    *   *Parameters:* `query` (text), `limit` (int).
    *   *Use Case:* "Find documentation related to Hybrid Find." -> Agent finds `_coretext/implementation-artifacts/5-3-hybrid-execution-thick-tool.md` even if the word "Find" isn't explicitly used.

*   **`get_dependencies` (Structural Analysis)**
    *   *Function:* Retrieves direct and indirect dependencies for a specific node ID. It can traverse both upstream (`in`) and downstream (`out`) edges.
    *   *Parameters:* `node_identifier` (str), `depth` (int).
    *   *Use Case:* "What files depend on the Architecture spec?" -> Agent lists all Stories and Epics that link *to* the architecture document.

*   **`query_knowledge` (The "Thick Tool")**
    *   *Function:* A universal context retrieval engine. It executes a complex pipeline in a single round-trip:
        1.  **Vector Search:** Finds top-k anchor nodes based on `natural_query`.
        2.  **Filtering:** Applies `regex_filter` (matches ID/Content) and `keyword_filter` (must contain string) to prune results.
        3.  **Graph Traversal:** Explores `depth` levels of connections (outgoing dependencies, incoming parents) from the surviving anchors.
    *   *Parameters:*
        *   `natural_query`: The semantic intent (e.g., "rate limiting logic").
        *   `top_k`: Number of initial anchors (default 5).
        *   `depth`: How far to traverse the graph (default 1).
        *   `regex_filter`: Regex pattern to scope search (e.g., `^/implementation-artifacts/.*`).
        *   `keyword_filter`: Exact substring match requirement.
    *   *Use Case:* "Summarize acceptance criteria for all 'Initialization' stories in the planning folder." -> Agent fetches a specific sub-graph containing only relevant headers and their content, filtering out noise.

---

## 4. Visualizing the Graph (Surrealist)

Sometimes you need to *see* the complexity to understand it. Surrealist allows both visual exploration and advanced SQL querying.

### 4.1. Visual Exploration
1.  **Launch Surrealist** (Desktop or Web).
2.  **Connect:** `ws://localhost:8010/rpc` (NS: `coretext`, DB: `coretext`, Auth: Anonymous).
3.  **Table View:**
    *   Search for a node ID (e.g., `node:⟨_coretext/planning-artifacts/architecture.md⟩`).
    *   **Inspect:** Click on a node to see its metadata, commit hash, and embedding vector.

### 4.2. Advanced SQL Analysis
Use the **SQL Console** in Surrealist to audit your graph.

**Query 1: Find "Orphaned" Specs**
Identify documentation that isn't linked to anything (potential dead knowledge).
```sql
SELECT * FROM node 
WHERE 
    node_type = 'file' 
    AND count(->references) = 0 
    AND count(<-references) = 0;
```

**Query 2: Analyze Impact (Incoming Dependencies)**
See everything that links *to* your Architecture document.
```sql
SELECT 
    id, 
    <-references<-node.path as referenced_by 
FROM node:⟨_coretext/planning-artifacts/architecture.md⟩;
```

**Query 3: Hybrid Search (Manual Vector Query)**
Simulate the vector math the Agent uses.
*Note:* The **CoreText Daemon** (Python) handles converting text to vectors. Since Surrealist connects directly to the **Database**, it cannot generate new embeddings from text on the fly. You must "borrow" an existing vector to test the similarity search.

```sql
-- 1. Grab the "Concept" vector of a known file
LET $concept = (SELECT embedding FROM node WHERE path = '_coretext/planning-artifacts/epics.md')[0].embedding;

-- 2. Find semantically related headers
SELECT 
    path, 
    content, 
    vector::similarity::cosine(embedding, $concept) AS relevance 
FROM node 
WHERE 
    node_type = 'header' 
    AND embedding != NONE 
ORDER BY relevance DESC 
LIMIT 5;
```

---

## 5. User Scenarios (The "Journeys")

### Scenario A: The Architect ("Structuring Chaos")
**Goal:** Define a new system component and ensure it links to existing architecture.

1.  **Create:** `poetry run coretext new story _coretext/planning-artifacts/story-new-feature.md`
2.  **Link:** Edit the file to add `[Architecture Reference](../architecture.md)`.
3.  **Validate:** Run `poetry run coretext lint`. If you made a typo in the link, it fails immediately.
4.  **Commit:** `git commit`. The hook runs `sync` automatically.
5.  **Verify:** `poetry run coretext inspect _coretext/planning-artifacts/story-new-feature.md` confirms the link to `architecture.md` exists in the graph.

### Scenario B: The AI Agent ("Context Pull")
**Goal:** Implement a feature without manually reading 50 files.

1.  **Prompt:** "I need to implement the 'Rate Limiting' feature. Use `query_knowledge` to find the requirements."
2.  **Agent Action:** Calls `query_knowledge(natural_query="rate limiting", regex_filter=".*planning.*")`.
3.  **Result:** The Agent receives the specific Story node and its constraints. It *doesn't* get the whole repo context window.
4.  **Prompt:** "What architectural patterns must I follow?"
5.  **Agent Action:** Calls `get_dependencies` on the Story node to find the linked `architecture.md` and reads the specific "Patterns" section.

### Scenario C: The Contributor ("Flow State")
**Goal:** Update a task status without context switching.

1.  **Action:** Edit `_coretext/planning-artifacts/epics.md` and mark `[x] Task 1`.
2.  **Action:** `git commit -m "Complete Task 1"`.
3.  **Result:** The sync hook updates the graph. The "Epic" node in the DB now reflects the progress. Project managers querying the graph see real-time status.

---

## 6. Troubleshooting & Resilience

*   **"Sync failed on commit":** CoreText has a **Fail-Open Policy**. If the daemon crashes or sync fails, your commit *will still proceed*. Check `.coretext/coretext.log` for errors.
*   **"Graph seems empty":** Run `poetry run coretext status`. If the daemon stopped, run `start` and then `sync --dir _coretext`.
*   **"Latency is high":** The daemon limits memory usage. If your repo is massive (>10k files), sync switches to "Async Mode" automatically to avoid blocking your terminal.