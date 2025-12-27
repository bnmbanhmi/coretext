# Test Design: Epic 1 - Core Knowledge Graph Foundation

**Date:** 2025-12-04
**Author:** Murat (TEA Agent)
**Status:** Draft

---

## Executive Summary

**Scope:** Full test design for Epic 1 (Core Knowledge Graph Foundation). Focus on scaffolding, database management, and synchronization logic.

**Risk Summary:**

- Total risks identified: 4
- High-priority risks (≥6): 2
- Critical categories: OPS, TECH

**Coverage Summary:**

- P0 scenarios: 5 (10 hours)
- P1 scenarios: 4 (4 hours)
- P2/P3 scenarios: 3 (1.5 hours)
- **Total effort:** 15.5 hours (~2 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-101 | OPS | SurrealDB binary download fails or permission denied during `init` | 2 (Possible) | 3 (Critical) | 6 | Implement robust retry logic, clear permission checks, and manual install fallback instructions. | Dev | Story 1.2 |
| R-102 | DATA | Schema mismatch between Pydantic models and SurrealDB state causing data corruption | 2 (Possible) | 3 (Critical) | 6 | Implement strict "Schema Projection" with automated application on startup. Fail fast on mismatch. | Dev | Story 1.2 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-103 | TECH | Git hook performance exceeds 1s, blocking developer workflow | 2 (Possible) | 2 (Degraded) | 4 | Implement Async Mode with timeout detection (Story 4.1). | Dev |
| R-104 | TECH | Python environment dependency conflicts (e.g., pydantic v1 vs v2) | 2 (Possible) | 2 (Degraded) | 4 | Strict poetry dependency pinning and `pyproject.toml` constraints. | Dev |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------ |
| R-105 | BUS | Malformed Markdown parsing errors frustrate users | 1 (Unlikely) | 2 (Degraded) | 2 | Implement "Loud Failures" with clear line-number reporting (Story 3.4). |

### Risk Category Legend

- **TECH**: Technical/Architecture (flaws, integration, scalability)
- **SEC**: Security (access controls, auth, data exposure)
- **PERF**: Performance (SLA violations, degradation, resource limits)
- **DATA**: Data Integrity (loss, corruption, inconsistency)
- **BUS**: Business Impact (UX harm, logic errors, revenue)
- **OPS**: Operations (deployment, config, monitoring)

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Blocks core journey + High risk (≥6) + No workaround

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Project Scaffolding (Story 1.1) | Unit | R-104 | 1 | Dev | Verify `pyproject.toml` and dir structure |
| DB Initialization (Story 1.2) | Integration | R-101 | 1 | Dev | Verify `surreal` binary download & startup |
| Schema Application (Story 1.2) | Integration | R-102 | 1 | Dev | Verify Pydantic models map to DB schema |
| Git Hook Trigger (Story 1.4) | E2E | R-103 | 1 | QA | Verify commit triggers sync |
| Markdown Parsing (Story 1.3) | Unit | R-102 | 1 | Dev | Verify valid BMAD MD -> Node conversion |

**Total P0**: 5 tests, 10 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk (3-4) + Common workflows

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Link Validation (Story 1.5) | Unit | - | 1 | Dev | Verify Standard Markdown Link extraction |
| Sync Logic (Story 1.4) | Integration | - | 1 | Dev | Verify file change -> DB update |
| Malformed MD Handling (Story 1.3) | Unit | R-105 | 1 | Dev | Verify error node creation |
| Extension Manifest (Story 1.1) | Unit | - | 1 | Dev | Verify `extension.yaml` validity |

**Total P1**: 4 tests, 4 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary features + Low risk (1-2) + Edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| Large Commit Sync (Story 1.4) | Performance | R-103 | 1 | QA | benchmark sync time with 10+ files |
| DB Persistence (Story 1.2) | Integration | - | 1 | Dev | Verify data persists across restarts |
| CLI Output Formatting (Story 1.1) | Component | - | 1 | Dev | Verify Rich output |

**Total P2**: 3 tests, 1.5 hours

### P3 (Low) - Run on-demand

**Criteria**: Nice-to-have + Exploratory + Performance benchmarks

| Requirement | Test Level | Test Count | Owner | Notes |
| ----------- | ---------- | ---------- | ----- | ----- |
| Windows/Linux Install | E2E | 1 | QA | Manual verify on other OSs |
| Network Flakiness | E2E | 1 | QA | Simulate network fail during download |

**Total P3**: 2 tests, 1 hour

---

## Execution Order

### Smoke Tests (<5 min)

**Purpose**: Fast feedback, catch build-breaking issues

- [ ] Verify `coretext` package imports
- [ ] Verify `coretext --help` runs
- [ ] Verify unit tests pass

**Total**: 3 scenarios

### P0 Tests (<10 min)

**Purpose**: Critical path validation

- [ ] DB Init Integration Test
- [ ] Schema Sync Integration Test
- [ ] Parser Unit Test (Basic)

**Total**: 3 scenarios

### P1 Tests (<30 min)

**Purpose**: Important feature coverage

- [ ] Git Hook Integration Test
- [ ] Link Validation Unit Test

**Total**: 2 scenarios

### P2/P3 Tests (<60 min)

**Purpose**: Full regression coverage

- [ ] Performance Benchmark
- [ ] Full Suite

**Total**: 2 scenarios

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
| -------- | ----- | ---------- | ----------- | ----- |
| P0 | 5 | 2.0 | 10 | Core infra setup tests |
| P1 | 4 | 1.0 | 4 | Standard logic |
| P2 | 3 | 0.5 | 1.5 | Simple validations |
| **Total**| **12**| **-** | **15.5** | **~2 days** |

### Prerequisites

**Test Data:**

- `tests/fixtures/valid_bmad/`: Set of valid BMAD markdown files.
- `tests/fixtures/malformed_bmad/`: Set of broken markdown files.
- `tests/fixtures/repo_state/`: Git repo simulation.

**Tooling:**

- `pytest`: Runner.
- `pytest-asyncio`: For async DB tests.
- `surreal`: Binary must be available for integration tests.

**Environment:**

- Local macOS (current).
- CI Environment (GitHub Actions) - Future.

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥95% (waivers required for failures)
- **Coverage Targets**: ≥80% for `coretext.core` logic.

### Non-Negotiable Requirements

- [ ] All P0 tests pass
- [ ] No high-risk (≥6) items unmitigated
- [ ] `pyproject.toml` and `extension.yaml` exist and are valid

---

## Mitigation Plans

### R-101: SurrealDB Download Failure (Score: 6)

**Mitigation Strategy:** Add `coretext/db/client.py` logic to check for existing binary, attempt download from primary URL, failover if needed (or just strict error report), and verify executable permission.
**Owner:** Dev
**Timeline:** Story 1.2

### R-102: Schema Mismatch (Score: 6)

**Mitigation Strategy:** `coretext/db/migrations.py` runs on daemon start. Computes hash of current Pydantic models vs stored schema hash. If different, applies schema definition.
**Owner:** Dev
**Timeline:** Story 1.2

---

## Approval

**Test Design Approved By:**

- [ ] Product Manager: {name} Date: {date}
- [ ] Tech Lead: {name} Date: {date}
- [ ] QA Lead: Murat Date: 2025-12-04

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `.bmad/bmm/testarch/test-design`
**Version**: 4.0 (BMad v6)
