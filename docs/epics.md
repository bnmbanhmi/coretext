# coretext - Epic Breakdown

**Author:** Minh
**Date:** 2025-12-04
**Project Level:** New Product Launch
**Target Scale:** Internal Tool

---

## Overview

This document provides the complete epic and story breakdown for coretext, decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

**Living Document Notice:** This is the initial version. It will be updated after UX Design and Architecture workflows add interaction and technical details to stories.

## Epics Summary

*   **Epic 1: Core Knowledge Graph Foundation**: Establishes the fundamental local-first knowledge graph, its synchronization with Git, and basic management.
*   **Epic 2: Agent Context Retrieval & Semantic Querying**: Focuses on enabling AI agents to query and retrieve precise, topologically aware context from the graph via MCP.
*   **Epic 3: Developer Workflow Integration & Tooling**: Implements CLI tools for developers to manage, inspect, and lint the knowledge graph.
*   **Epic 4: System Reliability & Performance Optimization**: Ensures the system operates efficiently, reliably, and within defined resource limits.

---

## Functional Requirements Inventory

1.  **FR1**: The system can parse BMAD-flavored Markdown files into a structured Knowledge Graph.
2.  **FR2**: The system can detect changes in Markdown files within a Git repository.
3.  **FR3**: The system can synchronize detected Markdown file changes into the Knowledge Graph.
4.  **FR4**: The system can store a Knowledge Graph in SurrealDB.
5.  **FR5**: The system can version the Knowledge Graph state based on Git commit hashes.
6.  **FR6**: The system can enforce referential integrity within the Knowledge Graph (e.g., verifying Standard Markdown Links).
7.  **FR7**: The system can detect and report malformed Markdown syntax that prevents successful parsing.
8.  **FR8**: The system can output a text-based dependency tree for a given node.
9.  **FR9**: The system can receive context queries from an AI Agent via an MCP Server.
10. **FR10**: The system can retrieve precise, topologically relevant context from the Knowledge Graph based on Agent queries.
11. **FR11**: The system can provide retrieved context to the AI Agent via the MCP Server.
12. **FR12**: The system can traverse graph relationships (e.g., `depends_on`, `governed_by`) to gather comprehensive context.
13. **FR13**: The system can integrate as a pre-commit Git hook.
14. **FR14**: The system can execute a synchronization process on `git commit`.
15. **FR15**: The system can run a "dry-run" integrity check on Markdown files before commit.
16. **FR16**: The system can provide a command-line interface (CLI) for system initialization.
17. **FR17**: The system can provide a CLI for viewing synchronization health.
18. **FR18**: The system can provide CLI commands for linting graph integrity.
19. **FR19**: The system can provide structured templates for creating BMAD Markdown files.
20. **FR20**: The system can complete incremental graph synchronization within a specified time limit for small commits.
21. **FR21**: The system can perform graph synchronization asynchronously for large commits.
22. **FR22**: The system can respond to Agent context queries within a specified time limit.
23. **FR23**: The system can operate within defined memory consumption limits.
24. **FR24**: The system can perform background processing with low CPU priority.

---

## FR Coverage Map

_This section will be populated during the story creation phase, mapping each FR to specific stories._

---

## Epic 1: Core Knowledge Graph Foundation

**User Value Statement**: Users can establish a reliable, local knowledge graph that automatically syncs with their Git repository, providing a foundational "second brain" for AI agents.

**PRD Coverage**: FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR13, FR14, FR16.

**Technical Context**:
*   **Architecture**: Custom AI-Native Scaffold (Python 3.10+, Poetry, FastAPI/Typer), SurrealDB (local-first, `~/.coretext/bin`), Nomic-Embed-Text-v1.5 (local embedding).
*   **Data Architecture**: "Schema Projection" (Pydantic Models <-> `schema_map.yaml`), Automatic Schema Application on Startup.
*   **Project Structure**: `coretext/core/graph/`, `coretext/db/`, `coretext/core/parser/`, `coretext/core/sync/`.
*   **Naming**: `snake_case` for database entities, `PascalCase` for Python classes.

