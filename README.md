# CoreText

> **The Missing Context Layer for AI Agents**

**CoreText** is a local-first, AI-native knowledge graph that automatically synchronizes with your Git repository. It solves the "Lost in the Middle" problem for AI coding agents by providing a structured, topologically-aware "Second Brain" that bridges the gap between your files and the AI's understanding.

---

## Why CoreText?

AI agents struggle with large codebases. RAG (Retrieval Augmented Generation) helps, but it often misses the *structure* of your project—the dependencies between files, the hierarchy of documents, and the architectural constraints defined in your specs.

**CoreText changes this by:**
1.  **Treating Markdown as Source Code**: It parses your documentation (specs, architecture, stories) into a structured graph, not just text chunks.
2.  **Invisible Synchronization**: A `git hook` ensures your knowledge graph is always perfectly synced with your codebase. No manual updates required.
3.  **Hybrid Search**: Combines **Vector Search** (Meaning) with **Graph Traversal** (Topology) to give agents precise context.
4.  **Local & Private**: Everything runs locally on your machine using [SurrealDB](https://surrealdb.com). No data leaves your perimeter.

---

## Key Features

*   **⚡ Git-Native Sync**: Automatically updates the graph on every `git commit`.
*   **🧠 Hybrid Retrieval**: Semantic search + Graph dependency traversal.
*   **🤖 Agent-Ready (MCP)**: Exposes a Model Context Protocol (MCP) server for Claude, Gemini, and other agents.
*   **🛡️ Integrity Checks**: Lints your graph for broken links and dangling references before you commit.
*   **📍 Topology Awareness**: Understands `depends_on`, `parent_of`, and `references` relationships.

---

## Available Tools

CoreText provides two distinct sets of tools: standard CLI commands for system management and "Thick Tools" for AI agents via the MCP server.

### 1. CoreText CLI Tools
These are "Outer Loop" tools for system lifecycle, file operations, and infrastructure management. Available in your terminal via `coretext <command>`.

*   **`init`**: Initializes the project, configuration, database binary, and embedding model.
*   **`start` / `stop`**: Manages the background daemon (SurrealDB + MCP Server).
*   **`status`**: Checks the health of the database and server.
*   **`sync`**: Manually synchronizes Markdown files to the graph.
*   **`new`**: Generates structured documentation from built-in BMAD templates (e.g., `coretext new story ...`).
*   **`lint`**: Runs integrity checks on your knowledge graph (broken links, schema violations).
*   **`inspect`**: Visualizes the dependency tree of a specific node in the terminal.
*   **`apply-schema`**: Applies database schema updates.
*   **`install-hooks`**: Installs Git hooks for automatic synchronization.

### 2. Gemini & MCP Exclusive Tools
These are "Inner Loop" tools designed for **AI Agents**. They are exposed via the Model Context Protocol (MCP) and are **not** available as standalone CLI commands because they require the persistent state of the MCP server (loaded embedding models, active database connections) to function efficiently.

*   **`query_knowledge` (The "Thick Tool")**:
    *   **Function:** A universal context retrieval engine. It combines **Vector Search** (Semantic), **Regex/Keyword Filtering**, and **Graph Traversal** in a single round-trip.
    *   **Why Exclusive?** It requires the embedding model (~300MB) to be resident in memory for sub-second performance. Running this via CLI would incur a massive "cold start" penalty (3-10s) per query.
*   **`search_topology`**:
    *   **Function:** Performs hybrid semantic search to find "Anchor Nodes" relevant to a natural language query.
    *   **Why Exclusive?** Relies on the same resident embedding model as `query_knowledge`.
*   **`get_dependencies`**:
    *   **Function:** Retrieves direct and indirect dependencies for a node in structured JSON format.
    *   **Note:** The CLI `inspect` command wraps this tool for human-readable output, but the raw tool is optimized for Agent consumption.

---

## Installation

CoreText is a Python application managed via `poetry`.

```bash
# Clone the repository
git clone https://github.com/bnmbanhmi/coretext.git
cd coretext

# Install dependencies
poetry install
```

---

## Quick Start

### 1. Initialize the Project
Sets up the local SurrealDB instance, downloads the embedding model, and configures the project. You will be prompted to choose a directory (e.g., `docs`, `wiki`, or `_coretext-knowledge`) to serve as your knowledge graph.

```bash
poetry run coretext init
```

### 2. Start the Daemon
Runs the SurrealDB database and the MCP Server in the background.

```bash
poetry run coretext start
```

### 3. Check Status
Verifies that the daemon is running and healthy.

```bash
poetry run coretext status
```

### 4. Create Content
Use built-in templates to create structured documentation inside your configured knowledge directory (e.g., `_coretext-knowledge`).

```bash
poetry run coretext new story _coretext-knowledge/my-new-feature.md
```

### 5. Inspect the Graph
Visualize the dependencies of any file or node.

```bash
poetry run coretext inspect _coretext-knowledge/my-new-feature.md
```

---

## Connecting an AI Agent (MCP)

CoreText exposes a **Model Context Protocol (MCP)** server at `http://localhost:8001/mcp`. You can connect any MCP-compliant agent (like Claude Desktop or Gemini CLI) to give it access to your knowledge graph.

### Gemini CLI Extension

To install CoreText as a native extension in the Gemini CLI:

```bash
# Ensure the daemon is running
poetry run coretext start

# Link the extension from the project root (Development Mode)
gemini extensions link .

# Verify installation
gemini extensions list
```

Once linked, verify the connection:
```bash
gemini mcp list
```
You should see `✓ coretext ... - Connected`. The Gemini Agent will now automatically discover and use the CoreText tools:
*   **`search_topology`**: Semantic search across files and headers.
*   **`get_dependencies`**: Analyze relationships between components.
*   **`query_knowledge`**: Universal context retrieval for complex queries.

#### Capabilities Exposed
*   **Knowledge Query**: Ask "What does the Flux Capacitor depend on?" and the agent will use `search_topology` or `get_dependencies` to find the answer from your synced docs.
*   **Structure Analysis**: The agent can visualize your project's knowledge graph topology.
*   **Commands**: Run any CoreText command (e.g., `status`, `sync`, `lint`) directly via the Gemini prompt.

---

## Architecture

CoreText operates as a background daemon composed of:

1.  **Sync Engine**: Watches your Git repository and uses AST parsing to transform Markdown files into graph nodes.
2.  **SurrealDB**: A multi-model database storing the graph (nodes/edges) and vector embeddings.
3.  **MCP Server**: A FastAPI server that provides the interface for AI agents.

### Data Model
*   **Nodes**: Files (`.md`) and Headers (`# H1`, `## H2`).
*   **Edges**: `contains` (File -> Header), `parent_of` (H1 -> H2), `references` (Link -> Target).

---

## Development & Contributing

### Running Tests
```bash
poetry run pytest
```

### Linting
```bash
poetry run coretext lint
```

### Manual Sync
If you need to force a sync without committing:
```bash
poetry run coretext sync
```

---

## License

[MIT License](LICENSE)