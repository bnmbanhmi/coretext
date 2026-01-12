# Story 4.2: mcp-query-latency-optimization

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI agent,
I want `coretext` to respond to my context queries quickly,
so that my "thinking" phase remains fluid and efficient.

## Acceptance Criteria

1.  **Latency Target:** The total Round-Trip Time (RTT) for MCP tools `search_topology` and `get_dependencies` is less than **500ms** (p95) for typical queries.
2.  **Non-Blocking Embeddings:** The embedding generation process (CPU-bound) does NOT block the FastAPI event loop.
3.  **Optimized Graph Queries:** SurrealDB queries utilize appropriate indexes and fetch only necessary data fields to minimize overhead.
4.  **Performance Baseline:** A benchmark script exists to verify the latency target is met.

## Tasks / Subtasks

- [x] **Performance Benchmarking (Baseline)**
    - [x] Create `scripts/benchmark_latency.py` to measure RTT of `search_topology` and `get_dependencies`.
    - [x] Establish current baseline latency.
- [x] **Async Embedding Optimization (Critical)**
    - [x] Modify `coretext/core/vector/embedder.py` to run the synchronous `model.encode()` method in a threadpool (using `run_in_executor`).
    - [x] Verify that the main event loop is no longer blocked during embedding.
- [x] **SurrealDB Indexing & Query Tuning**
    - [x] Review `coretext/db/migrations.py` and ensure indexes exist for:
        - `file_path` (lookup)
        - `type` (filtering)
        - Vector fields (MRL/HNSW index if supported by local surreal, otherwise flat search optimization).
    - [x] Optimize `GraphManager` queries in `coretext/core/graph/manager.py`:
        - Use `SELECT specific, fields FROM` instead of `SELECT *` where possible to reduce serialization cost.
        - Optimize graph traversal queries for `get_dependencies`.
- [x] **Verification & Tuning**
    - [x] Run `scripts/benchmark_latency.py` against optimized implementation.
    - [x] Tuning `uvicorn` settings if necessary (e.g., workers, though 1 is usually enough for local tool).

## Dev Notes

### Architecture & Performance Constraints
*   **Event Loop Blocking:** The most common cause of latency spikes in FastAPI + ML apps is running CPU-bound tasks (like `sentence-transformers.encode`) directly in an `async def` path. This freezes the loop.
    *   **Solution:** Use `await loop.run_in_executor(None, lambda: self.model.encode(text))` in `Embedder.embed`.
*   **SurrealDB Performance:**
    *   Ensure `DEFINE INDEX ...` statements are applied.
    *   Check if `SurrealDB` binary is running with appropriate resources.

### File Structure Notes
*   `coretext/core/vector/embedder.py`: Target for async refactor.
*   `coretext/core/graph/manager.py`: Target for query optimization.
*   `coretext/db/migrations.py`: Target for index definitions.

### Previous Story Intelligence
*   From Story 4.1: We learned that background threads can cause issues if not managed well. Here we are using `run_in_executor` which manages a pool, but we must ensure `Embedder` is thread-safe (usually is, `sentence-transformers` is generally fine for inference).

### References
*   [Epic 4: System Reliability & Performance Optimization](../planning-artifacts/epics.md#epic-4-system-reliability--performance-optimization)
*   [FastAPI Async/Await docs](https://fastapi.tiangolo.com/async/#path-operation-functions)

## Dev Agent Record

### Agent Model Used
Gemini-2.0-Flash-Thinking-Exp

### Debug Log References

### Completion Notes List
*   Created `scripts/benchmark_latency.py` to measure p95 latency.
*   Verified `VectorEmbedder` uses `asyncio.to_thread` for non-blocking execution.
*   Added `node_type_idx` to `coretext/db/migrations.py`.
*   Optimized `search_topology` in `coretext/core/graph/manager.py` to select specific fields (omitting embedding).
*   Made `get_dependencies` robust to ID types (RecordID/string).
*   Verified performance: `search_topology` ~44ms, `get_dependencies` ~3ms (p95). Both well below 500ms target.
*   Updated unit tests in `tests/unit/core/graph/test_manager.py`.
*   Updated integration test `tests/integration/server/test_story_2_1.py` to handle 404s correctly.

### File List
*   scripts/benchmark_latency.py
*   coretext/db/migrations.py
*   coretext/core/graph/manager.py
*   coretext/core/vector/embedder.py
*   tests/unit/core/graph/test_manager.py
*   tests/integration/server/test_story_2_1.py

## Change Log
*   2026-01-04: Initial implementation of query optimization and indexing. Added benchmark script and updated tests.
