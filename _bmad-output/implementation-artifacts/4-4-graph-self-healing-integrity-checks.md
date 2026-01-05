# Story 4.4: Graph Self-Healing & Integrity Checks

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a `coretext` system,
I want to automatically maintain the integrity of the knowledge graph,
so that broken links and outdated nodes don't accumulate and degrade its accuracy over time.

## Acceptance Criteria

1.  **Automatic Pruning**: On system initialization (daemon startup), a self-healing routine automatically scans for and removes "Dangling Edges" (edges where the `in` or `out` node no longer exists).
2.  **Orphan Node Cleanup**: The routine identifies and archives or removes "Orphan Nodes" (nodes that are not file roots and have no incoming edges from a valid parent) if they are remnants of deleted content.
    *   *Refinement*: Be careful not to delete valid isolated nodes if the schema allows them. For now, focus on *Dangling Edges* as the primary integrity failure.
3.  **Startup Integration**: The healing process runs as a non-blocking background task during the daemon startup sequence (`lifespan` startup event).
4.  **Reporting**: Significant healing actions (e.g., "Pruned 50 dangling edges") are logged to the application logs (and visible in `coretext status` logs or similar if implemented).
5.  **Manual Trigger**: The healing routine can be triggered manually via an internal API call (to support future `coretext heal` CLI commands).

## Tasks / Subtasks

- [ ] **Enhance GraphManager with Healing Logic**
  - [ ] Implement `coretext/core/graph/manager.py::prune_dangling_edges()`
    - [ ] Query: `DELETE FROM edge WHERE in = NONE OR out = NONE` (or SurrealQL equivalent checking existence).
    - [ ] Query: `DELETE FROM edge WHERE in.id IS NULL OR out.id IS NULL` (Verify SurrealQL behavior for deleted nodes).
  - [ ] Implement `coretext/core/graph/manager.py::prune_orphan_headers()`
    - [ ] Logic: Remove Header nodes that no longer have a `CONTAINS` relationship from a File node.
- [ ] **Implement Startup Routine**
  - [ ] Create `coretext/core/system/maintenance.py` (or keep in `graph/maintenance.py`) to coordinate these checks.
  - [ ] Add async task in `coretext/server/app.py` startup event.
  - [ ] Ensure it runs *after* the initial DB connection is established.
- [ ] **Logging & Telemetry**
  - [ ] Log count of removed items.
  - [ ] Log warnings if an unusually high number of items (>1000) are pruned (potential data loss indicator).
- [ ] **Unit & Integration Tests**
  - [ ] Test: Create a graph with intentional dangling edges (delete a node without deleting edges).
  - [ ] Run healing.
  - [ ] Assert edges are gone.

## Dev Notes

- **SurrealDB Behavior**: When a node is deleted in SurrealDB, edges connected to it might remain as "ghost" edges depending on how the deletion happened (record deletion vs graph relational integrity). SurrealDB does *not* strictly enforce referential integrity by default unless `ON DELETE CASCADE` is defined in schema.
- **Schema Strategy**: Since we are using "Schema Projection" (Pydantic models), we might not have `DEFINE FIELD ... ON DELETE CASCADE` in the DB. Explicit cleanup is safer.
- **Query Pattern**:
  ```sql
  -- Find edges where start or end doesn't exist
  SELECT * FROM edge WHERE out IS NULL OR in IS NULL;
  -- or
  DELETE edge WHERE out = NONE OR in = NONE;
  ```
  *Verify exact SurrealQL syntax for checking existence of linked record.*

### Project Structure Notes

- **Module**: `coretext/core/graph/` is the right place for the logic.
- **Service**: `coretext/server/app.py` for the trigger.

### References

- [SurrealDB DELETE statement](https://surrealdb.com/docs/surrealql/statements/delete)
- [Project Architecture - System Reliability](../planning-artifacts/architecture.md)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
