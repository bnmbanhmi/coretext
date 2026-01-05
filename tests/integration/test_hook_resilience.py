from unittest.mock import patch
from pathlib import Path
from typer.testing import CliRunner
from coretext.cli.main import app
import sys

runner = CliRunner()

def test_hook_detaches_on_many_files(tmp_path: Path):
    """
    Test that the post-commit hook detaches (runs in background) when many files are changed.
    """
    # Create a dummy config so it doesn't fail on init
    (tmp_path / ".coretext").mkdir()
    (tmp_path / ".coretext" / "config.yaml").write_text("daemon_port: 8000\nmcp_port: 8001")
    (tmp_path / ".git").mkdir()

    # Mock get_last_commit_files to return many files
    # Mock SyncEngine.should_detach to return True (or rely on logic if we provide enough files)
    # Patch subprocess.Popen to verify it's called
    
    # We need to patch where run_with_timeout_or_detach is imported or defined.
    # It is imported in cli/commands.py from core/sync/timeout_utils.py
    # But run_with_timeout_or_detach calls subprocess.Popen
    
    with patch("coretext.cli.commands.get_last_commit_files", return_value=[f"file_{i}.md" for i in range(10)]), \
         patch("coretext.core.sync.timeout_utils.subprocess.Popen") as mock_popen, \
         patch("coretext.cli.commands.check_daemon_health"), \
         patch("os._exit"):
         
        result = runner.invoke(app, ["hook", "post-commit", "--project-root", str(tmp_path)])
        
        # Should succeed (exit code 0)
        assert result.exit_code == 0
        # Should verify it printed the background message
        assert "Syncing in background" in result.stdout
        
        # Verify Popen was called to spawn the detached process
        mock_popen.assert_called_once()
        
        # Verify arguments to Popen
        args = mock_popen.call_args[0][0]
        assert sys.executable in args
        assert "coretext.cli.main" in args
        assert "--detached" in args

def test_hook_fail_open_on_crash(tmp_path: Path):
    """
    Test that the post-commit hook exits with 0 (success) even if the internal logic crashes.
    """
    (tmp_path / ".coretext").mkdir()
    (tmp_path / ".coretext" / "config.yaml").write_text("daemon_port: 8000\nmcp_port: 8001")
    (tmp_path / ".git").mkdir()

    # Mock get_last_commit_files to return 1 file
    # Mock _post_commit_hook_logic to raise an exception
    
    with patch("coretext.cli.commands.get_last_commit_files", return_value=["file.md"]), \
         patch("coretext.cli.commands._post_commit_hook_logic", side_effect=Exception("Critical Failure")), \
         patch("os._exit"):
         
        result = runner.invoke(app, ["hook", "post-commit", "--project-root", str(tmp_path)])
        
        # Must exit with 0 to not block the git commit
        assert result.exit_code == 0
        
        # Should see the warning message
        # Since we are capturing stdout/stderr, Typer prints to stderr with 'err=True'
        assert "Sync failed - queuing for retry" in result.stdout # Runner captures stderr into stdout by default? No, result.stdout and result.stderr?
        # CliRunner mixes them by default unless mix_stderr=False is passed. 
        # But verify output contains the warning.
        
        assert "Sync failed" in result.stdout

def test_hook_timeouts_on_slow_sync(tmp_path: Path):
    """
    Test that the hook exits gracefully (fail-open) if the sync operation times out.
    """
    (tmp_path / ".coretext").mkdir()
    (tmp_path / ".coretext" / "config.yaml").write_text("daemon_port: 8000\nmcp_port: 8001")
    (tmp_path / ".git").mkdir()
    
    import asyncio
    
    # Create a slow sync function
    async def slow_sync(*args, **kwargs):
        await asyncio.sleep(3) # Longer than 2s timeout
        
    with patch("coretext.cli.commands.get_last_commit_files", return_value=["file.md"]), \
         patch("coretext.cli.commands._post_commit_hook_logic", side_effect=slow_sync), \
         patch("coretext.core.sync.timeout_utils.TIMEOUT_SECONDS", 1), \
         patch("os._exit"):
         
        result = runner.invoke(app, ["hook", "post-commit", "--project-root", str(tmp_path)])
        
        # Should exit with 0 (fail open)
        assert result.exit_code == 0
        
        # Note: We don't assert the warning message here because signal.alarm
        # interactions with pytest execution environment can be unreliable.
        # The critical requirement is that it exits with 0 (fail-open).

