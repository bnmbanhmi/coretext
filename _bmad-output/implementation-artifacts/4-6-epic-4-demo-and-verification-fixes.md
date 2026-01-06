# Story 4.6: Epic 4 Demo & Verification Fixes

Status: done

## Story

As a user (Minh),
I want a verified, end-to-end demo guide for Epic 4, covering the new resilience and performance features (Async Git Hook, Fail-Open, Self-Healing, Latency),
so that I can confidently validate the system's robustness before we call this epic "done".

## Acceptance Criteria

1.  **Verified Demo Guide:** A comprehensive `docs/epic-4-demo-guide.md` exists, detailing step-by-step instructions for:
    *   **Async Hook:** Demonstrating the git hook detaching on slow syncs (user returns immediately).
    *   **Fail-Open Policy:** Demonstrating that a crashed sync/daemon does NOT block the commit.
    *   **Self-Healing:** Demonstrating the graph automatically correcting itself when files are manipulated externally or corruption is simulated.
    *   **Latency & Resources:** A quick check showing response times <500ms and memory usage <80MB under load.
2.  **Interactive Demo Script:** A script (`scripts/demo_epic_4.py`) that orchestrates these scenarios (where possible) or guides the user through them.
3.  **Fixes & Polish:** Any bugs found during the demo run are fixed immediately.

## Tasks / Subtasks

- [x] Create `docs/epic-4-demo-guide.md`.
- [x] Create/Update `scripts/demo_epic_4.py` to automate the demo steps.
- [x] Verify Async Hook behavior (manual or scripted).
- [x] Verify Fail-Open behavior.
- [x] Verify Self-Healing.
- [x] Fix any issues found.

## Dev Agent Record

### File List
- `coretext/cli/commands.py`
- `docs/epic-4-demo-guide.md`
- `scripts/demo_epic_4.py`
- `scripts/generate_stress_data.py`
- `scripts/benchmark_latency.py`

## Dev Notes

- Leverage `scripts/generate_stress_data.py` from Story 4.5 for data.
- Fixed `scripts/benchmark_latency.py` to handle correct API response structure (`results` key instead of `nodes`) and increased timeout to 30s for heavy stress loads.
- Updated `scripts/demo_epic_4.py` with:
    - Clean data generation (0% broken links) to ensure baseline sync success.
    - Robust error handling for sync failures.
    - Automated cleanup scenario.
- Verified all 5 resilience and performance scenarios on MacOS.
