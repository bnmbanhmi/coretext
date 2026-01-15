## **REPORT: ENHANCING AGENTIC AGILE SOFTWARE DEVELOPMENT VIA KNOWLEDGE GRAPH INTEGRATION**

## **Chapter I. Introduction**

### **1.1. Problem Statement**

In modern software engineering, documentation serves as the "source of truth" for autonomous AI agents. However, traditional documentation methods relying on disconnected, unstructured text files (e.g., Markdown) present significant challenges as project complexity scales. This challenge is diagnosed as a failure occurring at three distinct layers:

1.  **Model Level (Context Window Overload):** Feeding entire documentation repositories into Large Language Models (LLMs) leads to high token costs and the "Lost in the Middle" phenomenon, where models struggle to retrieve information from the middle of long contexts.
2.  **Tool Level (Flat-File Blindness):** Current tools (search, grep, ls) treat documents and knowledge as **flat, disconnected files**. They fail to capture the semantic and topological relationships (dependencies, references, hierarchies) between requirements, design, and implementation.
3.  **Context Level (The Autonomy Gap):** Even with structured methodologies like **BMad**—which organizes files into Epics and Stories—the system remains **insufficient for full autonomy**. The "Mental Model" of the project (the connections between an Epic and its specific code implementation) remains implicit in the files or the human operator's mind. Without an explicit, machine-navigable state machine, autonomous agents cannot self-direct effectively.

### **1.2. Research Objective**

This research proposes a methodological improvement to the BMad Agentic Agile framework by integrating a **Knowledge Graph** layer named **CoreText**. The objective is to resolve the three-level problem by:

1.  **Context:** Transforming static, unstructured documentation into a dynamic, structured graph database (SurrealDB).
2.  **Tool:** Providing agents with "Thick Tools" (MCP) that allow them to traverse relationships (e.g., "Find all stories linked to this Epic") rather than just matching text.
3.  **Model:** Delivering precise, topologically relevant subgraphs to the LLM, thereby solving the context window overload.

### **1.3. Scope of Research**

The research focuses on the **Specification, Design, and Testing** phases of the software lifecycle. It specifically targets the transition from human-written specifications (Artifacts) to machine-readable context (Graph Nodes/Edges) to support automated implementation.

### **1.4. Methodology Overview**

The approach combines **Docs-as-Code** principles with **Graph Theory**. A pipeline is proposed where documentation artifacts are parsed into semantic nodes, linked by explicit relationships, and exposed to agents via the **Model Context Protocol (MCP)**.

---

## **Chapter II. Theoretical Background & Technology Stack**

### **2.1. The Anatomy of a Coding Agent**

Contemporary AI engineering faces a fundamental constraint: LLMs operate under strict context window limits. Simply ingesting entire repositories leads to high latency, prohibitive costs, and the "Lost in the Middle" phenomenon. Therefore, the efficacy of an AI Agent is defined via the function:

$Performance \= f(Model, Tools, Context)$.

#### **2.1.1. Model**

The underlying LLM (e.g., GPT, Claude, Gemini).

- Role: Logic processing, code generation, natural language understanding.  
- Status: Models such as GPT-5.2, Claude 4.5 Opus, Gemini 3.0 Pro have achieved very high scores on coding benchmarks (HumanEval, SWE-bench).  
- Most important thing: their capability is growing everyday, is getting capable of doing more complex autonomous work (working independently longer)  
- Limitation: Black box. This research does not focus on improving the model

#### **2.1.2. Tools**

External Environment Interaction Capability: The ability to run terminal commands, read/write files (File I/O), and browse the web.

1. **IDE-Native Agents**  
- **Examples:** GitHub Copilot, Cursor, Windsurf, Google Antigravity (Editor View).  
- *Philosophy:* **Human-in-the-Loop.** Augmenting the active developer in real-time.  
- *Context Bottleneck:* Highly synchronous and constrained by the "Active Tab and Chat". They excel at micro-edits and being copilot, but struggle with macro-architectural consistency and operating autonomously.  
2. **CLI-Driven Agents**  
- **Examples:** Claude Code, Gemini CLI, Codex CLI.  
- *Philosophy:* **Headless** **High-Level Logic.** Focusing on file manipulation and refactoring via text-first interfaces, with the same tools humans have.  
- *Context Bottleneck:* **Session-Bound Memory.** They lack persistence. Once the terminal session closes, the "mental map" of the project is lost, requiring expensive context re-loading.  
3. **Autonomous Agents**  
- **Canvas/Product Agents** (e.g., Lovable, v0.dev): Focus on “vibe coding”  MVP generation.  
  - Limit: Effective for greenfield projects but prone to hallucinating patterns when applied to complex, existing "brownfield" architectures.  
- **Platform Agents** (e.g., Google Jules, Copilot Workspace): Async issue resolvers living in the repo.  
  - Limit: They act on isolated "Issues" often missing the broader side-effects of their changes on other modules.  
- **General Purpose Engineers** (e.g., Devin, OpenDevin): Fully autonomous agents.  
  - Limit: High "Discovery Cost." Without a structured map, they waste significant tokens and time just "reading" files to understand where things are.  
