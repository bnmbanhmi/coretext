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
    *   **Connection:** `ws://localhost:8000/rpc` (Namespace: `coretext`, DB: `coretext`, User/Pass: `root`/`root`)

    *   **Query 1: Check File Node**
        ```sql
        SELECT * FROM file WHERE id = 'demo_epic_1.md';
        ```
        *   *Expectation:* One record returned with `path: 'demo_epic_1.md'`.

    *   **Query 2: Check Header Node**
        ```sql
        SELECT * FROM header WHERE content CONTAINS 'Demo Epic 1';
        ```
        *   *Expectation:* One record (the H1 header).

    *   **Query 3: Check Relationship (File -> Header)**
        ```sql
        SELECT * FROM contains WHERE in = file:`demo_epic_1.md`;
        ```
        *   *Expectation:* One edge connecting the file to the header.

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
        SELECT * FROM header WHERE id CONTAINS 'demo_epic_1.md';
        ```
        *   *Expectation:* Now you should see TWO headers (the original H1 and the new H2 "Sub-section").

---

## Phase 5: Cleanup (Optional)

1.  **Stop Daemon:**
    ```bash
    poetry run coretext stop
    # OR kill the process manually if stop command isn't fully robust yet
    kill $(cat .coretext/daemon.pid)
    ```

2.  **Remove Demo File:**
    ```bash
    git rm demo_epic_1.md
    git commit -m "Cleanup demo file"
    ```
