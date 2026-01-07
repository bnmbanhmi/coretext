---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
inputDocuments: []
workflowType: 'prd'
lastStep: 11
project_name: 'coretext'
user_name: 'Minh'
date: '2025-12-03'
---

# Product Requirements Document - coretext

**Author:** Minh
**Date:** 2025-12-03

## Executive Summary

**coretext** is a local-first, AI-enhanced development platform designed to solve the "Lost in the Middle" context problem in LLM-assisted software engineering. By treating Markdown specifications (structured via BMAD) as the Source of Truth and automatically synchronizing them into a SurrealDB-based Knowledge Graph, `coretext` bridges the gap between human intent and machine understanding.

The system acts as a "Translator" and "Memory Layer," enabling a "Dual-Context" workflow: humans define architecture and requirements in standard files (VSC/Git), while an intelligent background process converts these into a semantic graph (Vectors + Relations). This allows the Gemini CLI Coding Agent to query the *structure* and *topology* of the project via an MCP Server, ensuring high-precision code generation and refactoring that respects the broader system architecture.

### What Makes This Special

*   **Topology Awareness vs. Symbolic Search:** Unlike traditional search that matches keywords, `coretext` understands the graph relationships (edges/links) between Epics, Tasks, and Files, allowing the agent to navigate the "shape" of the codebase.
*   **Implicit Synchronization:** The `sync.py` git hook uses Merkle Trees and AST parsing to incrementally update the knowledge base without manual user intervention.
*   **Dual-Context Access:** Provides a unified interface where the Human view (Files) and Agent view (Graph/Vectors) remain perfectly synced, enabling seamless collaboration.
*   **Local-First & Private:** Built on local file systems and local DB instances, ensuring data privacy and offline capability.

## Project Classification

**Technical Type:** Developer Tool
**Domain:** AI & Knowledge Management
**Complexity:** High

**Complexity Drivers:**
*   **Hybrid Search Architecture:** Combining Vector (Semantic), Graph (Relational), and Lexical search in SurrealQL.
*   **AST-Based Parsing:** Semantic chunking of Markdown based on syntax trees rather than simple line splitting.
*   **State Synchronization:** ensuring strict consistency between the Git file system and the Database state using Merkle Trees.

## Success Criteria

### User Success

*   **Contextual Confidence:** The user experiences a psychological shift from micromanaging the AI's context to trusting its "Second Brain." This is achieved when the AI proactively references architectural constraints or dependencies defined in files *not* manually provided in the immediate chat window.
*   **The "Aha!" Moment:** The user realizes they no longer need to copy-paste reference files. The "Lost in the Middle" anxiety vanishes as they witness the system's "Topology Awareness" connecting discrete documents automatically.
*   **Zero Context Anxiety:** Users feel their project is a cohesive, living organism. Documentation and code are no longer fragmented, leading to a sense of control and reduced cognitive load.

### Business Success

*   **Token ROI (Context Efficiency):** Drastic reduction in input tokens per task. The system injects only precise graph nodes rather than dumping full files, maximizing the value of the limited context window.
*   **Autonomous Trust Level:** Measured by the user's willingness to step away during generation. Success is achieved when the user assumes the AI has the necessary context without verification.
*   **First-Pass Success Rate:** Higher frequency of functional code generated on the first attempt, driven by strict adherence to dependencies and architectural patterns defined in BMAD.

### Technical Success

*   **Zero-Touch Synchronization:** The `sync.py` git hook operates invisibly, handling AST parsing and Merkle Tree updates post-commit without interrupting the developer's workflow.
*   **High-Precision Retrieval (Signal-to-Noise):** The MCP server delivers "Top-K" relevance, filtering out noise to ensure the context window is populated only with high-value, architecturally relevant information.

### Measurable Outcomes

*   **Reduction in Manual Context Loading:** Users stop manually pasting file contents into the chat.
*   **Reduction in Hallucinated Dependencies:** Code generation references correct, existing project modules.
*   **Seamless Sync:** Database state remains consistent with Git state without manual intervention.
*   **Gemini Extension Native:** The tool is verified to install and function seamlessly as a `gemini` extension.
*   **MCP Compliance:** The server passes standard MCP protocol validation tests.

## Product Scope

### MVP - Minimum Viable Product

**The Core Loop**
*   **Input:** Support for structured Markdown files (BMAD templates).
*   **Process:** Automatic extraction and synchronization to SurrealDB via Git Hooks (AST parsing).
*   **Output:** A functional Gemini CLI Coding Agent capable of querying the DB via MCP to answer topology questions (e.g., "What stories depend on this Epic?") and generate code based on that retrieved structure.

