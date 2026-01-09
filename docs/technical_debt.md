# Technical Debt Log

## Pending Issues

### Critical
*   **SurrealDB Data Ingestion Failure ('NONE' Value Error)**: Persistent "Can not execute CREATE statement using value: NONE" error when inserting Pydantic models into SurrealDB via `AsyncSurreal` client.
    *   **Status**: **Resolved** (2026-01-09). Fixed by `GraphManager` safety checks and schema defaults.

### Testing
*   **CLI `init` command integration tests**: The integration tests for `coretext init` (in `tests/unit/cli/test_commands.py`) fail with `exit_code=2` when run via `typer.testing.CliRunner`.
    *   **Cause**: Incompatibility between `CliRunner`, async commands, and `Path` options with default values in the version of Typer/Click being used.
    *   **Impact**: Tests cannot verify the success exit code (0) despite the command logic being functionally correct and verified via component mocks.
    *   **Status**: Recorded on 2025-12-07.
    *   **Action Required**: Investigate `CliRunner` alternatives for async Typer commands or refactor the command structure to be more test-friendly in future refactoring sprints.

### Architectural Trade-offs
*   **Simplified SurrealDB Management in Post-commit Hook**: The `post_commit_hook` attempts to start SurrealDB if not running. This is a simplified approach, acknowledging that a robust solution would involve a dedicated daemonized DB.
    *   **Cause**: Prioritization of MVP and quick integration.
    *   **Impact**: Potential for minor delays in commit process if DB needs to start; less robust error handling than a fully daemonized solution.
    *   **Status**: Recorded on 2025-12-10 (current date).
    *   **Action Required**: Consider implementing a dedicated daemon for SurrealDB management in a future architectural sprint.

### Implementation Gaps
* **Parser Blocking Future Links (Obsidian Style)**: The database schema for edges was updated to `SCHEMALESS` to allow linking to non-existent nodes (Story 1.6), but the `MarkdownParser` logic still treats missing targets as `ParsingErrorNode` and halts edge creation.
    * **Cause**: Validation logic in `coretext/core/parser/markdown.py` explicitly checks `.exists()` and returns early on failure.
    * **Impact**: Prevents the creation of "future links" (references to not-yet-created files), defeating the purpose of the schemaless edge design.
    * **Status**: Identified during code review.
    * **Action Required**: Relax validation in `MarkdownParser` to allow emitting `REFERENCES` edges even if the target file does not exist on disk.

### Data Integrity & Maintenance
* **Lack of Deletion/Rename Propagation (Ghost Nodes)**: The system currently only handles `UPSERT` (Add/Modify). Deleting or renaming a file in Git does not remove the old node from SurrealDB.
    * **Cause**: `git_utils.py` filters exclude 'D' (Deleted) status, and there is no "Delete" logic in the sync engine.
    * **Impact**: The graph will accumulate "ghost nodes" (nodes corresponding to deleted or renamed files) over time, leading to dead links.
    * **Status**: Accepted Trade-off. The project follows an "Append-only/Safe" philosophy for automated hooks.
    * **Action Required**: Do not implement automated deletion to prevent accidental data loss. Instead, implement a manual `coretext vacuum` or `prune` CLI command for periodic maintenance.

* **Concurrency in Post-commit Hook (Race Condition)**: Rapid consecutive commits may trigger parallel, detached hook executions.
    * **Cause**: No lockfile, queue, or PID check mechanism for the background sync process (`post-commit`).
    * **Impact**: Potential transaction conflicts in SurrealDB or out-of-order updates (older commit overwriting newer commit).
    * **Status**: Accepted Risk for Single-User MVP.
    * **Action Required**: Users should wait for sync completion messages. Future iterations should implement a lockfile or a daemonized queue system.

* **File Path as Node ID**: Node IDs are derived from mutable file paths (e.g., `folder/file.md`).
    * **Cause**: Simplicity for MVP and human-readability of IDs.
    * **Impact**: Refactoring folder structure (moving files) changes the Node ID, breaking the history and identity of the node in the graph (creating a new node instead of moving the old one).
    * **Action Required**: Evaluate moving to UUIDs for Node IDs in the future (requires a complex migration strategy).

## Optimization Opportunities

### Vector Engine
**Status:** Open
**Impact:** Performance, Memory, Storage efficiency.
**Identified:** 2026-01-09

The current embedding implementation uses `nomic-embed-text-v1.5` in a functional but unoptimized state.

- [ ] **Activate Matryoshka Slicing:**
    - *Current:* Storing full 768-float vectors.
    - *Optimization:* Reduce dimensions to 256 or 128. Nomic v1.5 supports this with ~98% performance retention.
    - *Benefit:* ~66% reduction in storage and index size; faster search.

- [ ] **Implement Batch Encoding:**
    - *Current:* `GraphManager.ingest` calls `embedder.encode(text)` individually for every node.
    - *Optimization:* Implement `encode_batch` in `VectorEmbedder` and use `model.encode(list_of_texts)`.
    - *Benefit:* Significant speedup during graph ingestion/sync.

- [ ] **Model Quantization:**
    - *Current:* Loading full precision model (~300MB RAM, >5s cold start).
    - *Optimization:* Switch to quantized (int8/binary) model loading.
    - *Benefit:* Reduced memory footprint (critical for 500MB daemon limit) and faster startup.