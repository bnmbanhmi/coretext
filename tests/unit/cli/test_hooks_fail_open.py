import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path
from coretext.cli.commands import app, post_commit_hook
import logging

runner = CliRunner()

@patch("coretext.cli.commands._post_commit_hook_logic")
@patch("coretext.cli.commands.typer.echo")
def test_post_commit_hook_fail_open(mock_echo, mock_logic, tmp_path: Path):
    # Simulate a crash in the logic
    mock_logic.side_effect = Exception("Catastrophic failure")

    # We need to invoke post_commit_hook directly or via runner?
    # Direct invocation is easier to test implementation details if not using typer app structure for unit test
    # But post_commit_hook is a typer command function.
    
    # Let's call it directly. It returns None (implicitly) or raises Exit.
    # If fail-open, it should catch Exception and exit 0 (which might be just returning or raising Exit(0))
    
    # We need to mock os.environ to avoid Side effects
    with patch.dict("os.environ", {"TOKENIZERS_PARALLELISM": "true"}):
         # If we use direct call:
         try:
             post_commit_hook(project_root=tmp_path, detached=False)
         except Exception as e:
             # Should be typer.Exit(0) or just return
             if hasattr(e, "exit_code"):
                 assert e.exit_code == 0
             else:
                 # If it didn't raise Exit, it returned normally, which is also exit 0
                 pass
    
    # Verify warning
    # Note: The implementation might use console.print or typer.echo
    # usage of "Sync failed" in output
    args_list = mock_echo.call_args_list
    found_warning = False
    for args, _ in args_list:
        if "Coretext Warning" in str(args[0]) and "Sync failed" in str(args[0]):
             found_warning = True
             break
    
    assert found_warning, "Did not find expected warning message in output"
    
    # Verify log file
    log_file = tmp_path / ".coretext" / "coretext.log"
    # The implementation should write to this file.
    # We assert it exists and contains the error
    assert log_file.exists()
    content = log_file.read_text()
    assert "Catastrophic failure" in content

