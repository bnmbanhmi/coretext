# Story 1.3: bmad-markdown-parsing-to-graph-nodes

Status: ready-for-dev
Completion Note: Ultimate context engine analysis completed - comprehensive developer guide created

## Story

As a `coretext` system,
I want to parse BMAD Markdown files using AST-based methods,
so that their content can be accurately and deterministically converted into a structured Knowledge Graph, with clear identification of malformed syntax.

## Acceptance Criteria

1.  **Valid BMAD Markdown Parsing:** Given a valid BMAD Markdown file, when parsed, the system accurately converts its structural elements (file, headers, text content) into corresponding graph nodes and relationships in SurrealDB, adhering to the defined Graph Schema Strategy (Root Node: File, Child Nodes: Markdown Header, Relationships: CONTAINS, PARENT_OF).
2.  **Malformed Markdown Handling (Loud Failures):** Given a malformed BMAD Markdown file (e.g., broken syntax), when parsed, the system detects the malformation, generates a "Parsing Error" Node, rejects the update of the corresponding graph section, and makes the failure visible (e.g., clear line-number reporting).
3.  **AST-Based Parsing Enforcement:** The parsing mechanism explicitly uses Abstract Syntax Tree (AST) analysis to preserve semantic boundaries, rather than relying on character count chunking or fuzzy parsing methods.
4.  **Referential Integrity Consideration:** The parser supports the identification of Standard Markdown Links and their conversion into graph edges, and flags potential "Dangling Reference" warnings for unresolved links (though full validation may be in a later story).
5.  **Deterministic Output:** For identical Markdown file content, the parser consistently produces an identical Knowledge Graph structure, verifiable via a deterministic test suite.

## Dev Notes

### 🔥 STRATEGIC OVERRIDE: Smart Linking & Canonical Normalization

1.  **CRITICAL: Canonical Path Normalization (The 'Single Truth' Rule)**
    *   **Rule:** You must ensure that File A referencing `../docs/prd.md` and File B referencing `docs/prd.md` both point to the EXACT SAME Node ID.
    *   **Logic:** Before creating any Node or Edge, you MUST resolve all paths to the Project Root Relative Path.
    *   **Example:** If in `coretext/core/`, referencing `../../docs/prd.md` -> It resolves to ID `docs/prd.md`.
    *   **Constraint:** The Node ID in SurrealDB must ALWAYS be the clean, relative path from root (e.g., `docs/epics.md`), never absolute paths (`/Users/...`) and never containing `..`.

2.  **MVP GOAL: Immediate Visualization**
    *   Prioritize creating `REFERENCES` edges to visualize connectivity in Surrealist.

3.  **LOGIC UPDATE: Smart Hybrid Link Detection**
    *   **Type A (Explicit):** Parse `[Label](./path)`. Resolve the relative path to Canonical ID.
    *   **Type B (Implicit):** Scan text for `r"[\w\-/]+\.(md|yaml)"`.
    *   **Validate:** Check if file exists.
    *   **Normalize:** Convert the found string to Canonical ID.
    *   **Create Edge:** Only if target exists.
    *   **Definition of Done:** `SELECT * FROM file WHERE id = 'docs/prd.md'` shows incoming edges from both explicit links and plain text references, unified under one ID.

### Relevant Architecture Patterns and Constraints

*   **Project Structure:** Parser logic belongs in `coretext/core/parser/`. Graph management logic is in `coretext/core/graph/`. Database interactions via `coretext/db/`.
*   **Graph Schema Strategy:** The parser must implement the following:
    *   **Root Node:** The Markdown file itself (ID = `file_path`).
    *   **Child Nodes:** Every Markdown Header (`#`, `##`, `###`, etc.) creates a distinct Graph Node.
    *   **Relationships:**
        *   `CONTAINS`: File -> Header.
        *   `PARENT_OF`: H1 -> H2, H2 -> H3, etc.
    *   **Content Storage:** Text directly under a header belongs to that Header Node.
*   **"Strict Schema, Loud Failures":** Malformed Markdown must result in a "Parsing Error" Node and a rejected update, never a "best guess." Error reporting should be clear, including line numbers.
*   **AST-Based Parsing (MANDATORY):** Use **`markdown-it-py`** for robust, CommonMark-compliant AST generation. Do not use regex or fuzzy parsing.
*   **Interface Contract:**
    *   `Parser.parse(file_path: Path) -> List[BaseNode]`
    *   `GraphManager.ingest(nodes: List[BaseNode]) -> SyncReport`
*   **Error Model:** `ParsingErrorNode` must contain `file_path`, `line_number`, `error_message`, and `raw_content_snippet`.
*   **Pydantic v2:** Use for internal data models representing graph nodes and edges.
*   **SurrealDB Interaction:** All DB writes must go through the `GraphManager` (`coretext/core/graph/manager.py`).

### Testing Standards Summary

