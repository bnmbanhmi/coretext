# Technical Debt Log

## Optimization Summary Matrix

| Component | Optimization Opportunity | Impact | Status |
| :--- | :--- | :--- | :--- |
| **Vector Engine** | Matryoshka Slicing (768 -> 128/256) | 66% reduction in storage; faster search. | Open |
| **Vector Engine** | Batch Encoding in `VectorEmbedder` | Significant speedup for graph ingestion. | Open |
| **Vector Engine** | Model Quantization (int8/binary) | Lower RAM usage (target < 500MB). | Open |
| **Vector Engine** | ONNX Runtime / GGML Acceleration | Millisecond cold-start; hardware acceleration. | Open |
| **Search/Ranking** | **Full-Text Indexing (FTS)** | Instant keyword filtering (replaces O(N) scan). | Open |
| **Search/Ranking** | **Native Graph Traversal (SurrealQL)** | Eliminates Python BFS round-trip latency. | Open |
| **Search/Ranking** | **Hybrid Search (RRF)** | Better relevance by combining Vector + Lexical. | Open |
| **Search/Ranking** | **Semantic Query Caching** | Instant response for repeated/similar queries. | Open |
| **Core Sync** | **Incremental Indexing (mtime/hash)** | Avoids redundant re-parsing of unchanged files. | Open |
| **Core Sync** | **Async/Batch Link Validation** | Prevents I/O blocking during the parsing phase. | Open |
| **Core Sync** | **Resilient Ingestion (Partial Success)** | Prevents one bad file from blocking entire sync. | Open |
| **Core Sync** | **Multi-Process Parsing (GIL Bypass)** | Linear sync scaling with available CPU cores. | Open |
| **Database** | **Connection Pooling & Config** | Eliminates handshake cost; removes hardcoded URLs. | Open |
| **Database** | **Schema Versioning/Migrations** | Enables safe data-preserving schema updates. | Open |
| **Knowledge** | **Hierarchical Context Indexing** | Bird's-eye view summaries for large folders. | Open |
| **System** | **Swap/Pagefile Monitoring** | Improved stability on low-resource machines. | Open |
| **CLI** | **Lazy Imports (Startup Latency)** | Prevents loading PyTorch on simple commands. | Open |
| **MCP API** | **Payload Optimization (Content)** | Reduces token cost/bandwidth by truncating content. | Open |
| **Config** | **Env Var Support** | Enables CI/CD and container-friendly configuration. | Open |
| **Logging** | **Log Rotation & Formatting** | Prevents disk overflow; enables structured parsing. | Open |

## Pending Issues

### Critical
*   **SurrealDB Data Ingestion Failure ('NONE' Value Error)**: Persistent "Can not execute CREATE statement using value: NONE" error when inserting Pydantic models into SurrealDB via `AsyncSurreal` client.
    *   **Status**: **Resolved** (2026-01-09). Fixed by `GraphManager` safety checks and schema defaults.

### Testing
*   **CLI `init` command integration tests**: The integration tests for `coretext init` (in `tests/unit/cli/test_commands.py`) fail with `exit_code=2` when run via `typer.testing.CliRunner`.
    *   **Status**: Recorded on 2025-12-07.
    *   **Action Required**: Investigate `CliRunner` alternatives for async Typer commands.

### Architectural Trade-offs
*   **Simplified SurrealDB Management in Post-commit Hook**: The `post_commit_hook` attempts to start SurrealDB if not running. 
    *   **Status**: Recorded on 2025-12-10.
    *   **Action Required**: Consider implementing a dedicated daemon for SurrealDB management.

### Implementation Gaps
* **Parser Blocking Future Links (Obsidian Style)**: The `MarkdownParser` logic still treats missing targets as `ParsingErrorNode`.
    *   **Action Required**: Relax validation to allow emitting `REFERENCES` edges for non-existent files.

## Optimization Opportunities

