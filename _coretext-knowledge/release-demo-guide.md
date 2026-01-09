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
- `.coretext/config.yaml` created with `docs_dir: _coretext-knowledge`.
- `_coretext-knowledge` folder created if missing.
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
**Goal:** Verify CoreText is scoped to the isolated directory `_coretext-knowledge`.

1. **Check Configuration:**
   Verify `.coretext/config.yaml` has `docs_dir: _coretext-knowledge`.

2. **Verify Scoped Sync:**
   ```bash
   poetry run coretext sync
   ```
   **Verify:** Output should show "Using configured docs directory: .../_coretext-knowledge" and sync only the files within that directory.

3. **Database Verification:**
   ```bash
   echo "SELECT path FROM node WHERE node_type = 'file';" | ~/.coretext/bin/surreal sql --endpoint http://localhost:8010 --ns coretext --db coretext
   ```
   **Verify:** Only files inside `_coretext-knowledge` should be present.

---

## 2. Content Authoring & Templates

**Goal:** Verify we can create standard BMAD documents using templates.

### 2.1. Create a New Document
We will use the `_coretext-knowledge` folder to keep our graph clean.
```bash
poetry run coretext new story _coretext-knowledge/demo-story.md
```
**Verify:**
- `_coretext-knowledge/demo-story.md` created with standard Story template structure.

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
Edit `_coretext-knowledge/demo-story.md` to add a broken link:
```bash
echo "\n[Broken Link](./does-not-exist.md)" >> _coretext-knowledge/demo-story.md
```

### 3.3. Run Linter
```bash
# Lints the knowledge folder recursively
poetry run coretext lint _coretext-knowledge/
```
**Verify:** Reports **1 Issue** (Broken Link) in `_coretext-knowledge/demo-story.md`.

### 3.4. Pre-commit Protection
Attempt to commit the broken file:
```bash
git add _coretext-knowledge/demo-story.md
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
    echo "# Reference Target\nThis file is referenced by the story." > _coretext-knowledge/reference-target.md
    ```

2.  **Fix the link in the story:**
    ```bash
    # Fix the link to point to reference-target.md
    sed -i '' 's|\[Broken Link\](\./does-not-exist\.md)|[Valid Link](./reference-target.md)|' _coretext-knowledge/demo-story.md
    
    # Verify content
    cat _coretext-knowledge/demo-story.md
    
    # Commit both files
    git add _coretext-knowledge/demo-story.md _coretext-knowledge/reference-target.md
    git commit -m "Add valid demo story with link to target"
    ```
**Verify:** **Commit SUCCEEDS.** Post-commit hook triggers sync.

### 4.2. Database Verification (The Truth)

You can verify the data using the CLI or the **Surrealist** app (recommended for visual inspection).

**Option A: CLI Check**
```bash
echo "SELECT id, node_type, path FROM node WHERE path = '_coretext-knowledge/demo-story.md';" | surreal sql --endpoint http://localhost:8010 --ns coretext --db coretext
```
**Expectation:** At least two records (file node and the H1 header node).

**Option B: Surrealist App (Data View)**
1. Open Surrealist (or web version) and connect to: `ws://localhost:8010/rpc`
   - **Namespace:** `coretext`
   - **Database:** `coretext`
   - **Auth Mode:** `None` / `Anonymous`

2. **Query 1: Check File Node**
   ```sql
   SELECT * FROM node WHERE path = '_coretext-knowledge/demo-story.md';
   ```
   **Expectation:** One record with `node_type: 'file'`.

3. **Query 2: Check Header Node & Hierarchy (parent_of)**
   ```sql
   SELECT 
       id, 
       title, 
       <-parent_of<-node.title AS parent_doc 
   FROM node 
   WHERE node_type = 'header' AND path = '_coretext-knowledge/demo-story.md';
   ```
   **Expectation:** Header nodes showing they are children (`parent_of` incoming) of the File node.

4. **Query 3: Check References (Valid Link)**
   ```sql
   SELECT 
       out.path as target_file, 
       out.node_type as target_type 
   FROM references 
   WHERE in.path = '_coretext-knowledge/demo-story.md';
   ```
   **Expectation:** One record where `target_file` is `_coretext-knowledge/reference-target.md`.

**Option C: Surrealist Graph Visualization**
1. Switch to the **Designer** or **Graph** view in Surrealist.
2. Search for the node `_coretext-knowledge/demo-story.md`.
3. Double-click to expand relationships.
   - **Verify:** You see lines connecting to:
     - **Header Nodes** (via `contains` or `parent_of` edges).
     - **reference-target.md** (via `references` edge).
   - This visual confirmation proves the graph topology is intact.

**Option D: Advanced Hybrid Retrieval (The Real Power)**
This step verifies the **Hybrid Search** architecture (Vector + Lexical + Graph). We will find nodes *semantically similar* to the file we just created, but *structurally filtered* to only show Headers.

1. **Run this Hybrid Query in Surrealist:**
   ```sql
   -- 1. Grab the "Concept" (Vector) of our new story
   LET $concept = (SELECT embedding FROM node WHERE path = '_coretext-knowledge/demo-story.md')[0].embedding;

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
poetry run coretext inspect _coretext-knowledge/demo-story.md
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
     -d '{"natural_query": "User Story", "limit": 3}'
```
**Verify:** Returns relevant nodes. `_coretext-knowledge/demo-story.md` should be present.

### 6.3. Dependency Retrieval
```bash
curl -X POST http://127.0.0.1:8001/mcp/tools/get_dependencies \
     -H "Content-Type: application/json" \
     -d '{"node_identifier": "file:_coretext-knowledge/demo-story.md", "depth": 1}'
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
1. Delete `_coretext-knowledge/demo-story.md` manually.
2. Run `git commit` (e.g., on a different file) or `coretext sync`.
3. Check DB: `SELECT count() FROM node WHERE path = '_coretext-knowledge/demo-story.md' `.
**Verify:** Node is automatically removed from graph.

---

## 8. Cleanup

Remove knowledge files and stop daemon:
```bash
git rm _coretext-knowledge/demo-story.md
rmdir _coretext-knowledge
git commit -m "Cleanup demo files"
poetry run coretext stop
```