4. **Specialized Agents (Review)**  
- **Review Agent**  
- **Examples:** CodeRabbit, Bugbot.  
- *Philosophy:* Automated review and security checks.

**Summary of Tools:** While these categories show immense progress in *Execution*, they all treat Project Knowledge as a flat, searchable text interface rather than a structured relationship model. This is the **Tool Level** failure: tools are optimized for modifying code, not for understanding the topology of knowledge.

#### 2.1.3. Context

**Context** represents the essential environmental data supplied to the Model to ground its reasoning and prevent hallucinations. Within an agentic workflow, context is categorized into three fundamental paradigms of retrieval:

1. **Semantic Context:** Relies on probabilistic similarity (Vector Embeddings) to retrieve information that "looks like" the query, excelling at handling unstructured intent.  
2. **Structural Context:** Utilizes deterministic connectivity (Graph/AST) to navigate the project’s topology, ensuring accuracy in dependency mapping and hierarchy.  
3. **Behavioral Context (Agentic Discovery):** Relies on the agent’s autonomy to explore and isolate relevant data in real-time, simulating a human developer’s iterative discovery process.  
   

**The Exploration Gap: Implementation vs. Specification**  
Current industry standards focus heavily on managing **Implementation Context**—the "How" of the codebase (functions, classes, and logic). However, a critical "Exploration Gap" exists regarding **Specification Context**—the "Why" behind the code (requirements, user stories, and architectural intent).

While code is treated as a structured entity, documentation is frequently relegated to flat, disconnected text. This research identifies this disconnect as **"Documentation Blindness"**. Consequently, a **Knowledge Graph layer** is proposed to bridge this gap, transforming static artifacts into a structured "Machine-Readable State" that allows agents to navigate business logic with the same precision as source code.

### **2.2. Agentic Agile & The BMad Method**

To solve the problem of automated software development, this research uses **BMad** as the process foundation. Specifically, the implementation module **BMM (BMad Method Module)** is utilized to automate the development lifecycle.

#### 2.2.1. Why? (The Need for Structured Autonomy)

Conventional Coding Agent methods often operate in an "Ad-hoc" (fragmented) manner: User requests a fix \-\> Agent fixes \-\> Ends.

However, in developing a complete software product, this approach reveals weaknesses:

- **Lack of overall vision:** The Agent only sees the code, not the product strategy.  
- **Loss of state control:** It's difficult to know which phase the project is in (Design or Implementation?).

**BMM** is chosen because it applies the **Agile** mindset to the AI Agent. It forces the Agent to adhere to a strict process: Plans (Sprint) and documents (Specs) must exist before writing Code. This turns the documentation into the single "Source of Truth."

#### 2.2.2. What? (The BMM Implementation)

BMAD is the methodology, while **BMM** is the execution engine that this research applies.

- **Operating Mechanism:** **"Documentation-Driven Development"**.  
- Instead of prompting directly "Please write the login code," BMM requires the user and the agent  to collaborate to create relevant  files, including spec documents and code.  
- These files act as the system's "State."  
- **Role in Research:** BMM serves as the **Input Generator**. It produces a large volume of structured specification documents (PRD, Architecture, Stories), setting the stage for building the Knowledge Graph.

#### 2.2.3. How? (The Workflow & Limitation)

The operational process of BMM follows an iterative waterfall model within Agile, as described below:

**Phase 1: Initialization and Analysis (Optional)**

- **Goal:** Deciding what to build and why.  
- **Agent:** Analyst  
- **Workflow:** **workflow-init, brainstorm-project, research, product-brief**  
- **Output artifacts:** bmm-workflow-status.yaml (project tracking file), product-brief.md (skipped for this project)

**Phase 2: Planning**

- **Goal:** Transform brief/vision to requirements (Functional/Non-Functional).  
- **Agent:** PM (Product Manager)  
- **Workflow:** **create-prd**  
- **Output artifact:** planning-artifacts/prd.md (Product Requirement Document)

**Phase 3: Solutioning**

- **Goal:** System design to implement from requirement.  
- **Agent:** Architect and Project Manager  
- **Workflow:**   
  - **create-architecture** (Architect): Design system architecture, data schema, tech stack, and Architectural Decision Records (ADRs). **Output artifact:** planning-artifacts/architecture.md  
  - **create-epics-and-stories** (PM): Based on PRD and Architecture, break down the project into Epics and User Stories. **Output artifact:** planning-artifacts/epics.md  
  - **implementation-readiness** (Architect): Check if PRD, Architecture and Epics are aligned before implementation.

**Phase 4: Implementation**

- **Goal:** Transform Stories into code  
- **Agent:** SM (Scrum Master), TEA (Test Architect), Dev (Developer)  
- **Workflow per Epic:**  
  - **sprint-planning** (SM): create tracking file including all Epics and Stories. **Output artifact:** implementation-artifacts/sprint-status.yaml  
  - **test-design** (TEA): design tests for each Epic based on planning artifacts (prd.md, architecture.md, epics.md). **Output artifact:** implementation-artifacts/test-design-epic-\[epic\].md  
  - **Workflow per Story**  
    - **create-story** (SM): **Output artifact:** implementation-artifacts/\[epic\]-\[story\]-\[story name\].md  
    - **dev-story** (Dev): write code, write test, update artifact and status  
    - **code-review** (Dev): review code, fix found issues, complete story  
  - **epic-retrospective** (All Agents): do a retrospective after completing an epic. Output artifact: implementation-artifacts/epic-\[epic\]-retro-\[date\].md

