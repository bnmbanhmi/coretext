# Test Design: Epic 4 - System Reliability & Performance Optimization

**Date:** 2026-01-03
**Author:** Minh
**Status:** Approved

---

## Executive Summary

**Scope:** Epic-level test design for System Reliability & Performance Optimization.

**Risk Summary:**

- Total risks identified: 6
- High-priority risks (≥6): 3
- Critical categories: TECH, DATA, PERF

**Coverage Summary:**

- P0 scenarios: 3 (6 hours)
- P1 scenarios: 3 (3 hours)
- P2/P3 scenarios: 3 (1.25 hours)
- **Total effort**: 10.25 hours (~1.3 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-001   | TECH     | Data Inconsistency: Async sync might fail silently, leading to drift between Git and Graph. | 3 | 3 | 9 | Implement robust logging, "status" command warning, and retry mechanism. | Dev | TBD |
| R-002   | PERF     | Latency Miss: Complex topological queries might exceed 500ms on large graphs. | 3 | 2 | 6 | Query optimization, caching, and database indexing. | Dev | TBD |
| R-003   | DATA     | False Positives in Self-Healing: Pruning logic might delete valid edges if graph state is transient. | 2 | 3 | 6 | Strict validation before delete, "soft delete" or dry-run logging first. | Dev | TBD |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-004   | OPS      | Resource Cap Violation: Python memory management is tricky; 50MB limit might be breached easily. | 2 | 2 | 4 | Memory profiling, aggressive GC, optimize object slots. | Dev |
| R-005   | TECH     | Async Detachment Failure: "Fail-Open" might not work if the hook process itself hangs/crashes badly. | 2 | 2 | 4 | Timeouts in the parent hook wrapper. | Dev |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------ |
| R-006   | OPS      | CPU Priority: `nice` might not be available or effective on all dev environments. | 2 | 1 | 2 | Monitor, document limitations. |

### Risk Category Legend

- **TECH**: Technical/Architecture
- **SEC**: Security
- **PERF**: Performance
- **DATA**: Data Integrity
- **BUS**: Business Impact
- **OPS**: Operations

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Blocks core journey + High risk (≥6) + No workaround

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Fail-Open Policy | E2E | R-005 | 2 | QA | Simulate hook crash, ensure commit succeeds. |
| Data Consistency | Integration | R-001 | 3 | QA | Verify graph state after async sync completion. |
| Self-Healing Safety | Integration | R-003 | 2 | QA | Verify no valid edges are deleted. |

**Total P0**: 7 tests, 6 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk (3-4) + Common workflows

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Async Detachment | Integration | R-001 | 2 | Dev | Verify process detaches for long ops. |
| Query Latency | Performance | R-002 | 1 | QA | k6 benchmark for topological queries. |
| 50MB RAM Limit | Performance | R-004 | 1 | QA | Monitor memory usage under load. |

**Total P1**: 4 tests, 3 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary features + Low risk (1-2) + Edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| CPU Priority | Unit | R-006 | 1 | Dev | Verify `nice` call logic. |
| Specific Edge Pruning | Unit | R-003 | 5 | Dev | Various dangling edge scenarios. |

**Total P2**: 6 tests, 1 hour

### P3 (Low) - Run on-demand

**Criteria**: Nice-to-have + Exploratory + Performance benchmarks

| Requirement | Test Level | Test Count | Owner | Notes |
| ----------- | ---------- | ---------- | ----- | ----- |
| Stress Test 10k files | Performance | 1 | QA | Validate architecture scaling NFR. |

**Total P3**: 1 tests, 0.25 hours

---

## Execution Order

### Smoke Tests (<5 min)

- [x] Hook Fail-Open check (simulated error)
- [x] Basic Async Sync triggers

### P0 Tests (<10 min)

- [ ] Data consistency verification
- [ ] Self-healing safety check

### P1 Tests (<30 min)

- [ ] Latency benchmarks (k6)
- [ ] Memory usage check

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100%
- **P1 pass rate**: ≥95%
- **Latency**: 95th percentile < 500ms
- **Memory**: < 50MB Idle

---

## Mitigation Plans

### R-001: Data Inconsistency (Async)
**Mitigation Strategy:** Implement a robust "Sync Status" table in DB to track in-progress syncs. On next CLI command, check status and warn user if sync failed or is lagging.
**Verification:** Test case where async process is killed, then user runs `coretext status`.

### R-002: Latency Miss
**Mitigation Strategy:** Use SurrealDB indexing on `file_path` and `parent_id`. Cache embedding models in memory (already planned).
**Verification:** Load test with 10k nodes.

### R-003: False Positives in Self-Healing
**Mitigation Strategy:** "Soft Delete" first (mark as `_deleted`), then physical delete after confirmation or time window. Or just strict validation logic (check file existence on disk before deleting node).
**Verification:** Create graph node for non-existent file, run self-heal, verify deletion. Create graph node for existing file, run self-heal, verify retention.

---

**Generated by**: BMad TEA Agent