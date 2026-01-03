# Epic 3 Demo Guide: Developer Workflow Tools

**Objective:** Verify the developer CLI tools (`init`, `status`, `new`, `lint`, `inspect`) that empower users to manage the knowledge graph.

**Prerequisites:**
* Epic 1 & 2 verified (System is runnable).
* `coretext` daemon is NOT running (we will start it).

---

## Phase 1: Initialization & Status

**Goal:** Verify `init` sets up the environment and `status` reports correctly.

1.  **Ensure Clean State (Daemon Stopped):**
    ```bash
    poetry run coretext stop
    ```

2.  **Run Init (Idempotency Check):**
    *   Even if already initialized, this should be safe to run again.
    ```bash
    poetry run coretext init
    ```
    *   **Verify:**
        *   Checks for binaries/models (should skip if present).
        *   Ensures config exists.
        *   Prompts to start daemon (Say "y" or run `start` manually).

3.  **Check Status:**
    ```bash
    poetry run coretext status
    ```
    *   **Verify:**
        *   **Daemon:** Running (Green)
        *   **Port:** 8000 (DB) / 8001 (MCP)
        *   **Sync Hooks:** Active

---

## Phase 2: Template Provisioning (`new`)

**Goal:** Verify we can easily create standard BMAD documents.

1.  **Create a New Story:**
    ```bash
    poetry run coretext new story docs/demo-story-3-6.md
    ```
    *   **Verify:**
        *   File `docs/demo-story-3-6.md` is created.
        *   Content contains the standard Story template structure.

2.  **List Templates:**
    ```bash
    poetry run coretext new
    ```
    *   **Verify:** Lists `prd`, `architecture`, `epic`, `story`.

---

## Phase 3: Linting (`lint`)

**Goal:** Verify the linter catches issues *before* we commit.

1.  **Run Lint on Valid File:**
    ```bash
    poetry run coretext lint
    ```
    *   **Verify:** "No issues found" (assuming clean repo).

2.  **Introduce an Error:**
    *   Edit `docs/demo-story-3-6.md` to add a broken link.
    ```bash
    echo "\n[Broken Link](./does-not-exist.md)" >> docs/demo-story-3-6.md
    ```

3.  **Run Lint Again:**
    ```bash
    poetry run coretext lint
    ```
    *   **Verify:**
        *   Reports **1 Issue**.
        *   File: `docs/demo-story-3-6.md`
        *   Type: **Broken Link** (or Reference Error)

---

## Phase 4: Sync & Inspection (`inspect`)

**Goal:** Verify we can visualize the graph topology.

1.  **Commit the File (Trigger Sync):**
    *   *Note: Sync might fail or warn on the broken link depending on configuration, but let's fix it first for a clean graph.*
    *   Remove the broken link.
    ```bash
    # Revert the broken line
    head -n -1 docs/demo-story-3-6.md > docs/demo-story-3-6.tmp && mv docs/demo-story-3-6.tmp docs/demo-story-3-6.md
    ```
    *   Commit:
    ```bash
    git add docs/demo-story-3-6.md
    git commit -m "Add demo story for Epic 3"
    ```

2.  **Inspect the Node:**
    ```bash
    poetry run coretext inspect docs/demo-story-3-6.md
    ```
    *   **Verify:**
        *   Displays a **Tree View**.
        *   **Root:** `demo-story-3-6.md`
        *   **Branches:** `Contains` (showing headers like "Story", "Acceptance Criteria").

---

## Phase 5: Cleanup

1.  **Remove Demo File:**
    ```bash
    git rm docs/demo-story-3-6.md
    git commit -m "Cleanup Epic 3 demo"
    ```
