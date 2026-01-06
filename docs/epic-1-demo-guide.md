# Epic 1 Demo Guide: Core Knowledge Graph Foundation

**Objective:** Verify the end-to-end functionality of the `coretext` system, from initialization to Git synchronization and database verification.

**Prerequisites:**
*   Python 3.10+ installed
*   Git installed
*   `surreal` binary (will be downloaded during init, or ensure it's in your path)
*   Surrealist app (recommended for DB viewing) or `surreal sql` CLI

---

## Phase 1: System Initialization

**Goal:** Verify the system can bootstrap itself, install dependencies, and start the database daemon.

1.  **Clean Slate (Optional but Recommended):**
    *   If you have a previous installation, you might want to back it up or clear the `.coretext` folder to test fresh.
    *   `rm -rf .coretext` (⚠️ Warning: Deletes local DB)

2.  **Initialize Project:**
    *   Run the init command from the project root.
    ```bash
    poetry run coretext init
    ```
    *   **Verify:**
        *   SurrealDB binary is downloaded to `~/.coretext/bin/`.
        *   `.coretext/config.yaml` is created.
        *   `.coretext/surreal.db/` folder exists.
        *   `.coretext/daemon.pid` exists.

3.  **Check Status:**
    *   Run the status command (if implemented in Epic 1, otherwise check process).
    ```bash
    # Check if process is running
    ps aux | grep surreal
    ```
    *   **Verify:** You should see a `surreal start` process running.

---

## Phase 2: Git Hook Installation

**Goal:** Verify the Git hooks are correctly installed and protecting the repository.

1.  **Install Hooks:**
    ```bash
    poetry run coretext install-hooks
    ```
    *   **Verify:** Check `.git/hooks/pre-commit` and `.git/hooks/post-commit`. They should be symlinks or files pointing to `coretext` logic.

2.  **Dry-Run / Lint Test (Malformation Check):**
    *   Create a file with BROKEN markdown.
    ```bash
    echo "# Broken Header\n\n[Broken Link](./non-existent.md)" > broken_test.md
    git add broken_test.md
    git commit -m "Test broken link"
    ```
    *   **Verify:**
        *   **Commit should FAIL.**
        *   Error message should report "Dangling Reference" or similar parsing error.
    *   *Cleanup:* `rm broken_test.md` and `git reset`


---

## Phase 3: Synchronization & Persistence

**Goal:** Verify that valid Markdown changes are automatically synced to SurrealDB.

1.  **Create Valid Content:**
    *   Create a test file with a valid structure.
    ```bash
    echo "# Demo Epic 1\n\nThis is a verification of Epic 1." > demo_epic_1.md
    ```

2.  **Trigger Sync (Commit):**
    ```bash
    git add demo_epic_1.md
    git commit -m "Add demo file for Epic 1 verification"
    ```
    *   **Verify:**
        *   Commit should SUCCEED.
        *   Post-commit hook should run (might be silent if fast, or show "Syncing...").

3.  **Database Verification (The Truth):**
    *   Open Surrealist or use CLI to query the DB.
    *   **Connection:** `ws://localhost:8010/rpc` (Namespace: `coretext`, DB: `coretext`, Auth: `None`)

    *   **Query 1: Check File Node**
        ```sql
        SELECT * FROM node:⟨demo_epic_1.md⟩;
        ```
        *   *Expectation:* One record returned with `node_type: 'file'` and `path: 'demo_epic_1.md'`.

    *   **Query 2: Check Header Node**
        ```sql
        SELECT * FROM node WHERE node_type = 'header' AND path = 'demo_epic_1.md';
        ```
        *   *Expectation:* One record (the H1 header `Demo Epic 1`).

    *   **Query 3: Check Relationship (File -> Header)**
        ```sql
        SELECT * FROM contains WHERE in = node:⟨demo_epic_1.md⟩;
        ```
        *   *Expectation:* One edge connecting `node:⟨demo_epic_1.md⟩` to `node:⟨demo_epic_1.md#demo-epic-1⟩`.

---

## Phase 4: Updates & Referential Integrity

**Goal:** Verify the graph updates correctly when content changes.

1.  **Update Content:**
    *   Modify the file.
    ```bash
    echo "\n## Sub-section\nNew content here." >> demo_epic_1.md
    ```

2.  **Sync Update:**
    ```bash
    git add demo_epic_1.md
    git commit -m "Update demo file"
    ```

3.  **Verify Update:**
    *   **Query:**
        ```sql
        SELECT * FROM node WHERE node_type = 'header' AND path = 'demo_epic_1.md';
        ```
        *   *Expectation:* You should now see at least TWO header nodes (the original H1 and the new H2 "Sub-section") belonging to `demo_epic_1.md`.

4.  **Verify References (Links):**
    *   Add a link to another file.
    ```bash
    echo "\n[Link to Epics](docs/epics.md)" >> demo_epic_1.md
    git add demo_epic_1.md
    git commit -m "Add link for reference check"
    ```
    *   **Query:**
        ```sql
        SELECT * FROM references WHERE in = node:⟨demo_epic_1.md⟩;
        ```
        *   *Expectation:* One edge connecting `node:⟨demo_epic_1.md⟩` to `node:⟨docs/epics.md⟩`.

---

## Phase 5: Cleanup (Optional)

1.  **Stop Daemon:**
    ```bash
    poetry run coretext stop
    # OR kill the process manually if stop command isn't fully robust yet
    kill $(cat .coretext/daemon.pid)
    ```
    *   **Note:** Running `coretext stop` will also **pause** the Git hooks. Subsequent commits will not trigger synchronization or validation until `coretext start` is run again.

2.  **Remove Demo File:**
    ```bash
    git rm demo_epic_1.md
    git commit -m "Cleanup demo file"
    ```
