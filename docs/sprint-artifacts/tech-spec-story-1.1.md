# Tech-Spec: Project Setup & Storage Service (Story 1.1)

**Created:** 2025-12-03
**Status:** Completed

## Overview

### Problem Statement
The application needs a foundational layer to persist data. Without it, tasks are lost when the program exits. We need a robust way to initialize the data store and handle read/write operations safely.

### Solution
Implement a `storage.py` module that manages a local `tasks.json` file. It will handle file initialization, JSON serialization/deserialization, and error handling. This module will be the single source of truth for data IO.

### Scope (In/Out)
**In Scope:**
- Creating `tasks.json` if missing.
- Reading list of tasks.
- Writing list of tasks.
- Basic JSON validation (catching decode errors).

**Out of Scope:**
- Database implementation (SQLite, etc.).
- Advanced querying or filtering (handled by Manager later).
- CLI commands (handled by CLI module).

## Context for Development

### Codebase Patterns
- **Module:** `storage.py`
- **Data Format:** JSON List of Dicts.
- **Error Handling:** Raise standard Python exceptions (`FileNotFoundError`, `json.JSONDecodeError`) or handle gracefully where appropriate (e.g., empty file = empty list).

### Files to Reference
- `docs/architecture.md` (Section 3.3 Storage Service)
- `docs/epics.md` (Story 1.1)

### Technical Decisions
- **Path:** Store `tasks.json` in the current working directory for simplicity (MVP).
- **Format:** Standard JSON. `indent=4` for human readability during dev.

## Implementation Plan

### Tasks

- [x] Create `storage.py` file.
- [x] Implement `_get_file_path()` helper (optional, good practice).
- [x] Implement `load_tasks() -> list[dict]`
    - Check if file exists.
    - If no, create empty list `[]` and write file.
    - If yes, read and parse JSON.
- [x] Implement `save_tasks(tasks: list[dict]) -> None`
    - Open file in write mode.
    - Dump data with indentation.
- [x] Create `test_storage.py` using `unittest` to verify behavior.

### Acceptance Criteria

- [x] **AC 1:** On first run, `tasks.json` is created with content `[]`.
- [x] **AC 2:** `load_tasks()` returns a list of dicts if data exists.
- [x] **AC 3:** `save_tasks()` writes valid JSON to disk.
- [x] **AC 4:** `save_tasks()` persists exact data passed to it.

## Additional Context

### Dependencies
- `json` (Standard Lib)
- `os` (Standard Lib)

### Testing Strategy
- **Unit Tests:** `test_storage.py`
    - Test `load_tasks` when file is missing (should create it).
    - Test `save_tasks` then `load_tasks` (round trip).
    - Test handling of corrupt JSON (optional but recommended).

### Notes
- Keep it simple. No classes needed for the storage module yet, functions are sufficient for this scale, but a `Storage` class is also fine if preferred for namespacing. Let's stick to functions for "Simple ToDo".