**UX Integration**: CLI commands (`coretext init`, `coretext status`), invisible `git commit` hook.

**Dependencies**: None. This epic establishes the core system.

### Story 1.1: Project Initialization & Core Scaffolding

As a developer, I want to initialize the `coretext` project environment, so that I have the core scaffold and dependencies in place to begin development.

**Acceptance Criteria:**
*   Given I am in the project root directory
*   When I run the initial scaffolding commands
*   Then a Poetry project named `coretext` is created.
*   And `fastapi[standard]`, `typer`, `pydantic`, `surrealdb`, `python-multipart`, `uvicorn`, `gitpython`, `sentence-transformers` are added as dependencies.
*   And the basic project structure (`cli/`, `server/`, `core/`, `db/`) is laid out as defined in Architecture.md.
*   And an extension.yaml manifest file is created at the root level for Gemini CLI integration.

**Technical Notes:**
*   Run `poetry new coretext` and `poetry add ...` commands.
*   Create empty `__init__.py` files for package structure.
*   Setup `pyproject.toml` with basic project metadata.
*   Create an `extension.yaml` defining the tool entry point.

**Prerequisites:** None.

### Story 1.2: SurrealDB Management & Schema Application

As a `coretext` system, I want to manage a local SurrealDB instance and apply the graph schema automatically, so that the knowledge graph has a persistent and structured storage.

**Acceptance Criteria:**
*   Given the `coretext` project is initialized
*   When `coretext init` is executed
*   Then the platform-specific `surreal` binary is downloaded to `~/.coretext/bin/`.
*   And a `surreal.db` file is created or found in `.coretext/`.
*   And the user is prompted to start the daemon immediately ("Do you want to start the coretext daemon now? [Y/n]").
*   And on daemon startup, the SurrealDB schema (defined by Pydantic models mapped via `schema_map.yaml`) is automatically applied.
*   And `GraphManager` class is implemented to be the sole gatekeeper for DB writes.

**Technical Notes:**
*   Implement `coretext/db/client.py` for SurrealDB connection.
*   Implement `coretext/db/migrations.py` for schema definition and application logic.
*   Implement `coretext/core/graph/manager.py` with methods for basic node/edge operations (create/read/update/delete).
*   Define Pydantic models for core graph entities (e.g., `Node`, `Edge`).
*   Implement logic for `schema_map.yaml` to map BMAD concepts to internal DB schema.

**Prerequisites:** Story 1.1.

### Story 1.3: BMAD Markdown Parsing to Graph Nodes

As the `coretext` system, I want to parse BMAD-flavored Markdown files, so that their content can be transformed into structured graph nodes and stored in SurrealDB.

**Acceptance Criteria:**
*   Given a BMAD-flavored Markdown file (`.md`) is provided
*   When the parsing engine processes the file
*   Then the file itself is represented as a Root Node (ID=`file_path`). (FR1)
*   And every Markdown header (`#`, `##`, `###`) creates a distinct Graph Node with `CONTAINS` relationship from the file. (FR1)
*   And content under a header is stored as a property of its corresponding Header Node. (FR1)
*   And malformed Markdown syntax results in a "Parsing Error" Node and a rejected update, with the error reported. (FR7)

**Technical Notes:**
*   Implement `coretext/core/parser/markdown.py` with AST parsing logic.
*   Define logic to identify headers, content sections, and map them to graph nodes.
*   Integrate parsing with `GraphManager` to store nodes in SurrealDB.
*   Implement error handling for malformed Markdown.

**Prerequisites:** Story 1.2.

### Story 1.4: Git Repository Change Detection & Synchronization

As a developer, I want my local Markdown changes to be automatically synchronized with the `coretext` knowledge graph upon Git commit, so that the graph always reflects the latest project state without manual intervention.

