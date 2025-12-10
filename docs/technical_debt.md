# Technical Debt Log

## Pending Issues

### Testing
*   **CLI `init` command integration tests**: The integration tests for `coretext init` (in `tests/unit/cli/test_commands.py`) fail with `exit_code=2` when run via `typer.testing.CliRunner`.
    *   **Cause**: Incompatibility between `CliRunner`, async commands, and `Path` options with default values in the version of Typer/Click being used.
    *   **Impact**: Tests cannot verify the success exit code (0) despite the command logic being functionally correct and verified via component mocks.
    *   **Status**: Recorded on 2025-12-07.
    *   **Action Required**: Investigate `CliRunner` alternatives for async Typer commands or refactor the command structure to be more test-friendly in future refactoring sprints.

### Architectural Trade-offs
*   **Simplified SurrealDB Management in Post-commit Hook**: The `post_commit_hook` attempts to start SurrealDB if not running. This is a simplified approach, acknowledging that a robust solution would involve a dedicated daemonized DB.
    *   **Cause**: Prioritization of MVP and quick integration.
    *   **Impact**: Potential for minor delays in commit process if DB needs to start; less robust error handling than a fully daemonized solution.
    *   **Status**: Recorded on 2025-12-10 (current date).
    *   **Action Required**: Consider implementing a dedicated daemon for SurrealDB management in a future architectural sprint.

