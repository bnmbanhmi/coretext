# Story 5.4: Gemini CLI Integration & Extension Packaging

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a User,
I want the CoreText MCP tools (specifically `query_knowledge`) to be natively available in the Gemini CLI,
so that I can interact with the knowledge graph naturally during my chat sessions (e.g., "How does the graph manager work?") without manually running CLI commands.

## Acceptance Criteria

1.  **Extension Manifest Configuration**:
    *   The `extension.yaml` (or `gemini-extension.json` if format migration is required) includes a `tools` (or `mcpServers`) section.
    *   The configuration correctly points to the running CoreText daemon (default: `http://127.0.0.1:8001` or the configured MCP port).
2.  **Tool Exposure**:
    *   The `query_knowledge` tool is exposed to the Gemini CLI agent.
    *   Other tools like `search_topology` and `get_dependencies` are also exposed if applicable.
3.  **End-to-End Verification**:
    *   When the user asks a natural language question in Gemini CLI (e.g., "Explain the project structure"), the Agent transparently invokes `query_knowledge`.
    *   The tool execution returns the context (JSON subgraph) to the conversation.
    *   The Agent uses this context to answer the question accurately.
4.  **Seamless Integration**:
    *   The extension works with the existing daemon lifecycle (init/start/stop).
    *   No manual tool definition pasting is required by the user.

## Tasks / Subtasks

- [ ] **Manifest Format Verification**
  - [ ] Research the specific Gemini CLI version's requirement for extension manifests (`extension.yaml` vs `gemini-extension.json`).
  - [ ] Identify the correct syntax for connecting an MCP Server (HTTP or Stdio). *Note: CoreText uses HTTP Daemon.*
- [ ] **Update Extension Manifest**
  - [ ] Add `tools` or `mcpServers` configuration to map to the local Daemon endpoints.
  - [ ] Ensure tool descriptions and parameter schemas in the manifest match the Pydantic models in `coretext/server/mcp/routes.py`.
- [ ] **Verify Tool Invocation**
  - [ ] Test 1: Start Daemon (`coretext start`).
  - [ ] Test 2: In Gemini CLI, run `/tools` (or equivalent) to verify `query_knowledge` is listed.
  - [ ] Test 3: Ask "How is the GraphManager implemented?". Verify `query_knowledge` is called.
- [ ] **Documentation Update**
  - [ ] Update `README.md` with instructions on how to install/enable the extension in Gemini CLI.

## Dev Notes

### Manifest & MCP Connection
*   **Current State**: `extension.yaml` lists custom commands but no tools.
*   **Target State**: We need to bridge the Gemini CLI to the `coretext` MCP server.
*   **Protocol**: Since `coretext` runs as a daemon exposing HTTP endpoints (Story 2.1, 2.4), the extension should ideally configure an **HTTP MCP Client** connection.
    *   *Alternative*: If the CLI requires Stdio, we might need a small adapter script (`coretext mcp-stdio`) that pipes stdin/stdout to the HTTP daemon, OR the manifest might support `command: ["coretext", "mcp-stdio"]`.
    *   *Preference*: HTTP connection if natively supported by the manifest to reuse the daemon.

### Tool Definitions
*   **`query_knowledge`**:
    *   Parameters: `natural_query` (str), `depth` (int), `top_k` (int), `regex_filter` (str), `keyword_filter` (str).
    *   Ref: Story 5.3 implementation.
*   **Consistency**: Ensure the description in the manifest is optimized for the Agent to know *when* to use it (e.g., "Use this for ANY codebase questions").

### Project Structure Notes
- **Manifest**: `extension.yaml` (Root).
- **Server Routes**: `coretext/server/mcp/routes.py`.

### References
- [Story 5.3 Artifact](../implementation-artifacts/5-3-hybrid-execution-thick-tool.md) (Tool Signature)
- `docs/api/mcp.md` (If exists, else `coretext/server/mcp/README.md`)

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### File List
- extension.yaml
- coretext/server/mcp/routes.py (for reference)
- README.md