**Acceptance Criteria:**
*   Given `coretext` is initialized and configured
*   When I make changes to Markdown files within the Git repository
*   And I execute `git commit`
*   Then the `sync.py` pre-commit Git hook detects the changes. (FR2, FR13)
*   And the system processes only the changed Markdown files. (FR3)
*   And the corresponding graph nodes in SurrealDB are updated or created. (FR3, FR4)
*   And the Knowledge Graph state is versioned with the Git commit hash. (FR5)
*   And the hook completes within 1 second for typical commits (1-5 files). (FR14, FR20)

**Technical Notes:**
*   Implement `coretext/core/sync/engine.py` for Git hook logic (using `gitpython`).
*   Develop mechanism to detect changed files.
*   Integrate with `markdown.py` parser and `graph/manager.py` for syncing to DB.
*   Implement versioning strategy using Git commit hashes.
*   Implement performance monitoring for the sync process.

**Prerequisites:** Story 1.3.

### Story 1.5: Referential Integrity & Link Validation

As a `coretext` system, I want to enforce referential integrity within the knowledge graph, so that all links and dependencies between documents are valid and consistent.

**Acceptance Criteria:**
*   Given Markdown files contain Standard Markdown Links (`[Label](./path)`)
*   When the parsing and synchronization process runs
*   Then these links are represented as `PARENT_OF` edges between graph nodes (e.g., H1 -> H2). (FR6)
*   And `coretext` verifies that linked paths exist as valid graph nodes. (FR6)
*   And "Dangling Reference" warnings are triggered during a "dry-run" linting phase before commit (via `coretext lint` or similar mechanism). (FR6)

**Technical Notes:**
*   Enhance `coretext/core/parser/markdown.py` to identify and extract Standard Markdown Links.
*   Modify `coretext/core/graph/manager.py` to create and manage graph edges for these links.
*   Implement validation logic within `coretext/core/sync/engine.py` or a dedicated linter (`coretext/cli/commands.py`) to check for existence of linked nodes.

**Prerequisites:** Story 1.4.

### Story 1.6: Epic 1 Demo & Verification Fixes

As a user (Minh), I want a verified, end-to-end demo guide for Epic 1, along with the necessary system fixes to make it work, so that I can confidently validate the core knowledge graph functionality.

**Acceptance Criteria:**
*   Given the system is built
*   When I follow `docs/epic-1-demo-guide.md`
*   Then I can successfully initialize, start, sync, verify, and stop the system.
*   And the `coretext stop` command exists.
*   And edge creation works without schema errors.

**Technical Notes:**
*   Implement `coretext stop`.
*   Fix `GraphManager` edge ingestion (Schema `SCHEMALESS` fix).
*   Create manual verification guide.

**Prerequisites:** Story 1.5.

---

## Epic 2: Agent Context Retrieval & Semantic Querying

**User Value Statement**: AI agents can retrieve precise, topologically aware context from the knowledge graph, enabling high-quality code generation and informed decision-making.

**PRD Coverage**: FR9, FR10, FR11, FR12.

**Technical Context**:
*   **Architecture**: MCP Server (FastAPI), Semantic Tool Abstraction (wraps SurrealQL queries into high-level tools).
*   **API Design**: MCP Tools exposed via `/mcp/tools/{tool_name}` routes (e.g., `search_topology`, `get_dependencies`).
*   **Project Structure**: `coretext/server/`, `coretext/server/mcp/`, `coretext/core/graph/manager.py` (for semantic graph queries).

**UX Integration**: Improves the AI agent's ability to respond accurately and proactively without manual context provisioning.

**Dependencies**: Epic 1 (Core Knowledge Graph Foundation).

### Story 2.1: MCP Server Setup & Health Check

As a `coretext` developer, I want an MCP server set up with health check endpoints, so that the Gemini CLI can communicate with it and verify its operational status.

**Acceptance Criteria:**
*   Given the `coretext` daemon is running
*   When the Gemini CLI checks `/health`
*   Then the server responds with a 200 OK status.
*   And the server binds only to `127.0.0.1`.
*   And the server exposes an MCP endpoint pattern like `/mcp/tools/{tool_name}`.

