# Story 3.5: BMAD Template Provisioning

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to easily generate structured BMAD Markdown files using predefined templates via the CLI,
so that I can quickly create new project documentation that is compliant with the knowledge graph schema.

## Acceptance Criteria

1.  **New Command (`coretext new`)**:
    *   [ ] Command is available via `coretext new <template_name> <output_path>`.
    *   [ ] Example usage: `coretext new prd docs/new-prd.md`.

2.  **Template Generation**:
    *   [ ] Creates a new Markdown file at the specified `output_path`.
    *   [ ] Populates the file with the content of the selected BMAD template.
    *   [ ] Ensures the output directory exists (creates if missing).
    *   [ ] Prevents accidental overwrite of existing files (prompts user or requires `--force` flag).

3.  **Template Inventory**:
    *   [ ] Supports the following standard templates:
        *   `prd` (Product Requirements Document)
        *   `architecture` (Architecture Decision Record)
        *   `epic` (Epic Breakdown)
        *   `story` (User Story)
    *   [ ] Templates are stored within the `coretext` package distribution.

4.  **List Templates**:
    *   [ ] If no `template_name` is provided (or user runs `coretext new --list`), lists all available templates.

5.  **Output Feedback**:
    *   [ ] Displays a success message with the full path of the created file.
    *   [ ] Uses `Rich` for consistent CLI styling.

## Tasks / Subtasks

- [ ] **Task 1: Create Template Resources**
    - [ ] Create `coretext/templates/` package directory.
    - [ ] Add `__init__.py`.
    - [ ] Add `prd.md`, `architecture.md`, `epic.md`, `story.md` with standard BMAD content (copied from `_bmad` standards or simplified versions).

- [ ] **Task 2: Implement `TemplateManager`**
    - [ ] Create `coretext/core/templates/manager.py`.
    - [ ] Implement `list_templates()` -> `List[str]`.
    - [ ] Implement `get_template_content(name: str)` -> `str`.
    - [ ] Use `importlib.resources.files("coretext.templates")` to access files (Python 3.10+ standard).

- [ ] **Task 3: Implement `new` Command**
    - [ ] Add `new` command to `coretext/cli/commands.py`.
    - [ ] Arguments: `template_name` (optional/argument), `output_path` (optional/argument).
    - [ ] Logic:
        - If args missing, show list of templates.
        - Check if output file exists.
        - Write content.
    - [ ] Add `--force` option to overwrite.

- [ ] **Task 4: Testing**
    - [ ] Unit tests for `TemplateManager` (mocking `importlib.resources` or checking actual bundled files).
    - [ ] Integration test: Run `coretext new story tmp/test.md` and verify file content.

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

### File List