### Growth Features (Post-MVP)

**Context Optimization**
*   **Intelligent Context Filtering:** Advanced logic to select the absolute minimum viable context, optimizing for speed and cost while further minimizing hallucinations.
*   **Visual Topology Exploration:** Tools for the human user to visualize the graph relationships stored in the DB.

### Vision (Future)

**Graph-Grounded Autonomy**
*   **Virtual Software Engineer:** Evolution into a fully autonomous agent (or team) that creates and maintains its own knowledge graph. The system doesn't just read code; it "understands" the project's evolving structure like a human lead architect.

## User Journeys

### Journey 1: Sarah, The Architect (Human) - "Structuring the Chaos"
**Role:** Senior Software Engineer / PM
**Goal:** Define project architecture and ensuring adherence without micromanagement.
**The Challenge:** Sarah is tired of explaining the same architectural patterns to her team (and AI assistants) repeatedly. Documents get ignored, and context is lost in chat windows.

**The Journey:**
1.  **Setup:** Sarah initializes `coretext` in her repo. She creates a `docs/architecture.md` file using a BMAD template, defining a strict "Service-Repository" pattern.
2.  **The Invisible Sync:** She commits the file: `git commit -m "Add architecture specs"`. Behind the scenes, `coretext`'s hook triggers. It parses her Markdown, extracts the "Service-Repository" pattern as a graph node, and upserts it to SurrealDB. She sees a subtle "Knowledge Graph Updated" success message in her terminal.
3.  **The Payoff:** Later, she asks the Gemini Agent to "scaffold a new User feature." She *doesn't* paste the architecture doc.
4.  **Resolution:** The Agent replies: "I see from `architecture.md` that we use the Service-Repository pattern. I have created `UserService` and `UserRepository` accordingly." Sarah smiles. The system "learned" her rules automatically. Her "Contextual Confidence" is high.

### Journey 2: Unit-734, The Coding Agent (Machine User) - "Navigating the Graph"
**Role:** Gemini CLI Agent (via MCP)
**Goal:** Retrieve precise context to answer a user query without hallucinating.
**The Challenge:** The user asked: "Refactor the payment logic." The Agent has zero context about where payment logic lives or what depends on it. A standard RAG search might return outdated wiki pages.

**The Journey:**
1.  **The Query:** The Agent receives the prompt "Refactor payment logic." It calls the `coretext` MCP tool: `search_knowledge_graph(query="payment logic", type="topology")`.
2.  **Traversing the Graph:** The `coretext` server doesn't just search text. It traverses the graph:
    *   Finds `payment-service.ts` (Vector match).
    *   Follows the `depends_on` edge to `stripe-adapter.ts`.
    *   Follows the `governed_by` edge to `compliance-policy.md` (PCI-DSS rules).
3.  **Context Assembly:** The MCP server returns a concise packet: "Target: `payment-service.ts`. Dependency: `stripe-adapter.ts`. Constraint: Must adhere to PCI-DSS (from `compliance-policy.md`)."
4.  **Resolution:** Unit-734 generates the refactor, explicitly adding a comment: `// Compliance: Masking card data per PCI-DSS policy`. It "knew" constraints that weren't in the prompt.

### Journey 3: Leo, The Contributor (Human) - "Flow without Friction"
**Role:** Junior Developer
**Goal:** Implement a feature without breaking the build or ignoring docs.
**The Challenge:** Leo is nervous. He doesn't know the whole codebase. He makes a change to a local Markdown file to track his progress but forgets to update the central wiki.

**The Journey:**
1.  **The Work:** Leo edits `docs/tasks/feature-X.md`, marking a checkbox as `[x] Completed`.
2.  **The Commit:** He runs `git commit`. He has no idea `coretext` exists.
3.  **The Safety Net:** The `sync.py` hook runs instantly. It detects the change in the task status and updates the parent Epic node in the DB.
4.  **The Collaboration:** Five minutes later, Sarah (The Architect) queries the Agent: "What is the status of Feature X?" The Agent queries the DB and reports: "Leo marked Feature X as completed 5 minutes ago."
5.  **Resolution:** Leo didn't have to log into a separate Jira-like tool. His code commit *was* his status update. His code commit *was* his status update. He stays in his flow.

### Journey Requirements Summary

