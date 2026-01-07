# Story 5.3: Hybrid Execution & Thick Tool Implementation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an AI Agent,
I want a single "Thick Tool" named `query_knowledge` that combines semantic search, graph traversal, regex matching, and keyword filtering,
so that I can perform ANY kind of context retrieval (fuzzy, exact, pattern-based, or structural) in a single query without needing multiple round-trips.

## Acceptance Criteria

1.  **Universal Query Capability**: The `query_knowledge` tool accepts the following parameters:
    *   `natural_query` (str): The semantic query for vector search (required).
    *   `depth` (int, default=1): Traversal depth for context.
    *   `top_k` (int, default=5): Number of anchor nodes to retrieve.
    *   `regex_filter` (str, optional): A regex pattern to filter nodes (e.g., `^/src/.*\.py$`).
    *   `keyword_filter` (str, optional): Specific keywords that MUST be present (lexical/exact match).
2.  **Combined Execution Logic**:
    *   The system first identifies "Anchor Nodes" using **Vector Search** based on `natural_query`.
    *   It *simultaneously* or *subsequently* filters these anchors using the `regex_filter` (if provided) and `keyword_filter` (if provided).
    *   *Note: If `regex_filter` is provided but `natural_query` is empty/generic, the system should allow searching primarily by Regex if feasible, or default to vector search first then filter.* (For this story, assume Vector is always the entry point, filtered by the others).
3.  **Graph Traversal**: From the *filtered* Anchor Nodes, the system traverses graph relationships (e.g., `PARENT_OF`, `depends_on`, `governed_by`) to the specified `depth`.
4.  **Consolidated Context**: Returns a single, deduplicated subgraph object containing all relevant nodes and edges.
5.  **Performance**: Latency < 500ms for typical usage.
6.  **Abstraction**: `GraphManager` handles the complexity of constructing the composite SurrealQL query.

## Tasks / Subtasks

- [x] **Enhance `GraphManager` with Universal Search Logic**
  - [x] Update `search_hybrid` signature: `search_hybrid(query: str, top_k: int, depth: int, regex: str = None, keywords: str = None)`.
  - [x] Construct SurrealQL query with dynamic `WHERE` clauses:
    -   Vector score: `vector::distance(...)`
    -   Regex: `AND file_path ~ $regex` (or `string::matches(content, $regex)`)
    -   Keywords: `AND content CONTAINS $keyword` (or use FTS `@@` operator if indexed).
  - [x] Implement the traversal logic (`SELECT ->edge->node FROM $filtered_anchors`).
- [x] **Implement `query_knowledge` MCP Tool**
  - [x] Update MCP Tool definition to include `regex_filter` and `keyword_filter` as optional strings.
  - [x] Add docstrings explaining how to use Regex for file path patterns or specific code structures.
- [x] **Optimize Query Strategy**
  - [x] Decide on "Filter-First" vs "Vector-First" strategy based on inputs. (Likely Vector-First for "semantic" queries, but ensure filters are applied efficiently).
- [x] **Verify End-to-End**
  - [x] Test 1: Pure Semantic ("Auth system").
  - [x] Test 2: Semantic + Regex ("Auth system" in `^/server/.*`).
  - [x] Test 3: Semantic + Keyword ("Auth" containing "JWT").

## Dev Notes

### Advanced Search Capabilities

*   **Regex (`~` or `string::matches`)**: This is powerful for filtering file paths or finding specific code patterns (e.g., `class .*Manager`). It is computationally more expensive than simple indexing, but for a local knowledge graph (<10k nodes), it is acceptable and highly flexible.
*   **Lexical (`CONTAINS` or FTS)**: "Lexical" usually implies Full-Text Search. For simplicity in this iteration, `CONTAINS` might be sufficient for keywords. If performance degrades, we can implement a proper `DEFINE ANALYZER` and `DEFINE INDEX ... FULLTEXT` in SurrealDB later.
*   **Combination Strategy**: The query should likely order by Vector Similarity *filtered by* the Regex/Keyword constraints.
    *   `SELECT * FROM node WHERE vector::distance(...) < threshold AND content ~ $regex ...`
    *   *Correction*: SurrealDB usually requires ordering by distance for KNN.
    *   `SELECT *, vector::distance(...) AS dist FROM node WHERE content ~ $regex ORDER BY dist ASC LIMIT $top_k`

### Project Structure Notes

- **Location**: `coretext/core/graph/manager.py`
- **Tool Definition**: `coretext/server/mcp/tools.py`

### References

- [SurrealQL Operators](https://surrealdb.com/docs/surrealql/operators) (`~` for regex, `CONTAINS` for containment)

## Dev Agent Record

### Implementation Plan
- Implemented `search_hybrid` in `GraphManager` using "Vector-First" strategy with dynamic WHERE clauses for regex/keywords.
- Implemented `query_knowledge` endpoint in `routes.py` exposing this functionality.
- Added new `QueryKnowledgeRequest/Response` models.
- Wrote unit tests for `GraphManager` and integration tests for the endpoint.

### Completion Notes
- `search_hybrid` supports depth traversal by iteratively querying edge tables.
- `query_knowledge` tool correctly maps API request to manager call.
- All tests passed.

## File List
- coretext/core/graph/manager.py
- coretext/server/mcp/routes.py
- tests/unit/core/graph/test_search_hybrid.py
- tests/unit/server/mcp/test_routes.py

## Change Log
- 2026-01-07: Implemented `search_hybrid` and `query_knowledge` tool with full test coverage.
- 2026-01-07: Senior Developer Review fixes:
  - Updated `GraphManager.search_hybrid` and `search_topology` to query all node tables dynamically.
  - Added error logging to `search_hybrid` traversal loop.
  - Fixed `get_dependencies` route to handle non-prefixed IDs.
