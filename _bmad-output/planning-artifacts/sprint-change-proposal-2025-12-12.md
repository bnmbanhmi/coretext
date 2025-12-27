# Sprint Change Proposal - 2025-12-12

**Author:** Product Manager (John)
**Date:** 2025-12-12
**Status:** Draft / Handover

## 1. Issue Summary

**Problem Statement:**
Critical failure in data persistence layer. Despite successful execution of the `sync.py` Git hook and "Synchronization COMPLETE" logs, no data is persisted to SurrealDB. Manual verification via `query_surreal.py` consistently returns `"Can not execute CREATE statement using value: NONE"`, indicating a fundamental mismatch between the application's data payload and SurrealDB's schema constraints or client behavior.

**Context:**
The issue was discovered during the demo phase of Story 1.4 (Git Repository Change Detection & Synchronization). While the infrastructure (Git hooks, async detachment, process management) is now robust, the core business value—storing knowledge in the graph—is blocked.

**Evidence:**
- `query_surreal.py` fails on `db.create` with `NONE` value error even when all Pydantic model fields are populated.
- Initial schema definition (`schema.py`) and Pydantic models (`models.py`) had mismatches (`file_path` vs `path`, missing `title`/`summary`).
- `AsyncSurreal` client interactions required specific handling for `RecordID` serialization and async context management.

## 2. Impact Analysis

**Story Impact:**
- **Story 1.4 (Git Sync):** Functionally incomplete. The "plumbing" works, but the "payload" is rejected. Status was prematurely marked "Done".
- **Epic 2 (Agent Context):** Blocked. Agents cannot retrieve context if the graph is empty.

**Technical Impact:**
- **Data Integrity:** Currently zero. No nodes or edges are being stored.
- **Client Stability:** The Python `surrealdb` client integration requires deeper validation against the specific SurrealDB version/configuration being used.

## 3. Recommended Approach

**Deep Diagnosis & Schema Refinement:**
We must pause feature development and focus solely on resolving the database interaction layer. The "Fail-Open" policy is working (commits aren't blocked), but the system is currently a "No-Op".

**Immediate Actions Required:**
1.  **Isolate the `NONE` Error:** Create a minimal reproduction script using *only* the `surrealdb` library and raw dictionary payloads (bypassing Pydantic) to rule out serialization issues.
2.  **Verify Schema Constraints:** Review the `schema.py` definition. The error likely stems from a `ASSERT $value != NONE` constraint on a field that is implicitly `NONE` during the `CREATE` operation.
3.  **Refactor `GraphManager`:** Ensure it aligns perfectly with the verified working raw query pattern.

## 4. Detailed Changes & Fixes Applied (Retrospective)

The following changes have already been applied to the codebase to address discovered issues:

### 4.1. Core Graph Logic (`coretext/core/graph/manager.py`)
- **Fix:** Added `⟨...⟩` escaping to node and edge IDs in `UPDATE` queries.
- **Rationale:** SurrealDB parsing failed on IDs containing hyphens (e.g., filenames).

### 4.2. Data Models (`coretext/core/graph/models.py`)
- **Fix:** Renamed `file_path` to `path` in `FileNode` and `HeaderNode`.
- **Fix:** Added `title` and `summary` fields with default empty strings.
- **Rationale:** Alignment with `DEFAULT_SCHEMA_MAP_CONTENT` in `schema.py`. The schema expects `path`, `title`, and `summary`.

### 4.3. Schema Definition (`coretext/core/parser/schema.py`)
- **Fix:** Added `commit_hash`, `created_at`, `updated_at` to node definitions.
- **Rationale:** Ensuring schema allows storage of versioning metadata.

### 4.4. CLI & Hooks (`coretext/cli/commands.py`)
- **Fix:** `install_hooks` now writes hooks invoking `sys.executable -m coretext.cli.main` instead of hardcoded `coretext`.
- **Fix:** Created synchronous `post_commit_hook` wrapper for async logic.
- **Rationale:** Robustness across different Python environments (Poetry/venv) and fixing `asyncio.run` loop conflicts.

### 4.5. Async Utilities (`coretext/core/sync/timeout_utils.py`)
- **Fix:** Refactored `run_with_timeout_or_detach` to be `async` and use `await`.
- **Rationale:** Resolving `RuntimeError: asyncio.run() cannot be called from a running event loop`.

## 5. Implementation Handoff

**Recipient:** Senior Developer / Database Specialist
**Scope:** Critical Bug Fix (Story 1.4 follow-up)

**Responsibilities:**
1.  Debug `query_surreal.py` to identify exactly *which* field is causing the `NONE` error.
2.  Once identified, apply the fix to `models.py` or `schema.py`.
3.  Verify end-to-end data ingestion from a `git commit`.
4.  Only then proceed to Epic 2.

**Success Criteria:**
- `python3 query_surreal.py` prints a successfully inserted record ID.
- `SELECT * FROM file` in Surrealist shows `demo.md`.
