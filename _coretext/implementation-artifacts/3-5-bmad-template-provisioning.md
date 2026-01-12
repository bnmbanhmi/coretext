# Story 3.5: BMAD Template Provisioning

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to easily generate structured BMAD Markdown files using predefined templates via the CLI,
so that I can quickly create new project documentation that is compliant with the knowledge graph schema.

## Acceptance Criteria

1.  **New Command (`coretext new`)**:
    *   [x] Command is available via `coretext new <template_name> <output_path>`.
    *   [x] Example usage: `coretext new prd docs/new-prd.md`.

2.  **Template Generation**:
    *   [x] Creates a new Markdown file at the specified `output_path`.
    *   [x] Populates the file with the content of the selected BMAD template.
    *   [x] Ensures the output directory exists (creates if missing).
    *   [x] Prevents accidental overwrite of existing files (prompts user or requires `--force` flag).

3.  **Template Inventory**:
    *   [x] Supports the following standard templates:
        *   `prd` (Product Requirements Document)
        *   `architecture` (Architecture Decision Record)
        *   `epic` (Epic Breakdown)
        *   `story` (User Story)
    *   [x] Templates are stored within the `coretext` package distribution.

4.  **List Templates**:
    *   [x] If no `template_name` is provided (or user runs `coretext new --list`), lists all available templates.

5.  **Output Feedback**:
    *   [x] Displays a success message with the full path of the created file.
    *   [x] Uses `Rich` for consistent CLI styling.

## Tasks / Subtasks

- [x] **Task 1: Create Template Resources**
    - [x] Create `coretext/templates/` package directory.
    - [x] Add `__init__.py`.
    - [x] Add `prd.md`, `architecture.md`, `epic.md`, `story.md` with standard BMAD content (copied from `_bmad` standards or simplified versions).

- [x] **Task 2: Implement `TemplateManager`**
    - [x] Create `coretext/core/templates/manager.py`.
    - [x] Implement `list_templates()` -> `List[str]`.
    - [x] Implement `get_template_content(name: str)` -> `str`.
    - [x] Use `importlib.resources.files("coretext.templates")` to access files (Python 3.10+ standard).

- [x] **Task 3: Implement `new` Command**
    - [x] Add `new` command to `coretext/cli/commands.py`.
    - [x] Arguments: `template_name` (optional/argument), `output_path` (optional/argument).
    - [x] Logic:
        - If args missing, show list of templates.
        - Check if output file exists.
        - Write content.
    - [x] Add `--force` option to overwrite.

- [x] **Task 4: Testing**
    - [x] Unit tests for `TemplateManager` (mocking `importlib.resources` or checking actual bundled files).
    - [x] Integration test: Run `coretext new story tmp/test.md` and verify file content.

## Dev Notes

### Architecture & Compliance
*   **Package Resources**: Use `importlib.resources` (standard in Python 3.10+) to access templates. Do NOT use `pkg_resources` (deprecated) or `__file__` relative paths (unreliable in zipped installs).
*   **Pattern**: `importlib.resources.files("coretext.templates").joinpath(f"{name}.md").read_text()`.

### Project Structure Notes
*   **Templates**: `coretext/templates/` (New directory).
*   **Manager**: `coretext/core/templates/` (New module).

### Previous Story Intelligence (from Story 3.4)
*   **Path Handling**: Ensure `output_path` is resolved correctly relative to current working directory.
*   **CLI Consistency**: Use the same `Rich` console object and error handling patterns established in `coretext lint`.

### References
*   [Python importlib.resources documentation](https://docs.python.org/3/library/importlib.resources.html)

## Dev Agent Record

### Agent Model Used

Gemini Pro 1.5

### Debug Log References

### Completion Notes List
*   Implemented `TemplateManager` using `importlib.resources`.
*   Added `coretext new` command with support for `prd`, `architecture`, `epic`, `story` templates.
*   Implemented unit tests for `TemplateManager` and integration tests for CLI command.
*   Added overwrite protection and `--force` flag.
*   Used Rich for output formatting.
*   **Code Review Fixes**:
    *   Refactored `TemplateManager.get_template_content` to remove redundant exception handling.
    *   Updated integration tests to verify all template types (`epic`, `architecture`) are listed.
    *   Documented previously untracked test file changes.
    *   **Senior Review Fixes (2026-01-04)**:
        *   Added strict input validation to `TemplateManager` to prevent path traversal/injection.
        *   Added interactive overwrite confirmation (`typer.confirm`) for better UX.
        *   Improved error handling for template loading (ImportError/ModuleNotFoundError).
        *   Added real template loading integration test and interactive CLI tests.

### File List
coretext/templates/__init__.py
coretext/templates/prd.md
coretext/templates/architecture.md
coretext/templates/epic.md
coretext/templates/story.md
coretext/core/templates/__init__.py
coretext/core/templates/manager.py
coretext/cli/commands.py
tests/unit/core/templates/test_template_manager.py
tests/integration/cli/test_new_command.py
tests/unit/core/parser/test_link_validation.py
tests/unit/core/parser/test_markdown.py

## Senior Developer Review (AI)

- [x] Story file loaded from `3-5-bmad-template-provisioning.md`
- [x] Story Status verified as reviewable (review)
- [x] Epic and Story IDs resolved (3.5)
- [x] Story Context located or warning recorded
- [x] Epic Tech Spec located or warning recorded
- [x] Architecture/standards docs loaded (as available)
- [x] Tech stack detected and documented
- [x] MCP doc search performed (or web fallback) and references captured
- [x] Acceptance Criteria cross-checked against implementation
- [x] File List reviewed and validated for completeness
- [x] Tests identified and mapped to ACs; gaps noted
- [x] Code quality review performed on changed files
- [x] Security review performed on changed files and dependencies
- [x] Outcome decided (Approve)
- [x] Review notes appended under "Senior Developer Review (AI)"
- [x] Change Log updated with review entry
- [x] Status updated according to settings (if enabled)
- [x] Sprint status synced (if sprint tracking enabled)
- [x] Story saved successfully

_Reviewer: Minh on 2026-01-04_