**Other workflows:**

- **party-mode** (All Agents): Summon every agent to finish any task together.  
- **correct-course** (PM): change management during implementation. Output artifact: planning-artifact/sprint-change-proposal-\[date\].md  
- **quick-dev** (Quick Dev): quick implementation, skipping rigid steps.

**The Scalability Barrier: From "Assisted" to "Autonomous"**

While the BMAD workflow combined with CLI-driven agents has proven effective for assisted development, it encounters significant theoretical and operational barriers when scaling toward fully autonomous systems. This represents the **Context Level** failure:

1. **The Human Dependency:** Current agents operate as "workers" rather than "managers." They rely on the human operator to maintain the project's "Mental Model"—manually selecting the correct workflow to route the agent. The system lacks an intrinsic mechanism to self-navigate the correct agent/workflow without human pointing.  
2. **The Limitation of Linear Ingestion:** To compensate for the lack of structural understanding, the standard approach often involves feeding entire documentation artifact into the Context Window ("Context Dumping"). This leads to the "Lost in the Middle" phenomenon and high token costs. Furthermore, flat documentation files are **stateless**; an autonomous agent cannot easily query the *status* of an Epic or the *impact* of a change without parsing the entire repository text repeatedly.

**Conclusion:** To transition from Human-in-the-Loop (Assisted) to Human-on-the-Loop (Autonomous), the system requires a **"Machine-Readable State"**. This necessitates moving from a document-centric storage (flat files) to a knowledge-centric architecture (Graph).

### **2.3. Knowledge Graph Theory**

Software engineering artifacts exhibit a naturally high degree of connectivity. Unlike generic text corpora, code and specifications are defined by their relationships (dependencies, inheritance, references). Therefore, a Knowledge Graph (KG) offers a more isomorphic representation of software projects than flat text or vector stores.

#### **2.3.1. The Property Graph Model**

This research utilizes the **Labeled Property Graph** model (implemented via SurrealDB). This model is characterized by:

* **Nodes (Vertices):** Represent discrete software artifacts. In our context, these include DocumentNode (files), SectionNode (headers/requirements), and CodeNode (functions/classes).  
* **Edges (Relationships):** Represent directed dependencies. Crucial relationships include Contains (File \-\> Header), Parent\_of (Header \-\> Header) and REFERENCES (File \-\> File).  
* **Properties:** Key-value pairs stored within nodes and edges (e.g., status, last\_modified, content\_hash), allowing for rich metadata filtering during traversal.

#### **2.3.3. Comparative Analysis: Vector Search vs. Graph Traversal**

To justify the architectural choice, we compare the dominant retrieval method (Vector RAG) with the proposed Graph approach:

| Feature | Vector Search (Semantic RAG) | Knowledge Graph (Structural RAG) |
| :---- | :---- | :---- |
| **Mechanism** | Probabilistic Similarity (Embeddings) | Deterministic Connectivity (Edges) |
| **Query Type** | *"Find code that looks like login logic"* | *"Find the exact User Story linked to this Function"* |
| **Strength** | Fuzzy matching, handling unstructured intent. | Traceability, Dependency mapping, Impact analysis. |
| **Weakness** | **Context Flattening:** Loses the hierarchical structure; prone to hallucinations when concepts overlap. | **Construction Cost:** Requires strict parsing and maintenance of the graph structure. |

While Vector Search is superior for "Discovery" (finding unknown items), Knowledge Graph is essential for "Navigation" (understanding complex systems). This research aims to leverage the deterministic nature of Graphs to reduce the hallucination rate in coding tasks.

#### **2.3.4. Graph Retrieval-Augmented Generation (GraphRAG)**

GraphRAG represents the synthesis of LLM reasoning and Graph topology. In this proposed framework, the workflow shifts from linear reading to recursive traversal:

1. **Extraction:** The LLM or Parser identifies entities in the user prompt (e.g., "AuthService").  
2. **Traversal:** The system queries the Graph to retrieve the "Sub-graph" (1-hop or 2-hop neighbors) connected to that entity.  
3. **Generation:** The Agent receives a highly curated context containing only the relevant logical cluster, filtering out noise.

This approach transforms the documentation from a static repository into a **dynamic cognitive map**, allowing the Agent to "reason" about the project structure before writing code.

### **2.4. Database Layer: SurrealDB**

In the overall architecture, instead of trying to ingest all the Codebase into the database, the project focus solely on Project Knowledge

#### **2.4.1. Strategic Data Segregation: Code vs. Knowledge**

Unlike other approaches trying to turn the whole Codebase into a graph, this project clearly separates the roles of 2 different data types:

1. **Code (Implementation Layer):**  
- **Characteristics:** Deterministic, frequently changing, and strictly structured (Syntax).  
- **Strategy:** Use **Agentic Tool-Use Retrieval**. Real-time CLI tools, grep, or AST parsers handle code searches far more efficiently than storing them in a Graph Database.  
2. **Knowledge (Specification Layer):**  
- **Characteristics:** Unstructured or semi-structured text (Markdown), containing design intent, business logic, and semantic relations.  
- **Strategy:** This is the primary subject for a **Knowledge Graph**. These must be converted from static files into dynamic graph nodes so the Agent can query the context.

