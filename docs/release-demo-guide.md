# CoreText Comprehensive Release Demo & Verification Guide

This guide provides a systematic walk-through of all CoreText features (Epics 1-4). Following these steps ensures the system is correctly initialized, synchronizes data accurately, empowers developers with CLI tools, and maintains performance and resilience.

---

## 1. System Initialization & Environment

**Goal:** Verify the system can bootstrap itself, install dependencies, and start the background services.

### 1.1. System Cleanup & Fresh Start
**Critical Step:** To ensure no data from previous demos interferes with this run (e.g., "ghost" nodes appearing in lint checks), strictly follow this cleanup:

1. **Stop the Daemon:**
   ```bash
   poetry run coretext stop
   ```

2. **Remove Persistence Layer & Artifacts:**
   ```bash
   # This removes the database, config, binary, AND any previous demo files
   rm -rf .coretext demo/
   ```
   *Tip: To keep the binary (skipping re-download) but reset data, use: `rm -rf .coretext/surreal.db .coretext/config.yaml demo/`*

### 1.2. Initialize Project
```bash
poetry run coretext init
```
**Verify:**
- SurrealDB binary downloaded to `~/.coretext/bin/`.
- `.coretext/config.yaml` created.
- `.coretext/surreal.db/` folder and `.coretext/daemon.pid` exist.

### 1.3. Check Daemon Status
```bash
poetry run coretext status
```
**Verify:**
- **Daemon:** Running (Green)
- **Port:** 8010 (DB) / 8001 (MCP)
- **Sync Hooks:** Active

│  Surrealist Auth:   None / Anonymous       │
│  Namespace / DB:    coretext / coretext    │
╰────────────────────────────────────────────╯

### 1.4. Scoped Configuration (Directory Selection)
**Goal:** Verify CoreText can be scoped to a specific directory, ignoring irrelevant files.

1. **Create Scoped Directories:**
   ```bash
   mkdir -p docs_only/inner
   echo "# Target Document" > docs_only/inner/target.md
   echo "# Ignored Document" > ignored_at_root.md
   ```

2. **Update Configuration:**
   Edit `.coretext/config.yaml` to set `docs_dir: "docs_only"`.

3. **Verify Scoped Sync:**
   ```bash
   poetry run coretext sync
   ```
   **Verify:** Output should show "Using configured docs directory: .../docs_only" and sync only the files within that directory.

4. **Database Verification:**
   ```bash
   echo "SELECT path FROM node WHERE node_type = 'file';" | ~/.coretext/bin/surreal sql --endpoint http://localhost:8010 --ns coretext --db coretext
   ```
   **Verify:** `docs_only/inner/target.md` should be present, but `ignored_at_root.md` should **not**.

---

## 2. Content Authoring & Templates

**Goal:** Verify we can create standard BMAD documents using templates.

### 2.1. Create a New Document
We will use a dedicated `demo/` folder to keep our demo artifacts separate from the rest of the project.
```bash
poetry run coretext new story demo/demo-story.md
```
**Verify:**
- `demo/demo-story.md` created with standard Story template structure.

### 2.2. List Available Templates
```bash
poetry run coretext new
```
**Verify:** Lists `prd`, `architecture`, `epic`, `story`.

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
# Lints the entire demo folder recursively
poetry run coretext lint demo/
```
**Verify:** Reports **1 Issue** (Broken Link) in `demo/demo-story.md`. (Note: This avoids noise from technical debt in other parts of the repository).

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
Remove the broken link and commit:
```bash
# Revert the broken line
head -n -1 demo/demo-story.md > demo/demo-story.tmp && mv demo/demo-story.tmp demo/demo-story.md
git add demo/demo-story.md
git commit -m "Add valid demo story"
```
**Verify:** **Commit SUCCEEDS.** Post-commit hook triggers sync.

### 4.2. Database Verification (The Truth)

You can verify the data using the CLI or the **Surrealist** app (recommended for visual inspection).

**Option A: CLI Check**
```bash
echo "SELECT id, node_type, path FROM node WHERE path = 'demo/demo-story.md';" | surreal sql --endpoint http://localhost:8010 --ns coretext --db coretext
```
**Expectation:** At least two records (file node and the H1 header node).

**Option B: Surrealist App**
1. Open Surrealist (or web version) and connect to: `ws://localhost:8010/rpc`
   - **Namespace:** `coretext`
   - **Database:** `coretext`
   - **Auth Mode:** `None` / `Anonymous`

2. **Query 1: Check File Node**
   ```sql
   SELECT * FROM node WHERE path = 'demo/demo-story.md';
   ```
   **Expectation:** One record with `node_type: 'file'`.

3. **Query 2: Check Header Node**
   ```sql
   SELECT * FROM node WHERE node_type = 'header' AND path = 'demo/demo-story.md';
   ```
   **Expectation:** Records for the headers (e.g., H1 "Demo Story").

4. **Query 3: Check Relationship**
   ```sql
   SELECT * FROM contains WHERE in = (SELECT id FROM node WHERE path = 'demo/demo-story.md');
   ```
   **Expectation:** Edges connecting the file node to its header nodes.

**Option C: Advanced Hybrid Retrieval (The Real Power)**
This step verifies the **Hybrid Search** architecture (Vector + Lexical + Graph). We will find nodes *semantically similar* to the file we just created, but *structurally filtered* to only show Headers.

1. **Run this Hybrid Query in Surrealist:**
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
       -- Graph/Lexical Constraint: Only look at Headers
       node_type = 'header' 
       -- Data Integrity: Ensure they have vectors
       AND embedding != NONE 
   -- Semantic Ranking
   ORDER BY relevance DESC 
   LIMIT 5;
   ```
   **Expectation:** You should see header nodes (likely the file's own headers or other semantically related headers in the graph) ranked by relevance. This proves the **Vector Store** and **Graph Store** are unified.

---

## 5. Graph Inspection & Visualization

**Goal:** Verify we can visualize the graph topology from the CLI.

### 5.1. Inspect Node
```bash
poetry run coretext inspect demo/demo-story.md
```
**Verify:** Displays a **Tree View** showing the file as root and its sections as branches.

---

## 6. AI Agent Integration (MCP)

**Goal:** Verify the MCP server enabling AI agents to retrieve context.

### 6.1. Health Check
```bash
curl http://127.0.0.1:8001/health
```
**Verify:** Returns `{"status": "OK"}`.

### 6.2. Semantic Search
```bash
curl -X POST http://127.0.0.1:8001/mcp/tools/search_topology \
     -H "Content-Type: application/json" \
     -d '{"query": "User Story", "limit": 3}'
```
**Verify:** Returns relevant nodes. `demo/demo-story.md` should be present.

### 6.3. Dependency Retrieval
```bash
curl -X POST http://127.0.0.1:8001/mcp/tools/get_dependencies \
     -H "Content-Type: application/json" \
     -d '{"node_identifier": "file:demo/demo-story.md", "depth": 1}'
```
**Verify:** Returns JSON structure of the file dependencies.

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
