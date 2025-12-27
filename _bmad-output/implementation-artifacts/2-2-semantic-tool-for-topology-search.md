# Story 2.2: semantic-tool-for-topology-search

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI agent,
I want a semantic tool to search the knowledge graph for topological connections,
so that I can understand project structure and dependencies relevant to my task.

## Acceptance Criteria

1.  **Embedding Model:** `nomic-embed-text-v1.5` is integrated via `sentence-transformers` with `trust_remote_code=True`.
2.  **Matryoshka Slicing:** The system supports generating variable-dimension embeddings (defaulting to 768, but capable of slicing) in `coretext/core/vector/embedder.py`.
3.  **Local Cache:** The model is downloaded to and loaded from `~/.coretext/cache/` (or similar local path) to ensure offline capability.
4.  **Vector Storage:** The Graph Schema is updated (`coretext/db/migrations.py`) to include a vector field on relevant nodes (e.g., `embedding` on `Header` and `File` nodes) with an HNSW index.
5.  **Semantic Search:** `coretext/core/graph/manager.py` implements a `search_topology(query: str, limit: int)` method that:
    *   Generates an embedding for the query (with `search_query:` prefix).
    *   Executes a SurrealQL vector similarity search (`vector::similarity::cosine` or `knn`).
    *   Returns a list of matching nodes with their similarity scores.
6.  **MCP Tool Endpoint:** A `POST /mcp/tools/search_topology` endpoint is implemented in `coretext/server/mcp/routes.py` that wraps the graph manager's search method.
7.  **Docstrings:** The endpoint includes a comprehensive docstring describing its usage for AI agents.

## Tasks / Subtasks

- [ ] **Core: Embedding Engine** (AC: 1, 2, 3)
  - [ ] Implement `coretext/core/vector/embedder.py` class `VectorEmbedder`.
  - [ ] Add logic to load `nomic-ai/nomic-embed-text-v1.5` with `trust_remote_code=True`.
  - [ ] Implement caching mechanism (check local dir first).
  - [ ] Add `encode(text, task_type="search_document")` method handling prefixes and Matryoshka slicing.
- [ ] **DB: Schema & Migration** (AC: 4)
  - [ ] Update `coretext/db/migrations.py` to `DEFINE FIELD embedding ON node TYPE array<float>`.
  - [ ] Add `DEFINE INDEX node_embedding_index ON node FIELDS embedding HNSW DIMENSION 768`.
  - [ ] Ensure migration runs on startup.
- [ ] **Core: Graph Manager Integration** (AC: 5)
  - [ ] Update `coretext/core/graph/manager.py` to ingest embeddings when creating/updating nodes. (Note: This might need a separate "re-index" trigger or happen on sync. For this story, focus on the *search* capability, but ensure data *can* be stored).
  - [ ] *Self-Correction:* Real-time embedding during sync might be slow. Decisions from Architecture say "Embeddings are generated in Python Daemon".
  - [ ] Add `search_topology(query)` method using SurrealQL vector functions.
- [ ] **Server: MCP Endpoint** (AC: 6, 7)
  - [ ] Add `search_topology` route to `coretext/server/mcp/routes.py`.
  - [ ] Define Pydantic models for `SearchTopologyRequest` and `SearchTopologyResponse`.
  - [ ] Ensure docstrings are agent-friendly.

## Dev Notes

- **Model Loading:** Use `sentence_transformers.SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)`.
- **Prefixes:** Nomic requires `search_query:` for queries and `search_document:` for documents.
- **SurrealDB Index:** `DEFINE INDEX ... HNSW ...` is crucial for performance.
- **Async:** Embedding generation is CPU-bound. Run it in a thread pool (`asyncio.to_thread`) to avoid blocking the FastAPI event loop.

### Project Structure Notes

- `coretext/core/vector/` is the new domain for this story.
- Ensure `python-multipart` is installed (it was in Story 1.1) if needed for file uploads, though this is a text search.

### References

- [Nomic Embed Text v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
- [SurrealDB Vector Search](https://surrealdb.com/docs/surrealql/datamodel/indexes)

## Dev Agent Record

### Agent Model Used
{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