**Conclusion:** Database is designed specifically for storing **Mental Model** of the project (Epics, Stories, PRDs), acting as a Reference Layer for Agent during interaction with Code.

### **2.4.2. Comparative Analysis: Why not Neo4j?**

After evaluating popular solutions such as Neo4j (Pure Graph) or Qdrant/Chroma (Pure Vector), this research opts for **SurrealDB**.

**Multi-model Architecture:** Managing software documentation requires the convergence of three critical elements:

1. **Document Store:** Storing raw text (Markdown content) for Agent comprehension.  
2. **Graph Store:** Storing reference links to understand project structure.  
3. **Vector Store:** Storing embeddings for semantic search.

SurrealDB natively supports all three models within a single entity (Record), eliminating the need to maintain multiple disparate databases and reducing **Architectural Complexity**.

While Neo4j is the industry standard for Graph Databases, applying it to "Agentic Context" problems reveals significant **Architectural Impedance Mismatch**:

| Feature Criteria | Neo4j (Traditional Graph) | SurrealDB (Selected) |
| :---- | :---- | :---- |
| **Document Storage** | **Weak.** Storing large text bodies (Markdown) in Node properties degrades performance and complicates management. | **Native.** Each Record acts as both a graph Node and a complete JSON Document. Ideal for Markdown files. |
| **Vector Search** | Requires plugins (Graph Data Science Lib) or complex configurations for Vector Index integration. | **Native.** Supports Vector Embeddings and distance functions (Cosine/Euclidean) directly in the database core. |
| **Deployment** | Heavy (Java-based); resource-intensive for local execution (Local-first constraint). | **Ultra-lightweight.** Single binary written in Rust. Perfectly fits CoreText’s "Local-First" and CLI tool architecture. |
| **Query Complexity** | Cypher is powerful for graphs but cumbersome when combining Full-text and Vector search. | **SurrealQL** allows combining all three query types in a single, simple SQL-like statement. |

**Conclusion:** Selecting SurrealDB eliminates the need to maintain two separate databases (Graph \+ Vector), reducing **Operational Complexity** by an estimated 50%. This choice prioritizes truth in efficiency over the flattery of following "industry standards" that don't fit the specific use case.

### **2.4.3. The Power of SurrealQL: A Unified Query Language**

The core strength of CoreText lies in its **Hybrid Retrieval** capability. The Agent does not need to execute multiple disjointed steps (e.g., querying a Vector DB for IDs, then a Graph DB for relationships). Instead, SurrealQL enables highly sophisticated compound queries:

**Mechanism:** A convergence of **Semantic Search** (Vector-based meaning), **Graph Traversal** (Relationship-based scope), and **Lexical Search** (Keyword-based matching).

**Theoretical Application:** Rather than merely searching for *similar* text fragments (Pure Vector), the system empowers the Agent to perform high-order logical queries:

*"Find business rules regarding 'Dual finding' (**Semantic**) BUT only within the scope of 'Search Story' (**Graph Topology**) AND containing the keyword 'SurrealDB' as the designated platform (**Lexical**)."*

This ensures that the context provided to the Agent is both semantically relevant and structurally accurate. This query mechanism precisely mirrors the mental model and cognitive process of a software engineer.

### **2.5. Orchestration Layer: Gemini CLI & Model Ecosystem**

In an Agentic architecture, the choice of execution tool (Orchestration Interface) is as critical as the choice of the Model itself. Rather than building a chat system from scratch, this research integrates **Gemini CLI**—a powerful open-source tool by Google—to serve as the entry point for programming tasks.

#### **2.5.1. The Reasoning Engine: Gemini 3.0**

The system utilizes the **Gemini 3.0** model family (released Q4/2025) as the primary Reasoning Engine. This choice is based on superior characteristics compared to contemporary rivals (such as GPT-5.2 or Claude 4.5):

- **Native Long Context (1M+ Tokens):** The ability to process massive context windows allows the Agent to grasp the entire graph structure when necessary.  
- **Adaptive Reasoning:** The capability to automatically switch between *Flash* (fast responses for simple queries) and *Pro* (deep reasoning for complex architectural tasks) modes, optimizing both latency and cost.  
- **Multi-modal Capabilities**

#### **2.5.3. Open Source**

Unlike proprietary closed-source tools such as *Cursor* or *Claude Code*, Gemini CLI is **Open Source**. This is a decisive factor for the scientific integrity of this research:

