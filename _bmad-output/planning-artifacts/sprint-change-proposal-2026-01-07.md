# Sprint Change Proposal

**Date:** 2026-01-07
**Project:** coretext
**Scope:** Epic 5 (Release Readiness)
**Trigger:** User Requirement for MCP/Extension Verification & Agent Skills Research

## 1. Issue Summary

**Problem:**
The current project plan (specifically Epic 5) covers the implementation of the `coretext` tool but lacks explicit verification for:
1.  **MCP Protocol Adherence:** Ensuring the server strictly follows the Model Context Protocol.
2.  **Gemini CLI Extension Compatibility:** Verifying the tool operates correctly when loaded as an extension (via `extension.yaml`) rather than just a standalone Python module.
3.  **End-to-End Agent Usability:** Proving the Gemini Agent can actually use the tool ("dogfooding").
4.  **Agent Skills Compatibility:** Clarity on whether `coretext` needs to support Anthropic's "Agent Skills" format.

**Impact:**
Without these verifications, we risk releasing a tool that technically works in isolation but fails when integrated into the actual user workflow (Gemini CLI) or violates the protocol it claims to support.

## 2. Impact Analysis

*   **Epics:** Epic 5 (Release Readiness) is significantly expanded. No changes to Epics 1-4.
*   **PRD:** Success Criteria should be updated to include "Verified Gemini CLI Extension Compatibility."
*   **Demo Guide:** Needs to include a section where the Agent itself interacts with the tool.

## 3. Recommended Approach: Direct Adjustment

We will **expand Epic 5** by adding 4 specific stories. This avoids disrupting the current implementation flow of Epics 1-4 while ensuring the final release meets the enhanced quality standards.

## 4. Detailed Change Proposals

### Artifact: `planning-artifacts/epics.md`

**Add the following stories to Epic 5:**

#### Story 5.3: Research & Definition: Agent Skills Compatibility
*   **Goal:** Deeply analyze the "Agent Skills" spec to decide if `coretext` should support *exporting* BMAD content to the `SKILL.md` format, or if `coretext` itself should be structured as a Skill.
*   **Deliverable:** A design document or decision record (ADR) on "Coretext vs. Agent Skills".

#### Story 5.4: Gemini CLI Extension Packaging & Verification
*   **Goal:** Configure and verify `coretext` as a valid Gemini CLI Extension.
*   **Acceptance Criteria:**
    *   `extension.yaml` is validated against the official schema.
    *   `mcpServers` definition correctly points to the `coretext` daemon.
    *   `gemini extensions install .` works successfully in a clean environment.

#### Story 5.5: MCP Protocol Compliance Verification
*   **Goal:** Verify the `coretext` MCP Server against the official Model Context Protocol specification.
*   **Acceptance Criteria:**
    *   Use an MCP Inspector (e.g., from `modelcontextprotocol/inspector`) or test suite.
    *   Validate JSON-RPC messages, tool schema definitions, and error handling.
    *   Zero critical protocol violations.

#### Story 5.6: End-to-End "Dogfooding" Demo
*   **Goal:** Update the `release-demo-guide.md` to include a "Meta-Test".
*   **Acceptance Criteria:**
    *   Demo includes a step: "Ask Gemini Agent: 'Explain the dependency structure of GraphManager'."
    *   Agent successfully calls `coretext` tools.
    *   Agent provides correct answer based on graph data.

### Artifact: `planning-artifacts/prd.md`

**Update "Success Criteria" section:**
*   Add: "**Gemini Extension Native:** The tool is verified to install and function seamlessly as a `gemini` extension."
*   Add: "**MCP Compliance:** The server passes standard MCP protocol validation tests."

## 5. Implementation Handoff

*   **Change Scope:** **Minor/Moderate**. (Adds work, but fits within existing release phase).
*   **Routing:**
    *   **Developer (Minh/Agent):** Implement Stories 5.3 - 5.6.
    *   **QA:** Execute the new "Dogfooding" demo steps.

---

**Approval Required:**
Do you approve this Sprint Change Proposal?
**[yes]** Proceed to update artifacts.
**[no]** Revise proposal.
