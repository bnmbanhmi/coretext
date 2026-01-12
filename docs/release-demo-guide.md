# CoreText Comprehensive Release Demo & Verification Guide

This guide provides a systematic walk-through of all CoreText features (Epics 1-4). Following these steps ensures the system is correctly initialized, synchronizes data accurately, empowers developers with CLI tools, and maintains performance and resilience.

---

## 1. System Initialization & Environment

**Goal:** Verify the system can bootstrap itself and be configured to scope a specific directory (e.g., `demo/`).

### 1.1. System Cleanup & Fresh Start
**Critical Step:** To ensure no data from previous demos interferes with this run:

1. **Stop the Daemon:**
   ```bash
   poetry run coretext stop
   ```

2. **Remove Persistence Layer & Artifacts:**
   ```bash
   rm -rf .coretext demo/
   ```

### 1.2. Initialize Project (Configuring Scope)
We will configure CoreText to **only** track files inside a `demo` folder, ignoring the rest of the repository.

```bash
poetry run coretext init
```
**Interactive Prompt:**
- **"Where are your documents located?"**: Enter `demo`.
- **"Directory 'demo' does not exist. Create it?"**: Enter `y`.
- **"Start daemon?"**: Enter `y`.

**Verify:**
- Check `.coretext/config.yaml`: It should contain `docs_dir: demo`.

### 1.3. Manual Schema Application
Verify the schema management tool can force-apply the graph schema to SurrealDB.

```bash
poetry run coretext apply-schema
```
**Verify:** Output should indicate `Schema applied successfully`.

### 1.4. Check Daemon Status
```bash
poetry run coretext status
```
**Verify:**
- **Daemon:** Running (Green)
- **Port:** 8010 (DB) / 8001 (MCP)
- **Sync Hooks:** Active

### 1.4. Verify Scoping
**Goal:** specific verify that CoreText ignores files outside the configured `demo` directory.

1. **Create Test Files:**
   ```bash
   # File INSIDE the scoped folder (Should be Synced)
   echo "# Inside Scope" > demo/inside.md
   
   # File OUTSIDE the scoped folder (Should be Ignored)
   echo "# Outside Scope" > root_ignored.md
   ```

2. **Trigger Sync:**
   ```bash
   poetry run coretext sync
   ```
   **Verify:** Output mentions syncing `demo/inside.md` but makes NO mention of `root_ignored.md`.

3. **Database Verification:**
   ```bash
   echo "SELECT path FROM node WHERE node_type = 'file';" | ~/.coretext/bin/surreal sql --endpoint http://localhost:8010 --ns coretext --db coretext
   ```
   **Verify:** 
   - ✅ `demo/inside.md` is present.
   - ❌ `root_ignored.md` is **NOT** present.

4. **Cleanup Root File:**
   ```bash
   rm root_ignored.md
   ```

---

## 2. Content Authoring & Templates

**Goal:** Verify we can create standard BMAD documents using templates.

### 2.1. Create a New Document
```bash
poetry run coretext new story demo/demo-story.md
```
**Verify:**
- `demo/demo-story.md` created with standard Story template structure.

### 2.2. List Available Templates
```bash
poetry run coretext new --list
```
**Verify:** Displays a table listing `architecture`, `epic`, `prd`, `story`.

---

## 3. Validation & Quality (Linter)

**Goal:** Verify the linter catches malformed content and dangling references.

### 3.1. Install Git Hooks
```bash
poetry run coretext install-hooks
```

### 3.2. Introduce a Validation Error
Edit `demo/demo-story.md` to add a broken link:
```bash
echo "\n[Broken Link](./does-not-exist.md)" >> demo/demo-story.md
```

### 3.3. Run Linter
```bash
# Lints the configured knowledge folder
poetry run coretext lint
```
**Verify:** Reports **1 Issue** (Broken Link) in `demo/demo-story.md`.

### 3.4. Pre-commit Protection
Attempt to commit the broken file:
```bash
git add demo/demo-story.md
git commit -m "This commit should fail"
```
**Verify:** **Commit FAILs.** Error message reports the broken link.

---

## 4. Synchronization & Persistence