**Technical Notes:**
*   Implement `coretext/server/app.py` for FastAPI application definition.
*   Implement `coretext/server/health.py` for the health check endpoint.
*   Configure `uvicorn` to run the FastAPI app, binding to `127.0.0.1`.
*   Ensure the daemon lifecycle management (start/stop) is integrated with CLI.

**Prerequisites:** Epic 1 (all stories).

### Story 2.2: Semantic Tool for Topology Search

As an AI agent, I want a semantic tool to search the knowledge graph for topological connections, so that I can understand project structure and dependencies relevant to my task.

**Acceptance Criteria:**
*   Given the MCP server is running and the graph contains data
*   When the AI agent calls `POST /mcp/tools/search_topology` with a query
*   Then `coretext` uses `nomic-embed-text-v1.5` for query embedding.
*   And `coretext` performs a vector similarity search in SurrealDB.
*   And `coretext` traverses graph relationships to find topologically relevant nodes. (FR10)
*   And `coretext` returns a list of relevant graph nodes (files, headers, entities) as context. (FR11)

**Technical Notes:**
*   Implement `coretext/core/vector/embedder.py` for embedding generation.
*   Ensure the embedder loads from the local cache (prepared in Story 3.1) without internet access.
*   Integrate embedding capabilities into `coretext/core/graph/manager.py` for semantic search.
*   Implement `coretext/server/mcp/routes.py` with the `search_topology` endpoint.
*   Wrap SurrealQL queries within `coretext/core/graph/manager.py` to abstract DB logic.

**Prerequisites:** Story 2.1.

### Story 2.3: Semantic Tool for Dependency Retrieval

As an AI agent, I want a semantic tool to retrieve direct and indirect dependencies for a given node, so that I can understand the impact of changes or prerequisites for implementation.

**Acceptance Criteria:**
*   Given the MCP server is running and the graph contains data
*   When the AI agent calls `POST /mcp/tools/get_dependencies` with a node identifier (e.g., file path, header ID)
*   Then `coretext` traverses `depends_on`, `governed_by`, or `PARENT_OF` edges in the graph. (FR12)
*   And `coretext` returns a structured list of dependent nodes and their relationships. (FR11)
*   And the tool is implemented to handle different types of relationships as defined in the graph schema.

**Technical Notes:**
*   Extend `coretext/core/graph/manager.py` with methods for graph traversal and dependency retrieval.
*   Implement `coretext/server/mcp/routes.py` with the `get_dependencies` endpoint.
*   Ensure the tool can accept various node identifiers and return consistent results.

**Prerequisites:** Story 2.2.

### Story 2.4: MCP Protocol Adherence & Documentation

As a `coretext` system, I want to strictly adhere to the MCP protocol and generate accurate tool definitions, so that AI agents can reliably discover and utilize its capabilities.

**Acceptance Criteria:**
*   Given the MCP server is running
*   When an AI agent inspects the server's capabilities
*   Then all exposed MCP tools (`search_topology`, `get_dependencies`, etc.) are well-documented with docstrings and example I/O. (FR9)
*   And the server generates a valid MCP manifest defining all available tools.
*   And the API adheres to the standard `HTTPException` for errors.

