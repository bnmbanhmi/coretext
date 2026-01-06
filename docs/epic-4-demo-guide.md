# Epic 4 Demo Guide: Resilience & Performance

**Goal**: Verify that CoreText handles scale, latency, and failures gracefully.

## Prerequisites

1.  **SurrealDB** running (`coretext init` has been run).
2.  **Python Environment** active.
3.  **Dependencies** installed (`poetry install`).

## Demo Scenarios

### 1. Stress Data Generation

**What**: Create a dense graph of connected markdown files to simulate a real-world repo.
**Why**: Empty repos don't show performance issues.
**Action**:
```bash
python scripts/generate_stress_data.py --output _stress_demo --files 50 --density 0.3
```
**Verify**: Folder `_stress_demo` exists with ~50 files.

### 2. Latency Benchmark (Story 4.2)

**What**: Measure query response time on the dense graph.
**Why**: Ensure MCP tools respond <500ms even with load.
**Action**:
```bash
python scripts/benchmark_latency.py --dir _stress_demo
```
**Verify**: Output shows p95 latency < 500ms.

### 3. Async Git Hook (Story 4.1)

**What**: Trigger a "slow" sync and confirm the user isn't blocked.
**Why**: Developers shouldn't wait seconds for `git commit` to finish.
**Action**:
Run the interactive demo script:
```bash
python scripts/demo_epic_4.py --scenario async
```
**Verify**: The script simulates a 3s sync delay, but reports "Hook detached" immediately.

### 4. Fail-Open Policy (Story 4.1)

**What**: Simulate a crash in the daemon/sync engine.
**Why**: A bug in CoreText should NEVER prevent a git commit.
**Action**:
Run the interactive demo script:
```bash
python scripts/demo_epic_4.py --scenario fail-open
```
**Verify**: The script simulates a crash (Exception), but exits with Code 0 (Success) and prints a warning.

### 5. Self-Healing Graph (Story 4.4)

**What**: Delete a file externally and verify the graph cleans up without manual intervention.
**Why**: The graph must stay consistent with the filesystem.
**Action**:
1.  Run `coretext sync` on `_stress_demo`.
2.  Delete `_stress_demo/file_0.md`.
3.  Run `coretext sync` again (or use the demo script).
4.  Inspect graph to verify node `file_0.md` is gone.
**Verify**: Node count decreases by 1 (and associated edges are removed).

## Running the Automated Demo

We have prepared a unified script to run these checks interactively:

```bash
python scripts/demo_epic_4.py
```

Select the scenarios from the menu to verify each component.
