# CoreText Dogfooding Report

**Date:** 2026-01-09
**Status:** SUCCESS

## Overview
Successfully implemented isolated knowledge base management using the `_coretext-knowledge` directory. Verified that the system strictly operates within configured boundaries and correctly indexes Markdown documentation.

## Key Findings
1.  **Isolation:** Setting `docs_dir` to `_coretext-knowledge` successfully isolated the system from the project root.
2.  **Safety:** The `sync` command was refined to manually exclude common garbage directories (`.git`, `node_modules`, etc.) and focus strictly on Markdown files.
3.  **Indexing Performance:**
    -   Files Synced: 17
    -   Nodes Ingested: 214
    -   Sync Time: ~25s (including embedding generation)
4.  **Query Capability:**
    -   Verified natural language Q&A for architectural questions.
    -   Verified hybrid search (substring matching) for specific mentions.

## Friction Points & Fixes
-   **Regex Parsing:** SurrealDB 2.0 `~` operator with parameters caused parsing errors. Fixed by switching to `CONTAINS` for robust string matching.
-   **Path Normalization:** The system stores absolute paths when files are provided as such. Improved test matching using `string::contains` to handle absolute path prefixes.
-   **Discovery Bloat:** Initial attempt to index root found >1000 files. Enforced `docs_dir` constraint and improved `rglob` filtering to prevent this.

## Gap Analysis
-   **Code Indexing:** Currently, only Markdown is supported for rich AST parsing. If code knowledge is required, it must be represented as Markdown or a dedicated Python parser must be added.
-   **Path Portability:** Storing absolute paths makes the DB non-portable across machines. Recommend enforcing project-relative paths in the `GraphManager`.

## Conclusion
CoreText is ready for production use as a documentation-first knowledge graph engine. The sandbox mechanism provides the necessary safety for enterprise repositories.
