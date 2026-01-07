# Sprint Change Proposal

**Date:** 2026-01-07
**Author:** Unit-734 (Gemini Agent)
**Trigger:** User Request (Scope Refinement)

## 1. Issue Summary

**Problem:** Epic 5 contained two "Research/Verification" tasks (5.3 Agent Skills, 5.5 MCP Compliance) that were misclassified as development stories. This cluttered the backlog with non-functional items.
**Context:** Identified during Sprint Planning/Review on 2026-01-07.

## 2. Impact Analysis

*   **Epic Impact:** Epic 5 is now leaner and focused purely on "Product Release" deliverables (Packaging & Dogfooding).
*   **Story Impact:**
    *   Removed: Story 5.3 (Agent Skills Research) & Story 5.5 (MCP Compliance).
    *   Renumbered: Story 5.4 -> 5.3 (CLI Extension).
    *   Renumbered: Story 5.6 -> 5.4 (Dogfooding Demo).
*   **Artifact Conflicts:** `epics.md` and `sprint-status.yaml` required updates.

## 3. Recommended Approach

**Refine Scope:** Move research tasks to a separate `external_tasks` tracking list to keep the development backlog "pure" (coding tasks only).

## 4. Detailed Change Proposals

**Artifact: `epics.md`**
*   Removed Sections 5.3 and 5.5.
*   Renumbered remaining stories to fill gaps.

**Artifact: `sprint-status.yaml`**
*   Added `external_tasks` section.
*   Moved research items to `external_tasks`.
*   Added new 5.3 and 5.4 to `epic-5` backlog.

## 5. Implementation Handoff

**Scope:** Minor (Documentation update only).
**Status:** ✅ Completed by Agent.

**Next Steps:**
*   Developer to pick up new Story 5.3 (CLI Extension Packaging).
*   PO/Architect to conduct the external research tasks offline.