**Capabilities Revealed:**
*   **For Sarah (Architect):** BMAD Template parsing, AST extraction of specific patterns (not just text), invisible "git-hook" trigger.
*   **For Unit-734 (Agent):** MCP Server with specialized tools (`topology_search`, `get_dependencies`), graph traversal logic (following edges like `depends_on`).
*   **For Leo (Contributor):** Low-latency sync (must be fast so `git commit` doesn't hang), seamless integration (zero manual configuration for contributors).

## Domain-Specific Requirements

### AI & Knowledge Management Compliance Overview
Since `coretext` acts as the "Brain" for an autonomous coding agent, it operates in the high-complexity domain of **Knowledge Engineering and AI Reliability**. The primary domain challenge is ensuring that the "Machine Understanding" (Graph) is a 100% accurate, deterministic reflection of the "Human Intent" (Files). Any drift between these two contexts leads to "AI Hallucination," which defeats the product's purpose. Therefore, we adopt a **"Strict Schema, Loud Failures"** philosophy.

### Key Domain Concerns
*   **Reproducibility:** Ensuring the Knowledge Graph is a deterministic function of the file system state.
*   **Validation:** Verifying the integrity of the translation from Markdown to Graph nodes.
*   **Accuracy:** Ensuring structural preservation during parsing (Nodes/Edges) rather than probabilistic guessing.
*   **Performance:** Maintaining "Non-Blocking Flow" for the developer despite heavy background processing.
*   **Resources:** Adhering to a "Good Neighbor Policy" on the user's local machine.

### Compliance Requirements
**1. State Determinism via Git**
*   **Requirement:** The database state must be a deterministic projection of the file system.
*   **Mechanism:** We use the Git Commit Hash as the version stamp. For identical file content (same hash), the system must produce a mathematically identical Graph structure (Merkle Tree logic).

**2. Strict Schema, Loud Failures**
*   **Requirement:** No "fuzzy" parsing of structural elements. A `## Header` is a Node. A Standard Markdown Link (`[Label](./path)`) is an Edge.
*   **Constraint:** Malformed Markdown (broken syntax) must result in a **"Parsing Error" Node** and a rejected update, rather than a "best guess" by the parser. The failure must be visible to the Agent and User.

### Industry Standards & Best Practices
*   **Referential Integrity (Shift-Left):** "Dangling Reference" warnings must be triggered during a "dry-run" linting phase before commit, preventing the creation of broken graph edges.
*   **AST-Based Parsing:** We reject "Split by Character Count" chunking in favor of Abstract Syntax Tree parsing to preserve semantic boundaries.

### Required Expertise & Validation
**Validation Methodology**
*   **Deterministic Test Suite:** The `sync.py` parser requires a test suite of varied Markdown inputs (valid, malformed, edge cases) that asserts the JSON output is exact.
*   **Auditability (Trust via Visibility):** The system must provide a `coretext inspect <filename>` CLI command to output a text-based dependency tree, allowing humans to verify the graph's "truth" against the file content.

### Implementation Considerations
**Performance & Resources (The "Good Neighbor" Policy)**
*   **Sync Latency:** `sync.py` hook must complete in **< 1 second** for typical commits (1-5 files). Large commits (>10 files) must shift to "Async Mode" (background thread).
*   **Query Latency:** MCP Server response target is **< 500ms**.
*   **Resource Caps:** Hard limit of **500MB RAM** for the background daemon. Embedding operations run at lowest process priority (`nice -n 19`).
*   **Model Selection:** Use quantized, CPU-optimized embedding models (e.g., `all-MiniLM-L6-v2`) to avoid heavy GPU dependency.

## Innovation & Novel Patterns

### Detected Innovation Areas
*   **Executable Documentation (Active Constraints):** Moving beyond documentation as "dead text." `coretext` treats Markdown specifications (BMAD) as source code that is "compiled" into a Knowledge Graph. This graph actively constrains the AI Agent, ensuring that architectural decisions (e.g., "Use PostgreSQL") are enforced as graph edges rather than just probabilistic text suggestions.
*   **The Knowledge Compiler Metaphor:** `sync.py` acts as a compiler that translates Human Intent (High-Level Natural Language) into Machine Actionable Topology (Graph/Vector Machine Code). This creates a deterministic bridge between the developer's specs and the AI's execution environment.
*   **"Context Pull" Paradigm:** Inverting the standard workflow. Instead of humans manually "pushing" files into the context window ("Context Stuffing"), `coretext` enables the AI to "pull" precise, topologically relevant context from the graph. This shifts the human's role from "Context Manager" to "Spec Author."

### Market Context & Competitive Landscape
*   **Current Landscape:** Most AI coding tools (Cursor, Copilot) rely on RAG (Retrieval Augmented Generation) which uses vector similarity search. This is probabilistic and often "hallucinates" or misses structural relationships.
*   **Differentiation:** `coretext` introduces **Topology Awareness**. By parsing the AST and building a Graph, it understands *relationships* (A depends on B), not just *keywords*. This makes it a "Second Brain" rather than just a "Smart Search Bar."
*   **New Category:** "AI-Native Knowledge Management." It bridges the gap between Documentation Tools (Notion, Obsidian) and AI Coding Assistants.

### Validation Approach
*   **The "Constraint Test":** Write a rule in a Markdown file (e.g., "All API responses must be wrapped in `ApiResponse<T>`"). Ask the Agent to generate an endpoint *without* providing that file in the chat. If the Agent generates code violating the wrapper, the innovation fails. If it respects the wrapper by pulling the graph node, the innovation is validated.
*   **The "Refactor Test":** Change a dependency in the Graph (e.g., rename a Service). Ask the Agent to "update all callers." Validates if the Agent can traverse the graph to find all dependent files.

### Risk Mitigation
*   **"Compiler Error" Handling:** Innovation Risk: The parser is too strict and rejects valid but slightly non-standard Markdown, frustrating users. **Mitigation:** Implement "Soft Warnings" vs "Hard Errors" and a `coretext lint` command to guide users to write compliant BMAD.
*   **Sync Latency Perception:** Innovation Risk: The background "compilation" feels slow. **Mitigation:** Optimistic UI updates in the VS Code extension (if built) or fast CLI feedback ("Graph updated in 300ms").

## Developer Tool Specific Requirements

### Project-Type Overview
`coretext` is fundamentally a developer tool designed to enhance the agent-assisted software development workflow. Its core functionality revolves around transforming human-readable Markdown specifications (BMAD flavor) into a machine-actionable Knowledge Graph. It prioritizes a "Markdown-First" strategy, where the structured text acts as the primary source of truth for architectural and project topology.

### System Architecture and Definitions

#### 1. The Integration Model: Gemini CLI Extension
Instead of just a standalone script, Coretext must be designed as a Gemini CLI Extension.

*   **Definition:** A packaged extension that extends the Gemini CLI capabilities via the `gemini` command and registers an MCP Server.
*   **Why:** To allow users to run commands like `gemini coretext status` or `gemini coretext index` directly from their workflow.
*   **Ref:** Follows the pattern at https://geminicli.com/docs/extensions/.

#### 2. The Workspace Structure (Separation of Concerns)
We must define a strict folder separation to avoid conflicts with BMAD:

*   **`/.bmad/` (Managed by BMAD):** Contains Agent definitions, Personas, and Workflow prompts. Coretext READS this but does not own it.
*   **`/.coretext/` (Managed by Coretext):** A new hidden directory to store:
    *   The local Knowledge Graph (`surreal.db`).
    *   Sync logs and lockfiles.
    *   `config.yaml` for the `sync.py` hook.
*   **`/docs/` (Shared):** The Markdown Source of Truth.

#### 3. Updated Tool Definitions (for Context)

*   **Gemini CLI:** The orchestration engine. It loads the coretext extension to gain "Topology Awareness."
*   **BMAD:** The Data Protocol. It provides the Schema (Epics, Stories) that Coretext indexes. Coretext is the Engine that makes BMAD "executable."
*   **MCP (Model Context Protocol):** The standard communication layer. Coretext exposes a Custom MCP Server (Python-based) that wraps SurrealDB queries into semantic tools like `get_related_nodes()`.

#### 4. Installation Flow Update
Change the distribution model description:

*   **Hybrid Distribution:** The Core Engine (`sync.py`) is Python/pip. The Interface is a Gemini CLI Extension that wraps the engine.

### IDE Integration (Loose Coupling, Tight Feedback)
*   **MVP (Git-Native):** The primary integration point is the **Terminal**, with "invisible" functionality provided by **pre-commit Git hooks**.
*   **Visual Studio Code (Frontend for Authors):**
    *   **Phase 1:** Provision of a `coretext.json` tasks configuration for VS Code users to easily run `sync` and `check` commands.
    *   **Phase 2 (Growth):** Development of a dedicated **VS Code Extension** to enable "Loud Failures" through real-time linting for BMAD files (e.g., red squiggly lines for broken Standard Markdown Links or missing required headers), allowing architects to fix graph integrity issues before committing.

### API Surface & Documentation
*   **Primary API Surface (Machine User):** The **MCP Server (Model Context Protocol)** serves as the interface for "Machine Users" (i.e., the Gemini CLI Coding Agent) to query the `coretext` knowledge graph.
*   **Secondary API Surface (Human User - CLI):** A robust **Command-Line Interface (CLI)** provides tools for human users to inspect and manage the knowledge graph:
    *   `coretext status`: View graph synchronization health.
    *   `coretext inspect <node>`: View dependencies and relationships of a specific node.
    *   `coretext lint`: Check for graph integrity errors and report them.
*   **Documentation & Examples:** A **"Reference Repo"** (e.g., a "To-Do App" built with BMAD) is essential to demonstrate the ideal `docs/` folder structure and provide practical, executable examples for user adoption.

## Functional Requirements

### Knowledge Graph Management

*   FR1: The system can parse BMAD-flavored Markdown files into a structured Knowledge Graph.
*   FR2: The system can detect changes in Markdown files within a Git repository.
*   FR3: The system can synchronize detected Markdown file changes into the Knowledge Graph.
*   FR4: The system can store a Knowledge Graph in SurrealDB.
*   FR5: The system can version the Knowledge Graph state based on Git commit hashes.
*   FR6: The system can enforce referential integrity within the Knowledge Graph (e.g., verifying Standard Markdown Links).
*   FR7: The system can detect and report malformed Markdown syntax that prevents successful parsing.
*   FR8: The system can output a text-based dependency tree for a given node.

### Agent Context Retrieval

*   FR9: The system can receive context queries from an AI Agent via an MCP Server.
*   FR10: The system can retrieve precise, topologically relevant context from the Knowledge Graph based on Agent queries.
*   FR11: The system can provide retrieved context to the AI Agent via the MCP Server.
*   FR12: The system can traverse graph relationships (e.g., `depends_on`, `governed_by`) to gather comprehensive context.

### Developer Workflow Integration

*   FR13: The system can integrate as a pre-commit Git hook.
*   FR14: The system can execute a synchronization process on `git commit`.
*   FR15: The system can run a "dry-run" integrity check on Markdown files before commit.
*   FR16: The system can provide a command-line interface (CLI) for system initialization.
*   FR17: The system can provide a CLI for viewing synchronization health.
*   FR18: The system can provide CLI commands for linting graph integrity.
*   FR19: The system can provide structured templates for creating BMAD Markdown files.

### System Reliability & Performance

*   FR20: The system can complete incremental graph synchronization within a specified time limit for small commits.
*   FR21: The system can perform graph synchronization asynchronously for large commits.
*   FR22: The system can respond to Agent context queries within a specified time limit.
*   FR23: The system can operate within defined memory consumption limits.
*   FR24: The system can perform background processing with low CPU priority.

## Non-Functional Requirements

### Performance (The "Blink of an Eye" Standard)

*   **Sync Latency (Pre-commit Hook):**
    *   **Target:** Less than 1000ms (1 second) for incremental commits involving fewer than 10 files.
    *   **Constraint:** If processing predicts exceeding 2000ms, the `sync.py` hook must automatically detach and switch to Background Async Mode, allowing the `git commit` to complete immediately while indexing continues silently.
*   **MCP Query Latency:**
    *   **Target:** Less than 500ms total Round-Trip Time (RTT) from receiving the AI Agent's request to returning the JSON context packet. This ensures the Agent's "thinking" phase remains fluid.
*   **Daemon Footprint:**
    *   **Cold Start:** The background process (daemon) must initialize (load DB connection + Embedding model) in less than 2 seconds.
    *   **Idle Usage:** Less than 50MB RAM when not actively indexing or responding to queries.

### Scalability (Codebase Capacity)

*   **Repository Size:** `coretext` must support repositories containing up to 10,000 Markdown and Code files without degradation in query latency or sync performance targets.
*   **Graph Density:** Capable of handling 100,000+ Graph Edges (representing dependencies and links) on standard consumer hardware (e.g., MacBook Air M1 base model) while maintaining performance NFRs.

### Reliability (The "Fail-Open" Policy)

*   **Git Hook Safety:** If `sync.py` encounters a crash (e.g., Python environment error, SurrealDB lock), it must operate with a "Fail-Open" policy.
    *   **Behavior:** It must log the error to `coretext.log`, display a non-blocking warning to the user (e.g., `[Coretext Warning] Sync failed - queuing for retry`), and allow the `git commit` to proceed without interruption. `coretext` must never block the user's work due to an internal tool error.
*   **Graph Integrity:** The system must include a self-heal routine on startup that scans for and automatically prunes "Dangling Edges" (links to deleted files or nodes).

### Security (Local Sovereignty)

*   **Data Perimeter:** Strict adherence to a "Local-First" policy. No file content, vector embeddings, or graph topology data is ever transmitted to a cloud server.
*   **Telemetry:** Telemetry is strictly opt-in and metadata-only, ensuring user privacy and local data residency.
*   **Database Isolation:** The SurrealDB instance must bind strictly to `127.0.0.1` and accept connections only from the local authenticated user process, preventing unauthorized network access.