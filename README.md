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

# Install the extension from the project root
gemini extensions install .
```

Once installed, the Gemini Agent will automatically discover the `query_knowledge` tool and use it to answer questions about your project structure and documentation.

### Capabilities Exposed:
*   `search_topology(query: str)`: Finds nodes semantically related to a concept.
*   `get_dependencies(node_id: str)`: Retrieves the dependency tree for a specific file or concept.

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