**Technical Notes:**
*   Ensure all FastAPI routes for MCP tools have comprehensive docstrings and Pydantic models for request/response.
*   Implement a mechanism to automatically generate the MCP manifest (potentially using FastAPI's OpenAPI spec).
*   Utilize FastAPI's error handling (`HTTPException`).

**Prerequisites:** Story 2.3.

---

## Epic 3: Developer Workflow Integration & Tooling

**User Value Statement**: Developers can seamlessly integrate `coretext` into their workflow, using CLI tools for management, linting, and inspection, and gaining real-time feedback on project topology.

**PRD Coverage**: FR8, FR15, FR17, FR18, FR19.

**Technical Context**:
*   **Architecture**: Typer-based CLI for user interaction, `Rich` library for enhanced CLI output (spinners, tables, errors).
*   **IPC**: HTTP Health Check + PID File for communication between CLI and Daemon.
*   **CLI Commands**: `coretext inspect <node>`, `coretext lint`, `coretext status`.
*   **Project Structure**: `coretext/cli/` module containing `main.py` and `commands.py`.

**UX Integration**: Direct developer interaction and feedback through intuitive CLI commands.

**Dependencies**: Epic 1 (Core Knowledge Graph Foundation).

### Story 3.1: CLI for `coretext init` and Daemon Management

As a developer, I want to initialize `coretext` and manage its background daemon process via the CLI, so that I can easily set up and control the system.

**Acceptance Criteria:**
*   Given `coretext` is installed
*   When I run `coretext init`
*   Then the SurrealDB binary is downloaded to `~/.coretext/bin/`.
*   And the embedding model (nomic-embed-text-v1.5) is downloaded and cached locally.
*   And `~/.coretext/config.yaml` is created with default settings.
*   And `~/.coretext/schema_map.yaml` is created.
*   And the `coretext` daemon (FastAPI server) is started in the background.
*   And a `daemon.pid` file is created in `.coretext/` with the process ID.
*   When I run `coretext start` or `coretext stop`
*   Then the daemon process is managed accordingly.

**Technical Notes:**
*   Implement `coretext/cli/commands.py` for `init`, `start`, `stop` commands using Typer.
*   Utilize `coretext/db/client.py` for SurrealDB binary download.
*   Use sentence_transformers to pre-download the model to ~/.coretext/cache/ during init.
*   Implement daemon process management (starting/stopping, PID file handling).
*   Use `Rich` for CLI output and spinners during long operations.

**Prerequisites:** Epic 1 (Core Knowledge Graph Foundation), Epic 2 (MCP Server Setup).

### Story 3.2: CLI for `coretext status`

As a developer, I want to check the operational status and health of the `coretext` daemon via the CLI, so that I can quickly verify the system is running correctly.

**Acceptance Criteria:**
*   Given the `coretext` daemon is running
*   When I run `coretext status`
*   Then the CLI pings the daemon's `/health` endpoint.
*   And the CLI displays a clear status message (e.g., "Coretext Daemon Running", "Daemon Stopped", "Sync Hook Active"). (FR17)
*   And relevant information like daemon PID and port are shown.

**Technical Notes:**
*   Implement `coretext/cli/commands.py` for the `status` command.
*   Utilize HTTP client to ping the daemon's health endpoint.
*   Parse and display the daemon's response using `Rich`.

**Prerequisites:** Story 3.1.

### Story 3.3: CLI for `coretext inspect <node>` (Dependency Tree)

As a developer, I want to inspect the dependency tree for a specific project node (e.g., a file or header) via the CLI, so that I can understand its relationships within the knowledge graph.

**Acceptance Criteria:**
*   Given the knowledge graph is populated
*   When I run `coretext inspect <file_path_or_node_id>`
*   Then the CLI queries the daemon for the node's relationships and dependencies. (FR8)
*   And the CLI displays a clear, text-based dependency tree (e.g., parent, children, linked nodes).
*   And the output is formatted for readability using `Rich`.

**Technical Notes:**
*   Implement `coretext/cli/commands.py` for the `inspect` command.
*   The CLI makes a request to the daemon's MCP endpoint (e.g., using the semantic tool from Story 2.3).
*   Daemon uses `coretext/core/graph/manager.py` for graph traversal.
*   CLI formats the returned graph data for console output.

**Prerequisites:** Story 2.3, Story 3.2.

### Story 3.4: CLI for `coretext lint` (Graph Integrity Check)

As a developer, I want to run an integrity check on the knowledge graph and my Markdown files via the CLI, so that I can identify and fix any malformed Markdown or broken links before committing.

**Acceptance Criteria:**
*   Given the knowledge graph is populated
*   When I run `coretext lint`
*   Then the CLI triggers a "dry-run" integrity check within the daemon. (FR15, FR18)
*   And `coretext` identifies malformed Markdown syntax. (FR7)
*   And `coretext` detects "Dangling References" (broken Standard Markdown Links). (FR6)
*   And the CLI displays a clear report of all detected issues, including file paths and line numbers, using `Rich`.

**Technical Notes:**
*   Implement `coretext/cli/commands.py` for the `lint` command.
*   The CLI makes a request to a dedicated daemon endpoint for linting.
*   Daemon utilizes `coretext/core/parser/markdown.py` for parsing and `coretext/core/graph/manager.py` for referential integrity checks.
*   The daemon performs checks without modifying the graph permanently.

**Prerequisites:** Story 1.5, Story 3.2.

### Story 3.5: BMAD Template Provisioning

As a developer, I want to easily generate structured BMAD Markdown files using predefined templates via the CLI, so that I can quickly create new project documentation that is compliant with the knowledge graph schema.

**Acceptance Criteria:**
*   Given `coretext` is installed
*   When I run `coretext new <template_name> <output_path>` (e.g., `coretext new prd docs/new-prd.md`)
*   Then a new Markdown file is created at `output_path` populated with the content of the specified BMAD template. (FR19)
*   And available template names (e.g., `prd`, `architecture`, `epic`) are listed if no `template_name` is provided.

**Technical Notes:**
*   Implement `coretext/cli/commands.py` for the `new` command.
*   Store predefined BMAD templates within the `coretext` package (e.g., `coretext/templates/`).
*   Implement logic to copy and populate template content, potentially resolving placeholders.

**Prerequisites:** Story 3.1.

---

## Epic 4: System Reliability & Performance Optimization

**User Value Statement**: The `coretext` system operates efficiently and reliably in the background, ensuring smooth developer workflow without performance bottlenecks or data integrity issues.

**PRD Coverage**: FR20, FR21, FR22, FR23, FR24.

**Technical Context**:
*   **Architecture**: Robust Daemon lifecycle management, resource caps (memory, CPU priority), "Fail-Open" policy for Git hooks, self-healing routines for graph integrity (e.g., pruning dangling edges).
*   **Implementation**: Asynchronous operations (`async/await`), optimized embedding generation, efficient SurrealDB query execution, `gitpython` for Git interaction.
*   **Project Structure**: Performance considerations integrated across `coretext/core/sync/`, `coretext/server/`, `coretext/db/`, and `coretext/core/vector/`.

**UX Integration**: Invisible background operation that ensures no blocking of Git commits and rapid AI agent query responses.

**Dependencies**: Epic 1 (Core Knowledge Graph Foundation), Epic 2 (Agent Context Retrieval).

### Story 4.1: Git Hook Async Mode & Fail-Open Policy

As a developer, I want `coretext`'s Git hook to operate efficiently without blocking my `git commit` operations, even for large changes or in case of internal errors, so that my workflow remains uninterrupted.

**Acceptance Criteria:**
*   Given the `sync.py` Git hook is active
*   When an incremental sync is predicted to exceed 2 seconds (or configured threshold)
*   Then the `sync.py` hook automatically detaches and switches to Background Async Mode. (FR21)
*   And `git commit` completes immediately.
*   And if `sync.py` encounters a crash, it logs the error and displays a non-blocking warning to the user, allowing `git commit` to proceed.
*   And `coretext` never blocks the user's work due to an internal tool error.

**Technical Notes:**
*   Implement logic within `coretext/core/sync/engine.py` to predict sync duration and trigger async mode.
*   Develop a mechanism for `sync.py` to gracefully detach and run in the background (e.g., using `subprocess.Popen`).
*   Implement robust error handling and logging within `sync.py` for the "Fail-Open" policy.

**Prerequisites:** Story 1.4.

### Story 4.2: MCP Query Latency Optimization

As an AI agent, I want `coretext` to respond to my context queries quickly, so that my "thinking" phase remains fluid and efficient.

**Acceptance Criteria:**
*   Given the MCP server is running and the graph is populated
*   When an AI agent makes a context query (e.g., `search_topology`, `get_dependencies`)
*   Then the total Round-Trip Time (RTT) from request to response is less than 500ms. (FR22)

**Technical Notes:**
*   Optimize SurrealDB queries within `coretext/core/graph/manager.py` for efficiency.
*   Ensure embedding generation (`coretext/core/vector/embedder.py`) is performant.
*   Profile and optimize FastAPI endpoint handling in `coretext/server/mcp/routes.py`.
*   Consider caching strategies for frequently accessed graph data.

**Prerequisites:** Story 2.2, Story 2.3.

### Story 4.3: Resource Consumption Management

As a developer, I want `coretext` to be a "good neighbor" on my local machine, consuming minimal system resources, so that it doesn't negatively impact the performance of other applications.

**Acceptance Criteria:**
*   Given the `coretext` daemon is running
*   When idle, the daemon consumes less than 50MB RAM. (FR23)
*   And background embedding operations run at the lowest process priority (`nice -n 19` on Unix-like systems). (FR24)

**Technical Notes:**
*   Implement memory profiling for the daemon and optimize Python object handling.
*   Use `psutil` or similar libraries to set process priority for background tasks.
*   Ensure `nomic-embed-text-v1.5` is configured for CPU-optimized inference.

**Prerequisites:** Story 1.4, Story 2.2.

### Story 4.4: Graph Self-Healing & Integrity Checks

As a `coretext` system, I want to automatically maintain the integrity of the knowledge graph, so that broken links and outdated nodes don't accumulate and degrade its accuracy over time.

**Acceptance Criteria:**
*   Given the `coretext` daemon starts up
*   When the system initializes
*   Then a self-heal routine runs that scans for and automatically prunes "Dangling Edges" (links to deleted files or nodes).
*   And `coretext` reports any significant graph integrity issues in the logs.

**Technical Notes:**
*   Implement a routine within `coretext/core/graph/manager.py` to identify and remove dangling edges.
*   Integrate this routine into the daemon's startup sequence (`coretext/server/app.py`).
*   Utilize SurrealDB's query capabilities to efficiently identify inconsistent data.

**Prerequisites:** Story 1.5.

---

## FR Coverage Matrix

| FR ID | Description                                                                   | Covering Stories                                                                                                                                                                                                                                                                                             |
| ----- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FR1   | The system can parse BMAD-flavored Markdown files into a structured Knowledge Graph. | Story 1.3: BMAD Markdown Parsing to Graph Nodes                                                                                                                                                                                                                                                              |
| FR2   | The system can detect changes in Markdown files within a Git repository.        | Story 1.4: Git Repository Change Detection & Synchronization                                                                                                                                                                                                                                                 |
| FR3   | The system can synchronize detected Markdown file changes into the Knowledge Graph. | Story 1.4: Git Repository Change Detection & Synchronization                                                                                                                                                                                                                                                 |
| FR4   | The system can store a Knowledge Graph in SurrealDB.                         | Story 1.2: SurrealDB Management & Schema Application, Story 1.4: Git Repository Change Detection & Synchronization                                                                                                                                                                                           |
| FR5   | The system can version the Knowledge Graph state based on Git commit hashes.  | Story 1.4: Git Repository Change Detection & Synchronization                                                                                                                                                                                                                                                 |
| FR6   | The system can enforce referential integrity within the Knowledge Graph.      | Story 1.5: Referential Integrity & Link Validation, Story 3.4: CLI for `coretext lint` (Graph Integrity Check), Story 4.4: Graph Self-Healing & Integrity Checks                                                                                                                                             |
| FR7   | The system can detect and report malformed Markdown syntax.                   | Story 1.3: BMAD Markdown Parsing to Graph Nodes, Story 3.4: CLI for `coretext lint` (Graph Integrity Check)                                                                                                                                                                                                  |
| FR8   | The system can output a text-based dependency tree for a given node.          | Story 3.3: CLI for `coretext inspect <node>` (Dependency Tree)                                                                                                                                                                                                                                               |
| FR9   | The system can receive context queries from an AI Agent via an MCP Server.      | Story 2.1: MCP Server Setup & Health Check, Story 2.4: MCP Protocol Adherence & Documentation                                                                                                                                                                                                                |
| FR10  | The system can retrieve precise, topologically relevant context.                | Story 2.2: Semantic Tool for Topology Search                                                                                                                                                                                                                                                                 |
| FR11  | The system can provide retrieved context to the AI Agent via the MCP Server.    | Story 2.2: Semantic Tool for Topology Search, Story 2.3: Semantic Tool for Dependency Retrieval                                                                                                                                                                                                              |
| FR12  | The system can traverse graph relationships.                                 | Story 2.3: Semantic Tool for Dependency Retrieval                                                                                                                                                                                                                                                            |
| FR13  | The system can integrate as a pre-commit Git hook.                            | Story 1.4: Git Repository Change Detection & Synchronization                                                                                                                                                                                                                                                 |
| FR14  | The system can execute a synchronization process on `git commit`.             | Story 1.4: Git Repository Change Detection & Synchronization                                                                                                                                                                                                                                                 |
| FR15  | The system can run a "dry-run" integrity check.                               | Story 3.4: CLI for `coretext lint` (Graph Integrity Check)                                                                                                                                                                                                                                                   |
| FR16  | The system can provide a CLI for system initialization.                       | Story 1.1: Project Initialization & Core Scaffolding, Story 3.1: CLI for `coretext init` and Daemon Management                                                                                                                                                                                             |
| FR17  | The system can provide a CLI for viewing synchronization health.                | Story 3.2: CLI for `coretext status`                                                                                                                                                                                                                                                                         |
| FR18  | The system can provide CLI commands for linting graph integrity.              | Story 3.4: CLI for `coretext lint` (Graph Integrity Check)                                                                                                                                                                                                                                                   |
| FR19  | The system can provide structured templates for creating BMAD Markdown files.   | Story 3.5: BMAD Template Provisioning                                                                                                                                                                                                                                                                        |
| FR20  | The system can complete incremental graph synchronization within a time limit.  | Story 1.4: Git Repository Change Detection & Synchronization                                                                                                                                                                                                                                                 |
| FR21  | The system can perform graph synchronization asynchronously for large commits.  | Story 4.1: Git Hook Async Mode & Fail-Open Policy                                                                                                                                                                                                                                                            |
| FR22  | The system can respond to Agent context queries within a time limit.          | Story 4.2: MCP Query Latency Optimization                                                                                                                                                                                                                                                                    |
| FR23  | The system can operate within defined memory consumption limits.              | Story 4.3: Resource Consumption Management                                                                                                                                                                                                                                                                   |
| FR24  | The system can perform background processing with low CPU priority.           | Story 4.3: Resource Consumption Management                                                                                                                                                                                                                                                                   |

---

## Summary

The `coretext` epic and story breakdown is now complete, encompassing 4 epics and 18 detailed stories. This plan provides a comprehensive roadmap for implementing a local-first, AI-enhanced development platform that solves the "Lost in the Middle" context problem in LLM-assisted software engineering.

**Full Context Incorporated:**
- ✅ PRD functional requirements and scope
- ✅ Architecture technical decisions and contracts
- ✅ UX Design interaction patterns and specifications (where applicable for a CLI tool)

**FR Coverage:** All 24 functional requirements from the PRD are fully mapped to specific stories, ensuring complete coverage.

**Epic Structure:** 4 epics are defined, delivering incremental user value and respecting technical dependencies.

**Ready for Phase 4:** Sprint Planning and Development Implementation

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._

_This document will be updated after UX Design and Architecture workflows to incorporate interaction details and technical decisions._


