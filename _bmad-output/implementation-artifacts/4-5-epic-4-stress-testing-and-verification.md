# Story 4.5: Epic 4 Stress Testing and Verification

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a `coretext` developer,
I want to perform comprehensive stress testing and verification of the Epic 4 features (async sync, performance optimizations, self-healing),
so that I can certify the system is robust, performant, and reliable under realistic usage conditions.

## Acceptance Criteria

1.  **Async Hook Verification**: Verify that the Git hook successfully detaches and runs in the background when the estimated sync time exceeds the threshold (2s), allowing the commit to complete immediately.
2.  **Fail-Open Policy**: Verify that if the sync process crashes or encounters a critical error, the Git commit is NOT blocked and the user is warned.
3.  **Query Latency Benchmark**: Verify that MCP topological queries (`search_topology`) respond within 500ms (95th percentile) even with a populated graph.
4.  **Resource Consumption**: Verify that the daemon's memory footprint remains below 50MB when idle and CPU priority for background tasks is properly managed.
5.  **Graph Self-Healing at Scale**: Verify that the self-healing routine correctly identifies and prunes dangling edges in a larger, more complex graph scenario without deleting valid data.
6.  **Load Simulation**: A stress test script is created to simulate a repository with a significant number of files (e.g., 100+) and inter-dependencies to validate stability.

## Tasks / Subtasks

- [ ] **Create Stress Test Data Generator**
  - [ ] Implement `scripts/generate_stress_data.py` to create a temporary directory with hundreds of inter-linked BMAD markdown files.
  - [ ] Ensure a mix of valid links, broken links, and various headers to create a dense graph.
- [ ] **Verify Async & Fail-Open Git Hook**
  - [ ] Create `tests/integration/test_hook_resilience.py`.
  - [ ] Test Case: Mock a slow sync operation (>2s) and assert hook exit code is 0 (immediate return) while background process continues.
  - [ ] Test Case: Mock a crash (exception) in `sync.py` and assert commit is allowed (exit code 0) with a stderr warning.
- [ ] **Benchmark MCP Latency**
  - [ ] Create `scripts/benchmark_latency.py`.
  - [ ] Measure RTT for `search_topology` and `get_dependencies` against the generated stress data.
  - [ ] Report p50, p95, and p99 latencies.
- [ ] **Verify Resource Consumption**
  - [ ] Create `tests/performance/test_resources.py`.
  - [ ] Use `psutil` to monitor Daemon RSS memory usage during idle and active states.
  - [ ] Assert idle memory < 50MB.
- [ ] **Verify Self-Healing at Scale**
  - [ ] Enhance `tests/integration/test_healing_integration.py` or create new `tests/performance/test_healing_scale.py`.
  - [ ] Introduce controlled corruption (delete random files/nodes) in the large dataset.
  - [ ] Run healing routine and verify graph integrity (no dangling edges).

## Dev Notes

- **Tools**:
  - Use `psutil` for resource monitoring (add to dev dependencies if needed, or assume available in env).
  - Use `time` module for simple latency checks.
  - Use `gitpython` for simulating commits in tests.
- **Async Testing**: Testing the "detach" behavior of the hook might require careful process management in the test suite (e.g., `subprocess.Popen`). Ensure tests don't leave zombie processes.
- **SurrealDB Performance**: If latency is high, consider adding indices to `file_path`, `in`, `out` fields in `GraphManager`.
- **Fail-Open Implementation**: Review `coretext/core/sync/engine.py` to ensure the `try...except` block covers the entire execution scope.

### Project Structure Notes

- **Scripts**: Place benchmarks and generators in `scripts/`.
- **Tests**: Group performance tests in `tests/performance/` (create if missing) or `tests/integration/`.

### References

- [Epic 4 Test Design](../planning-artifacts/test-design-epic-4.md)
- [Story 4.1: Async Hook](../implementation-artifacts/4-1-git-hook-async-mode-fail-open-policy.md)
- [Story 4.4: Self-Healing](../implementation-artifacts/4-4-graph-self-healing-integrity-checks.md)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