**Goal:** Verify valid changes are synced to SurrealDB.

### 4.1. Fix and Sync
Fix the broken link by pointing it to a valid file.

1.  **Create a target file:**
    ```bash
    echo "# Reference Target\nThis file is referenced by the story." > demo/reference-target.md
    ```

2.  **Fix the link in the story:**
    ```bash
    # Fix the link to point to reference-target.md
    sed -i '' 's|\[Broken Link\](\./does-not-exist\.md)|[Valid Link](./reference-target.md)|' demo/demo-story.md
    
    # Verify content
    cat demo/demo-story.md
    
    # Commit both files
    git add demo/demo-story.md demo/reference-target.md
    git commit -m "Add valid demo story with link to target"
    ```
**Verify:** **Commit SUCCEEDS.** Post-commit hook triggers sync.

### 4.2. Database Verification (The Truth)

You can verify the data using the CLI or the **Surrealist** app (recommended for visual inspection).

**Option A: CLI Check**
```bash
echo "SELECT id, node_type, path FROM node WHERE path = 'demo/demo-story.md';" | surreal sql --endpoint http://localhost:8010 --ns coretext --db coretext
```
**Expectation:** At least two records (file node and the H1 header node).

**Option B: Surrealist App (Data View)**
1. Open Surrealist (or web version) and connect to: `ws://localhost:8010/rpc`
   - **Namespace:** `coretext`
   - **Database:** `coretext`
   - **Auth Mode:** `None` / `Anonymous`

2. **Query 1: Check File Node**
   ```sql
   SELECT * FROM node WHERE path = 'demo/demo-story.md';
   ```
   **Expectation:** One record with `node_type: 'file'`.

3. **Query 2: Check Header Node & Hierarchy (parent_of)**
   ```sql
   SELECT 
       id, 
       title, 
       <-parent_of<-node.title AS parent_doc 
   FROM node 
   WHERE node_type = 'header' AND path = 'demo/demo-story.md';
   ```
   **Expectation:** Header nodes showing they are children (`parent_of` incoming) of the File node.

4. **Query 3: Check References (Valid Link)**
   ```sql
   SELECT 
       out.path as target_file, 
       out.node_type as target_type 
   FROM references 
   WHERE in.path = 'demo/demo-story.md';
   ```
   **Expectation:** One record where `target_file` is `demo/reference-target.md`.

**Option C: Surrealist Graph Visualization**
1. Switch to the **Designer** or **Graph** view in Surrealist.
2. Search for the node `demo/demo-story.md`.
3. Double-click to expand relationships.
   - **Verify:** You see lines connecting to:
     - **Header Nodes** (via `contains` or `parent_of` edges).
     - **reference-target.md** (via `references` edge).
   - This visual confirmation proves the graph topology is intact.

**Option D: Advanced SQL Search (Under the Hood)**
This step verifies the **Unified Storage** architecture. We will find nodes *semantically similar* to the file we just created using raw SQL. Note that in Surrealist, we use an existing node's embedding as a "seed" because the SQL editor cannot embed text strings directly.

1. **Run this Query in Surrealist:**
   ```sql
   -- 1. Grab the "Concept" (Vector) of our new story
   LET $concept = (SELECT embedding FROM node WHERE path = 'demo/demo-story.md')[0].embedding;

   -- 2. Find related Headers (Vector Similarity + Type Filter)
   SELECT 
       path, 
       node_type, 
       vector::similarity::cosine(embedding, $concept) AS relevance 
   FROM node 
   WHERE 
       node_type = 'header' 
       AND embedding != NONE 
   ORDER BY relevance DESC 
   LIMIT 5;
   ```
   **Expectation:** You should see header nodes ranked by relevance. This proves the **Vector Store** and **Graph Store** are unified in SurrealDB.

---

## 5. Graph Inspection & Hybrid Querying

**Goal:** Verify we can visualize the graph and perform natural language hybrid searches from the CLI.

### 5.1. Inspect Node (Graph Structure)
```bash
poetry run coretext inspect demo/demo-story.md
```
**Verify:** Displays a **Tree View** showing the file as root and its sections as branches.

