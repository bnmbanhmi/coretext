# Story 5.6: Gemini CLI Extension Manifest & Command Packaging

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to package CoreText as a standard Gemini CLI extension using a `gemini-extension.json` manifest and TOML commands,
so that users can easily install and use the tool via the Gemini CLI with proper lifecycle management and custom commands.

## Acceptance Criteria

1.  **Manifest Creation**:
    *   A `gemini-extension.json` file is created at the project root.
    *   It contains valid metadata (name, version, description).
    *   It defines the `mcpServers` section for `coretext`.
    *   The command configuration uses `${extensionPath}` to correctly reference the executable/script regardless of install location.
    *   The `extension.yaml` file (deprecated format) is removed if it exists.
2.  **Command Packaging**:
    *   A `commands/` directory is created at the project root.
    *   A `commands/coretext.toml` file is created.
    *   The TOML file defines at least one useful command (e.g., a "CoreText Status" prompt or "CoreText Init" helper) to verify the mechanism.
3.  **Installation Verification**:
    *   Running `gemini extensions link .` in the project root successfully links the extension.
    *   The Gemini CLI recognizes the extension and its MCP capabilities.
    *   The Gemini CLI lists the custom commands defined in the TOML file.
4.  **End-to-End Functionality**:
    *   The MCP server starts automatically when the Gemini CLI is used (managed by the CLI via the manifest config).
    *   Previous functionality (Story 5.4/5.5) remains intact (queries still work).
5.  **MCP Stdio Adapter**:
    *   A `stdio_adapter` command is implemented to bridge MCP JSON-RPC over Stdio to the CoreText HTTP daemon.
    *   `gemini-extension.json` uses this adapter command instead of `start`.
    *   Agent can query tools (e.g., `search_topology`) via the extension.

## Tasks / Subtasks

- [x] **Cleanup Deprecated Artifacts**
  - [x] Remove `extension.yaml` from project root.
  - [x] Remove any references to `extension.yaml` in documentation or scripts (check `README.md`, `pyproject.toml`, etc.).
- [x] **Implement MCP Stdio Adapter**
  - [x] Implement `coretext/cli/adapter.py` to speak MCP JSON-RPC over Stdio and proxy requests to the local HTTP daemon.
  - [x] Add `adapter` command to `coretext/cli/commands.py`.
  - [x] Update `gemini-extension.json` `mcpServers.coretext.args` to use `adapter` command.
- [x] **Implement Manifest**
  - [x] Create `gemini-extension.json`.
  - [x] Configure `mcpServers.coretext` to run `python3 -m coretext.main` (or the installed binary path).
  - [x] **CRITICAL:** Use `${extensionPath}` logic to ensure the command works in both dev (linked) and prod (installed) modes.
- [x] **Implement Custom Commands**
  - [x] Create `commands/` directory.
  - [x] Create `commands/coretext.toml`.
  - [x] Define a `[status]` command that prompts the user to check system health.
  - [x] Define comprehensive commands for all CoreText CLI capabilities: `init`, `start`, `stop`, `lint`, `sync`, `apply-schema`, `new`, `install-hooks`, `inspect`, `ping`.
- [x] **Verification**
  - [x] Run `gemini extensions link .`.
  - [x] Restart Gemini CLI (if needed).
  - [x] Verify extension is listed.
  - [x] Verify MCP tools are discovered (using the new adapter).
  - [x] Verify custom commands appear in the prompt menu (if applicable) or are usable.

## Dev Notes

### Technical Requirements (from Sprint Change Proposal)

