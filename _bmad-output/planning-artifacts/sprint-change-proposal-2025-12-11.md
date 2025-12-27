# Sprint Change Proposal - Daemon Startup Logic

**Date:** 2025-12-11
**Trigger:** Review of Story 1.2 Implementation

## 1. Issue Summary
During the review of Story 1.2, it was identified that the `coretext init` command downloads the SurrealDB binary but fails to start the process or prompt the user to do so. Furthermore, the `coretext start` command, which is necessary for launching the daemon, is missing from the CLI (`--help` checks confirm its absence).

## 2. Impact Analysis
*   **Story 1.2 (SurrealDB Management):** Incomplete. Users have the binary but no easy way to run the DB, blocking further development/verification.
*   **Story 3.1 (CLI for init/daemon):** The `start` command requirement from this story needs to be pulled forward or implemented immediately to satisfy the usability needs of Story 1.2.
*   **UX:** Poor developer experience; "init" feels broken if the system isn't running afterwards.

## 3. Recommended Approach
**Direct Adjustment:**
1.  **Modify Story 1.2:** Explicitly require `coretext init` to prompt the user to start the daemon upon successful download.
2.  **Accelerate Implementation:** Implement the `coretext start` command in `cli/commands.py` immediately (pulling from Story 3.1 scope if needed) to support the `init` workflow.

## 4. Detailed Change Proposals

### Artifact: `docs/epics.md`

**Story 1.2: SurrealDB Management & Schema Application**

**Section:** Acceptance Criteria

**OLD:**
```markdown
* Given the `coretext` project is initialized
* When `coretext init` is executed
* Then the platform-specific `surreal` binary is downloaded to `~/.coretext/bin/`.
* And a `surreal.db` file is created or found in `.coretext/`.
* And on daemon startup, the SurrealDB schema (defined by Pydantic models mapped via `schema_map.yaml`) is automatically applied.
```

**NEW:**
```markdown
* Given the `coretext` project is initialized
* When `coretext init` is executed
* Then the platform-specific `surreal` binary is downloaded to `~/.coretext/bin/`.
* And a `surreal.db` file is created or found in `.coretext/`.
* And the user is prompted to start the daemon immediately ("Do you want to start the coretext daemon now? [Y/n]").
* And on daemon startup, the SurrealDB schema (defined by Pydantic models mapped via `schema_map.yaml`) is automatically applied.
```

## 5. Implementation Handoff
*   **Scope:** Minor (Direct implementation fix)
*   **Recipient:** Development Team
*   **Action:**
    1.  Update `coretext/cli/commands.py`:
        *   Add `start` command (using `subprocess` for detached mode).
        *   Update `init` command to ask user and call `start` logic if "Y".