### Advanced Architecture (Next-Level)
**Status:** Open
**Impact:** Breakthrough performance and intelligence.
**Identified:** 2026-01-09

- [ ] **Semantic Query Caching:**
    *   *Optimization:* Implement an in-memory cache for semantic search results using a small vector store or exact-match lookup.
    *   *Benefit:* Zero-latency response for repeated agent queries.

- [ ] **Local Acceleration (ONNX Runtime / GGML):**
    *   *Optimization:* Migrate embedding inference from PyTorch to ONNX or GGML.
    *   *Benefit:* 50%+ reduction in RAM; near-instant model loading.

- [ ] **Multi-Process Sync Worker:**
    *   *Optimization:* Move parsing/hashing logic to `ProcessPoolExecutor` to bypass the GIL.
    *   *Benefit:* True parallel sync utilizing all available CPU cores.

- [ ] **Hierarchical Context Indexing:**
    *   *Optimization:* Automatically generate and embed "Summary Nodes" for directories and sections.
    *   *Benefit:* Superior LLM context management for large-scale projects.

### CLI & API Efficiency
**Status:** Open
**Impact:** UX Latency, Token Cost, Bandwidth.
**Identified:** 2026-01-09

- [ ] **CLI Startup Latency (Lazy Imports):**
    *   *Optimization:* Move heavy imports inside command functions.
    *   *Benefit:* Instant CLI response.

- [ ] **MCP Payload Optimization:**
    *   *Optimization:* Add `include_content` flag or return node summaries by default.
    *   *Benefit:* Reduced token consumption for LLM agents.

### Ops & Reliability
**Status:** Open
**Impact:** Deployment flexibility, Observability, Resilience.
**Identified:** 2026-01-09

- [ ] **Environment Variable Configuration:**
    *   *Optimization:* Switch to `pydantic-settings`.

- [ ] **Log Rotation & Structured Logging:**
    *   *Optimization:* Implement `TimedRotatingFileHandler` and JSON formatting.

- [ ] **Resilient Ingestion (Retry & Partial Success):**
    *   *Optimization:* Add exponential backoff retries for DB transactions and support "Partial Success" mode.

### Core Architecture & Sync Performance
**Status:** Open
**Impact:** Sync Speed, I/O Blocking, Scalability.
**Identified:** 2026-01-09

- [ ] **Incremental Indexing & Change Detection:**
    *   *Optimization:* Use persistent cache of file `mtime` and content hashes.

- [ ] **Async/Batch Link Validation:**
    *   *Optimization:* Decouple link extraction from validation.

- [ ] **Database Connection Pooling & Hardcoded URL Fix:**
    *   *Optimization:* Implement persistent connection pool and use `config.surreal_url`.

- [ ] **Schema Versioning & Migrations:**
    *   *Optimization:* Implement a simple migration manager.

### Vector Engine
**Status:** Open
**Impact:** Performance, Memory, Storage efficiency.
**Identified:** 2026-01-09

- [ ] **Activate Matryoshka Slicing:**
    *   *Optimization:* Reduce dimensions to 256 or 128.

- [ ] **Implement Batch Encoding:**
    *   *Optimization:* Use `model.encode(list_of_texts)` in `VectorEmbedder`.

- [ ] **Model Quantization:**
    *   *Optimization:* Switch to quantized (int8/binary) model loading.

### Search & Ranking Strategy
**Status:** Open
**Impact:** Search Quality, Query Latency.
**Identified:** 2026-01-09

- [ ] **Full-Text Search (FTS) Indexing:**
    *   *Optimization:* Define SurrealDB `ANALYZER` and `INDEX ... SEARCH`.

- [ ] **Native Graph Traversal (SurrealQL):**
    *   *Optimization:* Move traversal logic into a single SurrealQL query.

- [ ] **Advanced Ranking (RRF / Re-ranking):**
    *   *Optimization:* Implement Reciprocal Rank Fusion (RRF) or Cross-Encoder re-ranking.