- **Transparent Logging:** Enables the export of full conversation histories, token usage, and model metadata. This is vital for quantitatively measuring Knowledge Graph efficiency.  
- **Reproducibility:** Any researcher can replicate the experimental environment without dependency on a specific paid IDE (though a dependency on Google's models remains).

#### **2.5.2. Context Caching Strategy**

One of the greatest hurdles in Agentic Development is the token cost of repeatedly loading large project documents. Gemini CLI addresses this via **Context Caching** technology:

- **Mechanism:** Instead of re-sending the entire document content in every chat turn, the system caches the state on Google's servers.  
- **Impact:** Reduces input token costs by **90%** for repetitive queries. This transforms "chatting with the entire project" from a luxury into an economically viable solution for this research.

#### **2.5.4. Extensibility via Model Context Protocol (MCP)**

Gemini CLI supports the **MCP (Model Context Protocol)** standard, allowing standardized connections to external tools.

- **Integration:** CoreText operates as an **MCP Server Extension**.  
- **Workflow:** When a user asks, *"Which files are affected by this User Story?"*, Gemini CLI invokes the `query_knowledge` tool via the MCP protocol to retrieve precise data from SurrealDB.

#### **2.5.5. Architectural Divergence: Overcoming Execution Bias**

A critical analysis reveals a distinct philosophical gap between **Gemini CLI** and industry standards like **Claude Code**.

* **The Standard Approach (Claude Code):** Adopts a **"Plan-First"** architecture. It enforces a rigid internal state machine (*Plan to Review to Execute*), treating coding as a systematic industrial process. While safe, this introduces significant latency.  
* **The Gemini Approach (Execution Bias):** Optimized for **"Low-Friction"** and massive context ingestion. Without external guidance, it tends to be "over-confident," often skipping the planning phase to jump directly into implementation ("vibe coding"). This leads to the perception of poor performance among casual users due to frequent "hallucinated simplicity" in complex architectures.

**Research Adaptation:** This project identifies that Gemini's "weakness" is actually an **advantage** when paired with a knowledge base. Instead of relying on the Model to maintain a mental plan (which creates "Prose Interference"), **CoreText** externalizes the "State Management" to the Graph.  

### **2.6. Input Artifacts: The Strategic Choice of Markdown**

In the AI era, selecting a document format is no longer just a matter of preference; it is a critical **Architectural Decision**. This research adopts **Markdown** as the primary format for storing knowledge (Knowledge Artifacts).

#### **2.6.1. The Optimal Human-AI Integration**

Software development documentation must serve two distinct audiences: **Humans** (for comprehension and creativity) and **AI Agents** (for analysis and code generation). Markdown represents the optimal equilibrium that other formats fail to achieve:

| Format | Human Readability | AI Readability | Disadvantages in Agentic Workflow |
| :---- | :---- | :---- | :---- |
| **Docx / PDF / LaTeX** | High (Visual) | Low / Medium | Contains excessive presentation metadata (layout, fonts). AI wastes tokens processing formatting "noise" without understanding logical structure. |
| **JSON / YAML / XML** | Low (Cluttered) | High (Strict Structure) | Difficult for long-form human writing. Unsuitable for drafting business descriptions (User Stories) or design thinking. |
| **Markdown (Selected)** | **High** | **High** | Lightweight syntax. AI easily identifies structure through symbols like `#`, `*`, and `>` without being distracted by noise. |

#### **2.6.2. Markdown as a Pre-Graph Structure**

Markdown is more than just flat text. With modern extensions (as seen in Obsidian or BMAD), Markdown possesses inherent pre-graph characteristics:

- **Links:** These function as **Reference edges** connecting different nodes.  
- **Headers (\# H1 \-\> \#\# H2):** Represent natural **Parent\_of** and **Contains** relationships.  
- **Frontmatter (YAML header):** Contains metadata, effectively serving as **Node Properties**.

**Conclusion:** Using Markdown allows the system to transition into a **Knowledge Graph (SurrealDB)** naturally, without requiring users to learn complex data entry tools.

### **2.7. The Transformation Logic: Abstract Syntax Tree (AST)**

To transform Markdown text into a Graph, the system moves beyond basic String Processing and utilizes **Abstract Syntax Tree (AST)** techniques.

- **Definition:** An AST is a tree-based structural representation of source code or text.  
- **Role in Research:** Instead of using error-prone Regex, an AST Parser decomposes documents into meaningful "Tokens": Headings, Paragraphs, Lists, and Links.  
- **Mechanism:**  
  1. *Input:* \# User Story 1  
  2. *AST Node:* Type: Heading, Level: 1, Content: "User Story 1”  
  3. *Graph Mapping:* Creates a HeaderNode in the database.  
- **Impact:** This ensures absolute precision in data extraction, preventing the Agent from experiencing "structural hallucinations" regarding the document layout.

### **2.8. The Connectivity Interface: Model Context Protocol (MCP)**

To ensure extensibility and compatibility with future IDEs, the system integrates the **Model Context Protocol (MCP)** (introduced by Anthropic in 2024).

- **The Problem:** Previously, connecting a Database to an AI required unique "Custom Glue Code" for each specific model (Claude, Gemini, etc.).  
- **The MCP Solution:** MCP acts as a standardized "USB port" for AI.  
  - **CoreText as an MCP Server:** It exposes Graph data as standardized "Resources" and "Tools." This means *any* Agent supporting the MCP standard can "plug into" the Knowledge Graph to retrieve data without the need for bespoke integration code.  
  - **AI Client (Gemini CLI via Extension):** Automatically understands how to invoke the query\_knowledge tool without complex configuration.  
- **Research Value:** Adopting MCP transforms CoreText from a local tool into a **"Knowledge Module"** that is Plug-and-Play across any AI ecosystem supporting the standard.

### **2.9. Operational Mechanics: Git Hooks & GitPython**

To realize the Background Synchronization features discussed in subsequent chapters, the system employs a Git-based **Event-Driven** mechanism.

- **Git Hooks (Pre-commit/Post-commit):** These are scripts that trigger automatically when a developer executes a `git commit`. They serve as **Checkpoints**, ensuring that the data within the Graph remains perfectly synchronized with the physical files on the disk.  
- **GitPython:** This library enables the system to manipulate the Git Repository at the programmatic level. It allows the system to answer time-based queries such as: *"When was this file last modified?"* or *"Who authored these changes?"*, thereby enriching the Knowledge Graph with vital temporal metadata.

---

### **2.10. User Interface: Typer & CLI Experience**

- **Typer:** Selected for building the Command Line Interface (CLI). Typer leverages Python Type Hints to automatically generate intuitive commands, input validation, and comprehensive help documentation.  
- **Role:** Ensures a frictionless **Developer Experience (DX)**, allowing developers to interact with a complex system (Graph, AI, Config) through simple commands like coretext sync or coretext status.

## **Chapter III. Related Work**

#### **3.1. Pre-indexed Semantic Retrieval (e.g., Cursor, GitHub Copilot)**

- **Mechanism:**  
  - **Hybrid Search:** A combination of **Sparse Retrieval** (keywords \- BM25/Splade) and **Dense Retrieval** (vector embeddings).  
  - **Codebase Indexing:** Fragments the entire codebase into snippets (chunking) and stores them in a Vector Store (e.g., Cursor uses a "Shadow Workspace" for local indexing).  
- **Strength:** Extremely fast for "Implementation" queries (e.g., *"How do I write a search function?"*). Handles ambiguous (fuzzy) queries well.  
- **Limitation:** Struggles with **Structural Causality**. It can find code that *looks* like "search" logic but fails to identify which module that code belongs to without explicit comments. For Markdown documentation, it treats it as flat text, completely losing the Epic/Story hierarchy.

#### **3.2. Pre-indexed Structural Retrieval (e.g., Sourcegraph Cody)**

- **Mechanism:**  
  - **SCIP/LSP (Language Server Protocol):** Uses static analysis to build precise Dependency Graphs: *Definition* → *Reference*. Modern agents increasingly leverage the **LSP** as a real-time semantic sensor, allowing them to access "Go-to-Definition" and "Find References" capabilities natively, mirroring a human developer's workflow.  
  - **Deterministic Navigation:** Zero guesswork. It knows exactly which function A calls function B.  
- **Strength:** Absolute precision within code (Zero hallucination on references). Highly effective for large-scale, cross-file refactoring.  
- **Limitation (The Doc-Code Disconnect):** Only functions effectively with **Code** (where syntax is rigid). With Markdown (unstructured), it either fails or reverts to standard keyword search. It cannot understand the semantic link between PRD.md and manager.py.

#### **3.3. Agentic Discovery & Feedback Loops with Just-in-Time (JIT) Retrieval (e.g., Claude Code)**

- **Core Philosophy:** No pre-indexing. The Agent explores the environment dynamically, much like a human developer.  
- **Mechanism 1: Progressive Disclosure:**  
  - Starts with a **Metadata Layer** (File tree, ls \-R).  
  - Performs **Surgical Reading** (detailed content access) only when necessary using tools (grep, cat, view).  
- **Mechanism 2: Context Isolation:**  
  - The Agent plans autonomously, breaking large tasks into sub-tasks.  
  - Each sub-task creates an isolated context session to prevent "Context Pollution."  
- **Mechanism 3: ARCS (Agentic Retrieval-Augmented Code Synthesis):**  
  - **Logic:** The Agent doesn't just retrieve *before* coding. It codes \-\> executes \-\> encounters an error \-\> **re-retrieves based on that error**.  
  - **Significance:** This marks the transition from a "Static Reader" to a "Dynamic Experimenter."  
- **Strength:** No indexing overhead. High reasoning capability.  
- **Limitation:**  
  - **Cold Start:** Without high-quality cues (like a perfectly written CLAUDE.md or README.md), the Agent wastes numerous steps (and tokens) figuring the project structure.  
  - **Manual Dependency:** Still relies on humans to manually draft CLAUDE.md to feed the context for business logic comprehension.

**Gemini CLI**, and other CLI-driven agents, represent Approach 3.3 (Agentic Tool-Use), optimizing execution through ReAct loops and robust CLI tools.

### **3.4. The Critical Gap: Missing "Documentation-Aware" Structure**

While the methods above are powerful, they share a common blind spot: **"Documentation Blindness."**

1. **Code is Structured, Docs are Flat:** Existing tools treat Code as a structure (AST/Graph) but treat Requirements (Specs, PRDs) as flat text.  
2. **No Bridge:** There is no automated mechanism to explicitly link a **Business Node** (e.g., a PRD) to an **Execution Node** (e.g., a User Story).  
3. **Consequence:** An Agent may modify code rapidly (via Approach 3.3) but easily violate Business Rules hidden in documentation because it cannot "query" that documentation logically.

**This is the fundamental reason this research proposes a specialized Knowledge Graph for Documentation.**

## **Chapter IV. Analysis, Design, and Methodology**

### **4.1. Requirements Analysis**

To bridge the "Documentation Blindness" gap, the system is designed to meet specific functional requirements derived from the "Dual-Context" access model: humans define architecture in files, while AI agents access a semantic graph.

#### **4.1.1. Core Problem & Solution**
The central problem is "Context Window Overload" and "Lost in the Middle" phenomena when feeding massive documentation to LLMs. The proposed solution is **CoreText**, a local-first Knowledge Graph engine.
-   **Dual-Context Access:** A unified interface where the Human view (Files) and Agent view (Graph/Vectors) remain perfectly synced.
-   **Implicit Synchronization:** The system acts as an invisible background process (`sync.py`) that converts human-written artifacts into machine-readable graph nodes without manual intervention.

#### **4.1.2. Functional Requirements**
Based on the Product Requirement Document (PRD), the system must support:
1.  **Parsing:** Convert BMAD-flavored Markdown into structured graph nodes (`FR1`).
2.  **Synchronization:** Detect Git changes (`FR2`) and update the graph incrementally via hooks (`FR3`, `FR13`).
3.  **Storage:** Persist the graph in a local SurrealDB instance (`FR4`) with versioning based on Git hashes (`FR5`).
4.  **Retrieval:** Provide an MCP interface (`FR9`) for agents to query topology (`FR10`) and traverse dependencies (`FR12`).
5.  **Integrity:** Enforce referential integrity (Standard Markdown Links) and report broken links (`FR6`, `FR7`).

### **4.2. System Architecture**

The architecture follows a **"Local-First, AI-Native"** philosophy, minimizing cloud dependencies and maximizing local performance.

#### **4.2.1. High-Level Design**
The system comprises three main components:
1.  **Core Daemon (Python Monolith):** The "Brain" of the system, running as a background process. It handles AST parsing, graph logic, and vector embeddings. It exposes an MCP Server via FastAPI.
2.  **CLI Client (Typer):** The "Controller". A lightweight CLI tool (`coretext`) that manages the daemon lifecycle (`init`, `start`, `status`) and provides user tools (`inspect`, `lint`).
3.  **Gemini Extension:** A thin client layer that integrates the CoreText MCP server into the Gemini CLI ecosystem, allowing the agent to invoke tools like `query_knowledge`.

#### **4.2.2. Data Architecture: Schema Projection**
To handle the flexibility of Markdown versus the rigidity of databases, a **"Schema Projection"** strategy is employed:
-   **Internal Schema:** Rigid Pydantic models (e.g., `class Epic(BaseNode)`) define the "Ideal State" within the Python code.
-   **Mapping Layer:** A configuration file (`schema_map.yaml`) maps external Markdown headers (e.g., `# User Story`) to internal DB properties.
-   **Storage:** **SurrealDB** is used for its multi-model capabilities, storing Content (Docs), Topology (Graph), and Semantics (Vectors) in a single `Record`.

#### **4.2.3. Technology Stack**
-   **Runtime:** Python 3.10+ (utilizing modern Type Hints).
-   **API Framework:** **FastAPI** (for high-performance MCP endpoints).
-   **CLI Framework:** **Typer** (for intuitive command-line experiences).
-   **Database:** **SurrealDB** (Embedded/Local binary).
-   **Vector Engine:** **Nomic Embed Text v1.5** (via `sentence-transformers`), chosen for its Matryoshka Representation Learning (MRL) capabilities, allowing flexible storage optimization.

### **4.3. Methodology & Implementation**

#### **4.3.1. Parsing Engine (AST & Normalization)**
Instead of fragile regex, the system uses **`markdown-it-py`** to generate a robust Abstract Syntax Tree (AST) from Markdown files.
-   **Node Generation:**
    -   **Root Node:** The File itself (`id = file_path`).
    -   **Header Nodes:** Each header (`#`, `##`) becomes a distinct node, linked via `CONTAINS` and `PARENT_OF` edges.
-   **Canonical Path Normalization:** A critical logic layer ensures that all file paths (e.g., `../docs/prd.md` vs `docs/prd.md`) resolve to a single **Canonical ID** relative to the project root. This prevents duplicate nodes and ensures graph connectivity.

#### **4.3.2. Knowledge Graph Construction**
The graph is constructed deterministically:
-   **Nodes:** Represents artifacts (`FileNode`, `HeaderNode`).
-   **Edges:**
    -   **Structural:** `CONTAINS`, `PARENT_OF` (derived from document hierarchy).
    -   **Referential:** `REFERENCES` (derived from `[Link](path)`).
-   **Validation:** The system employs a "Strict Schema, Loud Failures" policy. Malformed Markdown results in a `ParsingErrorNode`, preventing data corruption and alerting the user via the CLI.

#### **4.3.3. Semantic Retrieval (Hybrid Search)**
A **"Thick Tool"** named `query_knowledge` is implemented to abstract complex retrieval logic from the LLM.
1.  **Vectorization:** The user's natural language query is embedded using `nomic-embed-text-v1.5`.
2.  **Anchor Selection:** A vector similarity search (SurrealQL `vector::similarity::cosine`) identifies relevant "Anchor Nodes" in the graph.
3.  **Graph Traversal:** The system automatically traverses outgoing edges (`depends_on`, `child_of`) from these anchors to gather context.
4.  **Result:** A consolidated subgraph is returned, providing the Agent with both the *semantic match* and its *structural dependencies*.

#### **4.3.4. Synchronization Mechanism (Git Hooks)**
To ensure the graph never drifts from the codebase, **Git Hooks** (`pre-commit` / `post-commit`) are utilized.
-   **Event-Driven:** The `sync.py` hook triggers on every commit.
-   **Fail-Open Policy:** If the sync process fails (e.g., DB lock), it logs the error but *does not block* the commit, ensuring developer workflow continuity.
-   **Async Detachment:** For large commits (>10 files), the hook automatically detects potential latency and "detaches" the sync process to run in the background, keeping the commit operation instantaneous (<1s).

---

## **Chapter V. Results and Evaluation**

### **5.1. Experiment 1: Self-Reflexive Case Study (Project CoreText)**

- Context: Bootstrapping the CoreText engine using the standard BMAD framework (baseline scenario without Graph integration).  
- Workflow: Human \+ BMad  
- Pain Points Observed

**Observation:** The bootstrapping process of CoreText using the standard BMAD workflow (CLI \+ Human Guidance) yielded **unexpectedly high efficiency**. As the project scaled, the structured nature of BMAD documentation (epics, stories) combined with SOTA tools (like Claude Code) allowed for:

1. **Decreasing Token Waste:** The strict file structure enabled the human operator to pinpoint exactly which files to feed the agent, reducing unnecessary context.  
2. **High Accuracy:** The "Human-in-the-Loop" effectively acted as a semantic router, bridging the gaps that the AI couldn't see.

**Conclusion:** This proves that **Structure is Key**. Current Coding Agents are powerful enough to handle complex logic *if* provided with the correct, isolated context by a human.

### **5.2. Experiment 2: Application Case Study (Project Nhaminhbach)**

(Not Effective) 

**Why imply this? (The Research Justification):** This trade-off is intentional and represents a **Paradigm Shift from "Efficiency" to "Autonomy"**.

* **BMAD Classic:** Relies on *implicit* knowledge stored in the Human's mind (to find files). It is efficient but **not scalable** without the human.  
* **Graph Approach:** Externalizes that implicit knowledge into the Database. While currently slower (due to the lack of a fully optimized Orchestrator), it is the necessary **"Cognitive Infrastructure"** for the next phase.

### **5.3. Evaluation Metrics**

- **Context Precision:** (Theoretical) Graph retrieval provides higher signal-to-noise ratio than file dumping.  
- **Token Efficiency:** Reduced token usage per query due to targeted node retrieval.  
- **Scalability:** The system maintains performance as file count increases, whereas standard context windows degrade.

### **5.4. Discussion & Future Work**

- The success of Experiment 1 relied heavily on the human operator acting as a **"Human Orchestrator"**—manually selecting the correct documentation artifacts for the Agent. The Knowledge Graph acts as a **"Digital Orchestrator"**. Although currently in a "Proof-of-Concept" stage with performance overheads, it successfully demonstrates that an Agent *can* navigate project topology programmatically.  
- **Research Verdict:** The Knowledge Graph is not an immediate optimization tool for *assisted* coding (where tools like Cursor/Claude excel), but a **foundational enabling technology** for *autonomous* software engineering (where the human is absent).  

**Future Work:**

This research positions CoreText not merely as a static retrieval tool, but as the first step in a "Progressive Assimilation" strategy for autonomous software engineering.

1. **Phase 1 (Achieved):** CoreText functions as a **Utility**, offering structural retrieval commands (`grep` for graphs) to human developers via a CLI tool.  
2. **Phase 2 (Current Implementation):** CoreText acts as a **Driver** for existing agent frameworks (BMAD). It injects precise context via MCP, enabling agents to navigate complex documentation without "context dumping."  
3. **Phase 3 (Future Vision \- "Swallowing"):** It is envisioned that CoreText evolves into the **Native State Machine** for a Multi-Agent System (e.g., using frameworks like **Agno**).  
   * In this phase, the monolithic workflow files of BMAD are "ingested" into the Graph logic.  
   * This enables a clean separation of concerns: The **Multimodal Graph** manages the "Who, What, and Why" (Strategy & State), while specialized **Autonomous Agents** manage the "How" (Execution).  
   * This decoupling allows for smaller, faster, and highly reusable specialized agents, orchestrated dynamically by an stateful agentic framework via the graph's topology rather than static instruction files.  

Finally, while this research utilizes software engineering as a primary case study due to the high structural integrity of code artifacts, the proposed Knowledge Graph architecture possesses significant transferability. It offers a viable template for any domain requiring autonomous agents to navigate complex, interdependent documentation systems, such as legal analysis, medical research, or regulatory compliance.

### **5.5. Conclusion**

The integration of a Knowledge Graph into the BMad framework shifts the paradigm from "Document-Centric" to "Knowledge-Centric" development. This abstraction allows AI agents to operate with a structural understanding of the software, paving the way for more autonomous and accurate software engineering workflows.