-   **Manifest Standard:** usage of `gemini-extension.json` is MANDATORY. Do not use YAML.
-   **Path Variables:** The manifest MUST use `${extensionPath}` to refer to files within the extension.
    -   *Example:* `"command": "python3", "args": ["${extensionPath}/coretext/main.py"]` (or similar entry point).
    -   *Better approach:* If using `poetry` or `pip` installed globally, the command might be `coretext`. However, for a self-contained extension, pointing to the internal python module or a wrapper script in `${extensionPath}` is safer for portability.
    -   *Architecture Decision:* The architecture defines `coretext` as a python package. The extension should likely invoke the module directly or use a `script` wrapper if packaged.
    -   *Recommendation:* Use `["-m", "coretext"]` with `cwd` set to `${extensionPath}` if the env is set up, OR assume the user has `coretext` in their PATH.
    -   *Refinement:* Since this is a "Local-First" tool installed via Poetry/Pip *separately* usually, the extension might just be a "Linker".
    -   *Constraint Update:* The Acceptance Criteria says "package CoreText as a standard... extension". If the user installs the extension, they expect it to work.
    -   *Decision:* The `mcpServers` config should point to the `coretext` executable if we assume it's in PATH, or try to locate it.
    -   **Proposal Specifics:** The proposal says "Correct `mcpServers` configuration (command, args, cwd) for the CoreText daemon."
    -   *Let's try:*
        ```json
        "mcpServers": {
          "coretext": {
            "command": "coretext",
            "args": ["start", "--stdio"], 
            "env": { ... }
          }
        }
        ```
        *Wait*, CoreText daemon is an HTTP server (FastAPI). The MCP protocol over Stdio is different from HTTP.
        *Story 2.1* says "server binds only to 127.0.0.1". It's an HTTP MCP server (SSE/Post).
        **Crucial Check:** Does Gemini CLI support HTTP MCP servers? Yes, usually via SSE.
        **Manifest Config for HTTP:**
        If the server is HTTP, the manifest usually needs to start it and then connect, OR just know where it is.
        Actually, standard MCP logic often uses Stdio for local extensions to avoid port conflicts.
        *Check Architecture:* "Architecture: MCP Server (FastAPI)... API Design: MCP Tools exposed via /mcp/tools/...".
        *Conflict:* If Gemini CLI expects Stdio, and we built FastAPI/HTTP, we need an adapter or we need to configure Gemini to use SSE.
        *Assumption:* We will configure the manifest to launch the existing daemon or a lightweight stdio wrapper if needed.
        *Update:* If the daemon is already running (managed by `coretext init/start`), the extension might just be a client. But "Lifecycle Management" in the proposal implies Gemini *manages* it.
        **Guidance:** Configure `gemini-extension.json` to launch the daemon in a way Gemini accepts. If Gemini supports SSE, use that. If Stdio is required, we might need a `stdio_adapter.py` (add to tasks if needed, but let's assume the Dev Agent figures out the transport details based on standard MCP patterns).

### Directory Structure Requirements

```
coretext/
├── gemini-extension.json       # <--- NEW
├── commands/                   # <--- NEW
│   └── coretext.toml           # <--- NEW
├── extension.yaml              # <--- DELETE
...
```

### Previous Learnings & Anti-Patterns

-   **Don't mix formats:** Ensure `extension.yaml` is gone. Don't leave it as a "backup".
-   **Path issues:** Absolute paths in dev environments break when moved. Use `${extensionPath}`.
-   **Port conflicts:** If the daemon uses a fixed port, multiple instances (or restarts) can crash. Ensure the `start` command handles "already running" gracefully or uses dynamic ports if Gemini manages the lifecycle completely.

### References

-   `_bmad-output/planning-artifacts/sprint-change-proposal-2026-01-09.md`
-   `docs/architecture.md` (Updated structure)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List
- Verified removal of extension.yaml and updated all references.
- Created gemini-extension.json with mcpServers configuration using ${extensionPath} and python3 -m coretext.main adapter.
- Created commands/coretext.toml with ALL 11 CoreText CLI commands (init, start, stop, status, lint, sync, apply-schema, new, install-hooks, inspect, ping).
- Updated coretext/main.py to be a runnable entry point.
- Implemented coretext/cli/adapter.py to bridge MCP Stdio to HTTP Daemon.
- Added adapter command to CLI.
- Verified manifest, command list, and adapter configuration via automated tests (tests/test_extension_integration.py).
- Verified environmental setup via tests/integration/test_dogfooding_setup.py.
- Updated README.md with Gemini CLI Extension usage guide.
- Updated docs/release-demo-guide.md with Gemini CLI agent demo scenario.

### File List
- gemini-extension.json
- commands/coretext.toml
- coretext/main.py
- coretext/cli/adapter.py
- coretext/cli/commands.py
- extension.yaml (deleted)
- scripts/verify_extension_integration.py
- tests/test_extension_integration.py
- tests/test_scaffolding.py
- tests/integration/test_dogfooding_setup.py
- _bmad-output/planning-artifacts/project_context.md
- .coretext/config.yaml
- README.md
- docs/release-demo-guide.md