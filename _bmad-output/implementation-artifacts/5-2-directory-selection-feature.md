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

### Upcoming: Gap Analysis & Polishing
- [ ] Task 5: Execute Release Demo Guide (`docs/release-demo-guide.md`)
- [ ] Task 6: Document findings in `docs/gap-analysis.md`
- [ ] Task 7: Propose and implement additional "must-have" features


## Dev Notes

- **Architecture**: This touches the Configuration layer (`config.py`), CLI layer (`commands.py`), and Server layer (`routers/lint.py`).
- **Patterns**: Follow the existing pattern of loading config via `load_config`.
- **Validation**: Ensure strict validation of paths to prevent security issues (though primarily local).

### Project Structure Notes

- **Config**: `coretext/config.py`
- **CLI**: `coretext/cli/commands.py`
- **Server**: `coretext/server/routers/lint.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 3: Developer Workflow Integration & Tooling] (Related to tooling improvements)
- [Source: README.md#Configuration]

## Dev Agent Record

### Agent Model Used

Gemini-Pro

### Debug Log References

### Completion Notes List

### File List