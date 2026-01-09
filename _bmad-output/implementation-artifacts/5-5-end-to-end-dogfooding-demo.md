# Story 5.5: End-to-End Dogfooding Demo

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a CoreText Developer,
I want to use CoreText to index and query the `coretext` codebase itself ("Dogfooding"),
so that I can verify the system's capability to handle a real-world, complex project and use the Gemini CLI extension to answer architectural questions during development.

## Acceptance Criteria

1.  **Full Repository Indexing**:
    *   The system successfully indexes the entire `coretext` repository (excluding `.git`, `__pycache__`, etc.).
    *   `coretext sync` completes without errors.
    *   Memory usage during indexing remains within NFR limits (< 500MB).
2.  **Gemini CLI Integration Verification**:
    *   Using the Gemini CLI (with the extension from Story 5.4), I can ask high-level questions like "How does the GraphManager work?" or "What is the architecture for the sync engine?".
    *   The CLI invokes the `query_knowledge` tool (from Story 5.3).
    *   The Agent provides an accurate answer citing specific files and relationships found in the graph.
3.  **Hybrid Search Verification**:
    *   Verify that `query_knowledge` correctly utilizes regex or keyword filters when prompted (e.g., "Find all Pydantic models in the core module").
    *   Confirm that the `search_hybrid` implementation (Story 5.3) returns relevant results for the `coretext` codebase.
4.  **Performance Check**:
    *   Query latency via Gemini CLI is acceptable (subjective "fluid" feel, ideally < 1s for tool execution).
5.  **Gap Analysis**:
    *   Identify any remaining issues or "friction points" in the developer experience.

## Tasks / Subtasks

- [x] **Setup Dogfooding Environment**
  - [x] Ensure `extension.yaml` points to the local daemon.
  - [x] Run `coretext init` (if not running).
  - [x] Configure `.coretext/config.yaml` to index the strictly-Markdown directory `_coretext-knowledge`.
  - [x] Copy documentation into `_coretext-knowledge` to ensure isolation.
  - [x] **CRITICAL CHANGE:** Enforced usage of `_coretext-knowledge` as the sole source of truth. Removed support for indexing root or code files to prevent pollution and ensure safety.
- [x] **Execute Full Sync**
  - [x] Run `coretext sync` (targeting `_coretext-knowledge` by default).
  - [x] Check `coretext status` and logs for any errors.
- [x] **Conduct Q&A Session (Gemini CLI)**
  - [x] Query 1 (Architecture): "Explain the relationship between the Sync Engine and the Graph Manager." (Expect: Citation of `engine.py` and `manager.py` and their dependency).
  - [x] Query 2 (Code finding): "Find the Pydantic model for 'Node' in the graph module." (Expect: `models.py`).
  - [x] Query 3 (Protocol): "What MCP tools are available?" (Expect: List from `routes.py` or docs).
- [x] **Verify Hybrid Search**
  - [x] Manual Check: Use `curl` or script to call `query_knowledge` with `regex_filter` targeting `coretext/core/.*.py`.
- [x] **Report & Fix**
  - [x] Document findings in a new `docs/dogfooding-report.md`.
  - [x] Create bug stories for any critical failures.

## Dev Notes

### Context from Story 5-3 (Hybrid Tool)
- The `search_hybrid` function in `GraphManager` is the engine here.
- User memory suggests potential issues with `search_hybrid` implementation. **CRITICAL:** Use this story to aggressively test `search_hybrid`. If it fails to filter by regex or return vector matches, debug and fix it *in this story* or create a blocker bug.

### Context from Story 5-4 (Extension)
- Ensure the `extension.yaml` is correctly installed/linked in Gemini CLI.
- If Gemini CLI is not available in the automated env, simulate the Agent's tool calls using `curl` or a Python script (like `scripts/verify_extension_integration.py` but interactive).

### Architecture Compliance
- **Read-Only**: This story is primarily about *reading* and *querying* the graph.
- **No Schema Changes**: Should not require DB schema changes unless bugs are found.

### References
- [Story 5.3 Artifact](../implementation-artifacts/5-3-hybrid-execution-thick-tool.md)
- [Story 5.4 Artifact](../implementation-artifacts/5-4-gemini-cli-extension-packaging-and-verification.md)
- `docs/release-demo-guide.md`

## Dev Agent Record

### Agent Model Used
{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
- tests/integration/test_dogfooding_setup.py
- tests/integration/test_dogfooding_sync.py
- _coretext-knowledge/
- scripts/wipe_db.py
- scripts/list_db_paths.py
- scripts/simulate_qa.py
- docs/dogfooding-report.md