*   **Deterministic Test Suite:** Develop a comprehensive test suite (using `pytest`) with varied Markdown inputs (valid, malformed, edge cases) to assert that the JSON output (graph structure) is exact and reproducible.
*   **Test Data Fixtures:** create `tests/data/` containing:
    *   `valid_simple.md` (Basic headers)
    *   `valid_complex.md` (Nested headers, links)
    *   `malformed_syntax.md` (Broken structures to test error nodes)
*   **Error Reporting:** Tests should verify that malformed Markdown correctly triggers "Parsing Error" Nodes and provides clear error messages.
*   **Integration with Story 1.2:** Ensure parser output can be seamlessly stored and managed by the `SurrealDB Management & Schema Application` implemented in the previous story.

### Technical Requirements

*   **Core Parser Module:** Implement `coretext/core/parser/markdown.py` using `markdown-it-py`.
*   **Schema Projection Logic:** Implement or extend `coretext/core/parser/schema.py` to define the mapping from Markdown structure to graph nodes/edges.
*   **Graph Node Models:** Define specific Pydantic models in `coretext/core/graph/models.py` for File Nodes, Header Nodes, `ParsingErrorNode`, and their relationships.
*   **Graph Manager Integration:** Ensure `coretext/core/graph/manager.py` implements the `ingest()` method.
*   **Error Handling:** Implement robust error handling for parsing failures, generating "Parsing Error" nodes as specified.

### Project Structure Notes

*   **Code Organization:**
    *   Parser logic: `coretext/core/parser/markdown.py`
    *   Schema mapping: `coretext/core/parser/schema.py`
    *   Graph Models: `coretext/core/graph/models.py`
    *   Graph Manager: `coretext/core/graph/manager.py`
    *   **Test Data:** `tests/data/*.md`
*   **`.coretext/schema_map.yaml`:** This file defines the mapping from external Markdown headers to internal DB properties, which the parser must utilize.

### Previous Story Intelligence (Story 1.2 Learnings)

*   **Database Foundation:** Story 1.2 (`SurrealDB Management & Schema Application`) has established the local SurrealDB instance, binary management, and automatic schema application. Story 1.3 will build directly upon this foundation, utilizing the `GraphManager` for all DB interactions.
*   **Schema Application:** The mechanism to apply Pydantic-defined schemas to SurrealDB is in place. Story 1.3's graph node models will integrate with this.
*   **Pydantic Usage:** Story 1.2 extensively used Pydantic for data modeling, which aligns with Story 1.3's need for defining graph node structures.
*   **Testing Approach:** The previous story's integration tests for SurrealDB and schema application provide a precedent for how to test database interactions and schema changes.

### Git Intelligence Summary

*   The most recent work has focused on documenting the project (adding diagrams, etc.).
*   Story 1.2 completion (`958d2d5400f7c1d03dda19c67092a254cab6433a complete 1-2, including dev, review, fix`) signifies a stable codebase after implementing SurrealDB management and schema application, providing a solid foundation for Story 1.3.
*   The emphasis on tracking file origins (`020894cac49371a50babb1fe0688b2b71fb9cb06 add docs_with_origin diagram to track down the origin of each file`) reinforces the need for accurate file path handling and metadata in the graph nodes created by the parser.

### Latest Technical Information

*   **Library Selection:** `markdown-it-py` is chosen for its speed, safety, and strict CommonMark compliance, which is crucial for deterministic parsing.
*   **Pydantic v2:** Essential for defining robust internal data models for graph nodes and edges, ensuring type safety and schema validation.
*   **SurrealDB:** The existing setup from Story 1.2 provides a stable foundation for interaction. Focus for this story will be on defining and interacting with the schema for Markdown-derived nodes and edges.

### Project Context Reference

*   No specific `project-context.md` file was found. Relevant project context has been derived from `PRD.md` and `architecture.md`.

---
## Dev Agent Record

### Context Reference

*   `docs/prd.md`
*   `docs/architecture.md`
*   `docs/test-design-epic-1.md`
*   `docs/sprint-artifacts/1-2-surrealdb-management-schema-application.md`

### Agent Model Used

gemini-2.5-flash

### Debug Log References

### Completion Notes List

*   Comprehensive analysis of `PRD.md`, `architecture.md`, and `test-design-epic-1.md` completed.
*   Learnings from previous story (`1.2-surrealdb-management-schema-application`) incorporated.
*   Web research on Python Markdown AST parsers conducted.
*   Detailed story, acceptance criteria, technical requirements, and dev notes generated.

### File List

*   `coretext/core/parser/markdown.py` (NEW - Core parser module)
*   `coretext/core/parser/schema.py` (MODIFIED - Schema projection logic)
*   `coretext/core/graph/models.py` (MODIFIED - Graph Node Pydantic models)
*   `coretext/core/graph/manager.py` (MODIFIED - Graph Manager Integration)
*   `tests/unit/core/parser/test_markdown.py` (NEW - Deterministic test suite for parser)