### 5.2. Hybrid Query (The "Thick Tool" in action)
Verify the combined Semantic + Lexical + Graph retrieval. This command is much more powerful than a simple search as it pulls a unified context.

```bash
# Natural Language + Regex Filter + Graph Traversal
poetry run coretext query "acceptance criteria for initialization" --regex ".*1-1.*" --depth 1
```
**Verify:** 
- Displays a table of relevant nodes with semantic scores.
- Summarizes the number of graph connections (edges) found during traversal.

---

## 6. AI Agent Integration (MCP)

**Goal:** Verify the MCP server enabling AI agents to retrieve context.

### 6.1. Health Check
```bash
curl http://127.0.0.1:8001/health
```
**Verify:** Returns `{"status": "OK"}`.

### 6.2. Exclusive MCP Tools (Semantic Retriever)

Verify the "Inner Loop" tools that enable Agent intelligence.

**A. search_topology (Semantic Search)**
```bash
curl -X POST http://127.0.0.1:8001/mcp/tools/search_topology \
     -H "Content-Type: application/json" \
     -d '{"query": "User Story", "limit": 3}'
```
**Verify:** Returns relevant nodes. `demo/demo-story.md` should be present.

**B. query_knowledge (The "Thick Tool")**
Verify the combined Semantic + Regex + Graph Traversal engine.
```bash
curl -X POST http://127.0.0.1:8001/mcp/tools/query_knowledge \
     -H "Content-Type: application/json" \
     -d '{
       "natural_query": "demo story",
       "top_k": 1,
       "depth": 1,
       "regex_filter": ".*demo.*"
     }'
```
**Verify:** Returns a JSON object with both `nodes` and `edges`. The edges should show the relationship between the file and its headers.

### 6.3. Gemini CLI Extension Demo

**Goal:** Verify the Gemini CLI agent can use the extension tools to query knowledge naturally.

1.  **Link the Extension:**
    ```bash
    gemini extensions link .
    ```

2.  **Verify Connection:**
    ```bash
    gemini mcp list
    ```
    **Verify:** `coretext` shows as **Connected**.

3.  **Start Gemini CLI:**
    ```bash
    gemini
    ```

4.  **Interact with the Agent:**
    *   **Scenario 1: Lifecycle & Health**
        *   **Prompt:** "What is the status of the CoreText system?"
        *   *Expectation:* The agent runs the `coretext status` command and reports the health.
    *   **Scenario 2: Semantic Research (search_topology)**
        *   **Prompt:** "Find any documents related to 'Story' using coretext search."
        *   *Expectation:* The agent uses the `search_topology` tool and lists relevant nodes.
    *   **Scenario 3: Complex Context Retrieval (query_knowledge)**
        *   **Prompt:** "Give me a detailed overview of the 'demo-story.md' file including its section structure and any files it references."
        *   *Expectation:* The agent uses `query_knowledge` with `depth=1` to pull the file node, its header nodes, and connected references in one step.
    *   **Scenario 4: Dependency Analysis (get_dependencies)**
        *   **Prompt:** "What does the 'demo-story.md' file depend on?"
        *   *Expectation:* The agent uses `get_dependencies` and identifies the link to `reference-target.md`.

---

## 7. Performance & Resilience

**Goal:** Verify handles scale, latency, and failures gracefully.

### 7.1. Latency Benchmark
```bash
python3 scripts/benchmark_latency.py
```
**Verify:** p95 latency < 500ms.

### 7.2. Fail-Open Policy
Simulate a sync failure:
```bash
python3 scripts/demo_epic_4.py --scenario fail-open
```
**Verify:** Script simulates a crash but exits with Code 0, ensuring Git workflow isn't blocked.

### 7.3. Self-Healing Graph
1. Delete `demo/demo-story.md` manually.
2. Run `git commit` (e.g., on a different file) or `coretext sync`.
3. Check DB: `SELECT count() FROM node WHERE path = 'demo/demo-story.md' `.
**Verify:** Node is automatically removed from graph.

---

## 8. Cleanup

Remove demo files and stop daemon:
```bash
git rm demo/demo-story.md
rmdir demo
git commit -m "Cleanup demo files"
poetry run coretext stop
```
