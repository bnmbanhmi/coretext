# Story 5.2: Directory Selection & Gap Analysis

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Developer using CoreText,
I want to identify and close gaps in the product's features,
so that the system is fully ready for release.

## Acceptance Criteria

1.  **Directory Selection**: The system supports a `docs_dir` setting to scope document scanning (Completed).
2.  **Gap Analysis**: Execute the demo guide and identify remaining missing features or bugs.
3.  **Feature Implementation**: Implement identified "must-have" features for release.

## Tasks / Subtasks

### Completed: Directory Selection Feature
- [x] Task 1: Update Configuration Schema (AC: 1)
  - [x] Update `coretext/config.py` `Config` model to include `docs_dir`.
  - [x] Update `DEFAULT_CONFIG_CONTENT` to include the new field.
- [x] Task 2: Enhance CLI Initialization (AC: 1)
  - [x] Update `coretext/cli/commands.py` `init` command.
  - [x] Add Typer prompt for directory selection.
  - [x] Implement directory validation logic.
  - [x] Save selection to config file.
- [x] Task 3: Update Sync Logic (AC: 1)
  - [x] Update `coretext/cli/commands.py` `sync` command.
  - [x] Read `docs_dir` from config.
  - [x] Set `target_path` based on config if not overridden by arguments.
- [x] Task 4: Update Lint Logic (AC: 1)
  - [x] Update `coretext/server/routers/lint.py`.
  - [x] Ensure `lint_endpoint` reads config and scans the correct directory.

### Completed: Gap Analysis - Authentication & Stability
- [x] Task 5: Resolve Port Conflicts (AC: 2)
  - [x] Migrated default daemon port from 8000 to 8010 to avoid common system conflicts.
  - [x] Updated `config.py` and `dependencies.py` to reflect the new default.
- [x] Task 6: Stabilize SurrealDB Connection (AC: 2)
  - [x] Implemented a strictly Unauthenticated Mode for local development to bypass SurrealDB 2.x credential issues.
  - [x] Added explicit `await db.connect()` calls to all database interaction points.
  - [x] Added a 1-second stabilization delay in `start_surreal_db` to ensure WebSocket readiness.
- [x] Task 7: Improve Error Visibility (AC: 2)
  - [x] Updated Git hooks to print fatal errors to stderr instead of failing silently.
  - [x] Changed default log level to `DEBUG` in config for easier troubleshooting.

### Upcoming: Release Polishing
- [ ] Task 8: Execute Final Release Demo Guide (`docs/release-demo-guide.md`)
- [ ] Task 9: Document final release findings in `docs/gap-analysis.md`
- [ ] Task 10: Implement remaining "nice-to-have" UI/CLI polish

## Dev Notes

- **Port Strategy**: Moved to 8010/8001 to isolate CoreText from other SurrealDB/FastAPI instances.
- **Auth Strategy**: Purely unauthenticated local-first mode. Removed all `signin` calls and credential flags.
- **Connection**: `AsyncSurreal` requires an explicit `connect()` call before `use()`.

### Project Structure Notes

- **Config**: `coretext/config.py` (Default port and log level)
- **CLI**: `coretext/cli/commands.py` (Sync, Hook, and Schema logic)
- **Server**: `coretext/server/dependencies.py` (DB client provider)
- **DB**: `coretext/db/client.py` (Binary startup logic)

### References

- [Source: docs/epic-4-demo-guide.md] (Discovery source for these gaps)

## Dev Agent Record

### Agent Model Used

Gemini-Pro

### Debug Log References

- [Auth Error]: `{'code': -32000, 'message': 'There was a problem with authentication'}`
- [Port Conflict]: `Warning: Port 8000 is already in use`

### Completion Notes List

- Migrated to Port 8010.
- Implemented unauthenticated mode.
- Fixed `signin` signature mismatch.
- Fixed `NameError` in `_apply_schema_logic`.

### File List

- `coretext/config.py`
- `coretext/cli/commands.py`
- `coretext/server/dependencies.py`
- `coretext/db/client.py`