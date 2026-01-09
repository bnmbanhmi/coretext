# Sprint Change Proposal: Gemini CLI Extension Integration Fix

**Date:** 2026-01-09
**Author:** Minh / CoreText Team
**Status:** Proposed

## 1. Issue Summary

**Problem:** The current project plan relies on a deprecated or insufficient `extension.yaml` format for Gemini CLI integration. It lacks the necessary lifecycle management configuration (`command`, `args`, `cwd`) required by the Gemini CLI to properly spawn and manage the CoreText MCP server and custom commands.

**Discovery:** Identified during technical review of the extension packaging requirements. The Gemini CLI requires a `gemini-extension.json` manifest and a specific directory structure to function correctly.

**Evidence:**
- Current `extension.yaml` only supports simple URL references.
- Valid extensions require `gemini-extension.json` with `mcpServers` definitions using `${extensionPath}`.

## 2. Impact Analysis

### Epic Impact
- **Epic 1 (Foundation):** `Story 1.1` scaffolding must now generate `gemini-extension.json` instead of `extension.yaml`.
- **Epic 5 (Release):** `Story 5.4` was insufficient. A new `Story 5.6` has been added to explicitly handle the packaging and manifest creation according to the standard.

### Artifact Conflicts
- **Architecture:** The project structure in `architecture.md` was outdated. It has been updated to replace `extension.yaml` with `gemini-extension.json` and add the `commands/` directory.
- **PRD:** Implicitly affected; the "Integration Model" now strictly follows the Gemini CLI Extension standard.

## 3. Recommended Approach

**Path Forward:** **Direct Adjustment**
We have modified the planning artifacts to align with the correct technical standard. This does not require a rollback or scope reduction, but rather a **correction of technical details** to ensure the product works as intended.

**Rationale:**
- **Necessity:** Without this fix, the extension simply will not install or run in the target environment.
- **Low Risk:** The change is purely configuration and packaging; it does not alter the core logic of the knowledge graph or AST parsing.

## 4. Detailed Change Proposals

### Architecture Updates
- **File Structure:** Updated to include `gemini-extension.json` and `commands/`.
- **Manifest Format:** Switched from YAML to JSON.

### Epic Updates
- **Story 1.1:** Updated acceptance criteria to scaffold the correct JSON manifest.
- **Story 5.4:** Refined to focus on valid MCP server configuration.
- **Story 5.6 (New):** Added to specifically address "Gemini CLI Extension Manifest & Command Packaging", including the requirement for `${extensionPath}` usage and TOML command definitions.

## 5. Implementation Handoff

**Scope:** **Minor/Moderate**
The changes are well-defined and contained within the packaging and initialization logic.

**Route To:**
- **Development Team:** Implement the updated Story 1.1 (Scaffolding) and the new Story 5.6 (Packaging).
- **QA/Verification:** Verify installation using `gemini extensions link .`.

**Success Criteria:**
- `coretext` can be installed via `gemini extensions link .`.
- The MCP server starts automatically when the Gemini CLI is used.
- Custom commands (if any) defined in `commands/*.toml` are available in the CLI.
