# Test Design: Epic 2 - Agent Context Retrieval & Semantic Querying

**Date:** 2025-12-26
**Author:** Minh
**Status:** Draft

---

## Executive Summary

**Scope:** Full test design for Epic 2 (Agent Context Retrieval & Semantic Querying). Focuses on the "Brain" of the system—the MCP server, semantic search, and graph traversal.

**Risk Summary:**

- Total risks identified: 6
- High-priority risks (≥6): 4
- Critical categories: TECH, PERF, BUS

**Coverage Summary:**

- P0 scenarios: 4 (8 hours)
- P1 scenarios: 5 (5 hours)
- P2/P3 scenarios: 6 (3 hours)
- **Total effort:** 16 hours (~2 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-203 | TECH | **Semantic Search Accuracy**: Embeddings fail to capture topological relevance, leading to poor context. | 3 (Likely) | 3 (Critical) | **9** | Create evaluation dataset (golden set) of query-node pairs. Tune embedding model. | QA/Dev | 2026-01-05 |
| R-202 | TECH | **Daemon Lifecycle Failure**: Daemon fails to start, crash loops, or fails to bind, blocking all MCP calls. | 2 (Possible) | 3 (Critical) | **6** | Robust PID file management, startup retries, self-healing process manager. | Dev | 2026-01-02 |
| R-206 | PERF | **Query Latency > 500ms**: Search + Embedding + DB Lookup exceeds timeout, causing Agent lag. | 3 (Likely) | 2 (Degraded) | **6** | Optimize SurrealDB queries, async embedding generation, caching. | Dev | 2026-01-08 |
| R-209 | BUS | **Hallucination Induction**: Irrelevant context returned by MCP leads Agent to generate wrong code. | 2 (Possible) | 3 (Critical) | **6** | Strict confidence thresholds for vector search. Clear tool descriptions for Agent. | QA | 2026-01-05 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-201 | TECH | **MCP Integration Complexity**: Request/Response format mismatch with Gemini CLI. | 2 (Possible) | 2 (Degraded) | **4** | Strict adherence to MCP spec, unit tests for Pydantic models. | Dev |
| R-207 | PERF | **Memory Consumption**: Daemon exceeds 500MB RAM cap. | 2 (Possible) | 2 (Degraded) | **4** | Memory profiling, lazy loading of heavy libraries. | Dev |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------ |
| R-204 | SEC | Unauthorized Local Access | 1 (Unlikely) | 2 (Degraded) | **2** | Monitor |
| R-205 | SEC | Data Exposure via MCP | 1 (Unlikely) | 2 (Degraded) | **2** | Monitor |

### Risk Category Legend

- **TECH**: Technical/Architecture
- **SEC**: Security
- **PERF**: Performance
- **BUS**: Business Impact

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Blocks core Agent capability + High Risk (≥6)

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| **FR10**: Retrieve topologically relevant context | Integration | R-203, R-209 | 2 | QA | Validate against Golden Set (known query -> expected nodes). |
| **FR21**: Daemon Startup & Health Check | Integration | R-202 | 1 | Dev | Verify process start, PID file creation, port binding. |
| **FR22**: Response within 500ms | Performance | R-206 | 1 | Dev | Measure RTT for `search_topology` tool. |

**Total P0**: 4 tests, 8 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium Risk (3-4)

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| **FR12**: Traverse `depends_on` relationships | Integration | - | 2 | QA | Verify A->B->C dependency chain retrieval. |
| **FR9**: MCP Protocol Compliance | Unit | R-201 | 2 | Dev | Verify tool schema generation and error formats. |
| **FR11**: Provide Context to Agent | E2E | - | 1 | QA | Mock Agent call to MCP server and verify JSON response structure. |

**Total P1**: 5 tests, 5 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Edge cases + Low Risk

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| **FR10**: Search with empty query | Unit | - | 1 | Dev | Verify graceful handling. |
| **FR10**: Search with no matches | Unit | - | 1 | Dev | Verify empty list return (no errors). |
| **FR23**: Memory Usage Check | Performance | R-207 | 1 | Dev | Monitor RAM usage during stress test. |
| **FR12**: Circular Dependencies | Unit | - | 3 | Dev | Ensure graph traversal doesn't infinite loop. |

**Total P2**: 6 tests, 3 hours

---

## Execution Order

### Smoke Tests (<5 min)

**Purpose**: Fast feedback, catch build-breaking issues

- [ ] Daemon Health Check (`/health` returns 200) (Integration)
- [ ] Embedder Model Loading (Unit)

### P0 Tests (<10 min)

**Purpose**: Critical path validation

- [ ] Topology Search Accuracy (Golden Set) (Integration)
- [ ] Query Latency Check (Performance)
- [ ] Daemon Lifecycle (Start/Stop) (Integration)

### P1 Tests (<30 min)

**Purpose**: Important feature coverage

- [ ] Dependency Retrieval (Integration)
- [ ] MCP Tool Schema Validation (Unit)
- [ ] Error Handling Scenarios (Unit)

### P2 Tests (<60 min)

**Purpose**: Full regression coverage

- [ ] Circular Dependency Traversal (Unit)
- [ ] Memory Profiling (Performance)

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
| -------- | ----- | ---------- | ----------- | ----- |
| P0 | 4 | 2.0 | 8 | Complex integration with SurrealDB and Embeddings |
| P1 | 5 | 1.0 | 5 | Standard API/Unit tests |
| P2 | 6 | 0.5 | 3 | Edge cases |
| **Total**| **15**| **-** | **16** | **~2 days** |

### Prerequisites

**Test Data:**

- **Golden Set**: A `markdown_corpus` fixture with 10-20 linked files and a `queries.json` file mapping queries to expected file IDs.
- **Graph Factory**: Helper to seed SurrealDB with specific graph structures (cycles, trees, disconnected nodes).

**Tooling:**

- `pytest-asyncio` for async FastAPI/DB tests.
- `httpx` for integration testing against running daemon.
- `surrealdb` python client (mocked for unit, real for integration).

**Environment:**

- Local SurrealDB instance (managed by test fixture).
- Nomic Embed Model (cached locally).

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (Blocking)
- **Search Accuracy**: Recall@3 > 80% (Blocking for R-203)
- **Latency**: p95 < 500ms (Blocking for R-206)
- **High-risk mitigations**: All R-203, R-202, R-206, R-209 mitigations implemented.

### Non-Negotiable Requirements

- [ ] Daemon MUST bind only to 127.0.0.1 (Security).
- [ ] Graph traversal MUST NOT infinite loop on cycles.

---

## Mitigation Plans

### R-203: Semantic Search Accuracy (Score: 9)

**Mitigation Strategy**:
1. Create a "Golden Set" of 20 queries and expected document matches.
2. Implement an evaluation script to calculate Recall@K.
3. If accuracy is low, fine-tune chunking strategy (e.g., include parent header context).

**Owner**: QA/Dev
**Status**: Planned

### R-202: Daemon Lifecycle Failure (Score: 6)

**Mitigation Strategy**:
1. Implement a PID file lock mechanism.
2. Add a `check_port` routine before startup to handle "Port Already in Use".
3. Add a 3-retry loop for daemon startup in the CLI.

**Owner**: Dev
**Status**: Planned

---

## Approval

**Test Design Approved By:**

- [ ] Product Manager: Minh Date: 2025-12-26
- [ ] Tech Lead: Minh Date: 2025-12-26
- [ ] QA Lead: Murat Date: 2025-12-26

**Comments**:
Focus heavily on the "Golden Set" for search accuracy. This is the make-or-break for the AI agent's performance.

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `.bmad/bmm/testarch/test-design`
**Version**: 4.0 (BMad v6)
