# Technical Debt Log

## Pending Issues

### Testing
*   **CLI `init` command integration tests**: The integration tests for `coretext init` (in `tests/unit/cli/test_commands.py`) fail with `exit_code=2` when run via `typer.testing.CliRunner`.
    *   **Cause**: Incompatibility between `CliRunner`, async commands, and `Path` options with default values in the version of Typer/Click being used.
    *   **Impact**: Tests cannot verify the success exit code (0) despite the command logic being functionally correct and verified via component mocks.
    *   **Status**: Recorded on 2025-12-07.
    *   **Action Required**: Investigate `CliRunner` alternatives for async Typer commands or refactor the command structure to be more test-friendly in future refactoring sprints.
