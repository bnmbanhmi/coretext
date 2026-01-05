import pytest
from typer.testing import CliRunner
from pathlib import Path
from coretext.cli.commands import install_hooks, pre_commit_hook, _post_commit_hook_logic
import stat
from unittest.mock import patch, MagicMock, AsyncMock, ANY
import typer
import asyncio
from coretext.core.sync.engine import SyncMode

runner = CliRunner()

@patch("coretext.cli.commands.typer.echo")
@patch("coretext.cli.commands.typer.Exit")
def test_install_hooks_success(mock_exit, mock_echo, tmp_path: Path):
    # Setup .git directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    
    # Directly call the function
    install_hooks(project_root=tmp_path)

    mock_echo.assert_any_call(f"Installed pre-commit hook to {tmp_path / '.git' / 'hooks' / 'pre-commit'}")
    mock_echo.assert_any_call(f"Installed post-commit hook to {tmp_path / '.git' / 'hooks' / 'post-commit'}")
    mock_exit.assert_not_called()
    
    hooks_dir = git_dir / "hooks"
    pre_commit = hooks_dir / "pre-commit"
    post_commit = hooks_dir / "post-commit"
    
    assert pre_commit.exists()
    assert post_commit.exists()
    
    # Check executable permissions
    assert pre_commit.stat().st_mode & stat.S_IEXEC
    assert post_commit.stat().st_mode & stat.S_IEXEC
    
    assert "coretext.cli.main hook pre-commit" in pre_commit.read_text()
    post_commit_content = post_commit.read_text()
    assert "coretext.cli.main hook post-commit" in post_commit_content
    # Ensure it is NOT backgrounded in shell (no trailing &)
    assert "&" not in post_commit_content.strip().splitlines()[-1]

@patch("coretext.cli.commands.typer.echo")
def test_install_hooks_no_git(mock_echo, tmp_path: Path):
    # Directly call the function, expecting it to raise Typer.Exit
    with pytest.raises(typer.Exit) as excinfo:
        install_hooks(project_root=tmp_path)
    
    assert excinfo.value.exit_code == 1
    mock_echo.assert_any_call("Error: .git directory not found. Is this a git repository?", err=True)

@patch("coretext.cli.commands.SyncEngine")
@patch("coretext.cli.commands.get_staged_files")
@patch("coretext.cli.commands.typer.echo")
def test_pre_commit_hook_success(mock_echo, mock_get_files, mock_engine_cls, tmp_path: Path):
    # Configure the mocked get_staged_files
    mock_get_files.return_value = ["test.md", "other.md"] 

    mock_engine = mock_engine_cls.return_value
    mock_sync_result = MagicMock()
    mock_sync_result.success = True
    mock_engine.process_files = AsyncMock(return_value=mock_sync_result)
    
    pre_commit_hook(project_root=tmp_path) 
    
    mock_get_files.assert_called_once_with(tmp_path) 
    mock_engine_cls.assert_called_once()
    mock_engine.process_files.assert_awaited_once_with(
        ["test.md", "other.md"],
        mode=SyncMode.DRY_RUN, 
        content_provider=ANY
    )
    mock_echo.assert_any_call("Checking 2 staged Markdown files...")
    mock_echo.assert_any_call("✅ CoreText Pre-commit Check PASSED.")

@patch("coretext.cli.commands.SyncEngine")
@patch("coretext.cli.commands.get_staged_files")
@patch("coretext.cli.commands.typer.echo")
def test_pre_commit_hook_fail(mock_echo, mock_get_files, mock_engine_cls, tmp_path: Path):
    # Configure the mocked get_staged_files
    mock_get_files.return_value = ["bad.md"] 

    mock_engine = mock_engine_cls.return_value
    mock_sync_result = MagicMock()
    mock_sync_result.success = False
    mock_sync_result.errors = ["Parsing error in bad.md"]
    mock_engine.process_files = AsyncMock(return_value=mock_sync_result)
    
    with pytest.raises(typer.Exit) as excinfo:
        pre_commit_hook(project_root=tmp_path)
    
    assert excinfo.value.exit_code == 1
    mock_get_files.assert_called_once_with(tmp_path) 
    mock_engine_cls.assert_called_once()
    mock_engine.process_files.assert_awaited_once_with(
        ["bad.md"],
        mode=SyncMode.DRY_RUN, 
        content_provider=ANY
    )
    mock_echo.assert_any_call("Checking 1 staged Markdown files...")
    mock_echo.assert_any_call("❌ CoreText Pre-commit Check FAILED:", err=True)
    mock_echo.assert_any_call("  - Parsing error in bad.md", err=True)

@pytest.mark.asyncio
@patch("coretext.cli.commands.typer.echo")
@patch("coretext.cli.commands.get_last_commit_files")
@patch("coretext.cli.commands.get_head_content")
@patch("coretext.cli.commands.SyncEngine")
@patch("coretext.cli.commands.MarkdownParser")
@patch("coretext.cli.commands.GraphManager")
@patch("coretext.cli.commands.SchemaMapper") # Added SchemaMapper patch
@patch("coretext.cli.commands.SurrealDBClient")
@patch("coretext.cli.commands.AsyncSurreal", new_callable=MagicMock)
async def test_post_commit_hook_detached_success(
    mock_surreal_cls, mock_db_client_cls, mock_schema_mapper_cls, mock_graph_manager_cls, mock_parser_cls, 
    mock_sync_engine_cls, mock_get_head_content, mock_get_last_commit_files, 
    mock_echo, tmp_path: Path
):
    # Mock SurrealDBClient
    mock_db_client_instance = mock_db_client_cls.return_value
    mock_db_client_instance.is_running = AsyncMock(return_value=False)
    mock_db_client_instance.start_surreal_db = AsyncMock()
    mock_db_client_instance.stop_surreal_db = AsyncMock()

    # Mock get_last_commit_files
    mock_get_last_commit_files.return_value = ["commit_file1.md"]
    mock_get_head_content.return_value = "# Committed File Content"

    # Mock Surreal context manager
    mock_surreal_cls_instance = AsyncMock()
    mock_surreal_cls.return_value = mock_surreal_cls_instance
    mock_surreal_instance = AsyncMock()
    mock_surreal_cls_instance.__aenter__.return_value = mock_surreal_instance
    mock_surreal_cls_instance.__aexit__.return_value = False

    # Mock GraphManager
    mock_graph_manager_instance = mock_graph_manager_cls.return_value

    # Mock MarkdownParser
    mock_parser_instance = mock_parser_cls.return_value

    # Mock SyncEngine
    mock_sync_engine_instance = mock_sync_engine_cls.return_value
    mock_sync_report = MagicMock()
    mock_sync_report.success = True
    mock_sync_engine_instance.process_files = AsyncMock(return_value=mock_sync_report)

    # Call _post_commit_hook_logic directly (bypassing asyncio.run)
    await _post_commit_hook_logic(project_root=tmp_path, detached=True)

    # Assertions
    mock_get_last_commit_files.assert_called_once_with(tmp_path)
    mock_db_client_cls.assert_called_once_with(project_root=tmp_path)
    mock_db_client_instance.is_running.assert_awaited_once()
    mock_db_client_instance.start_surreal_db.assert_awaited_once()
    mock_surreal_cls.assert_called_once_with("ws://localhost:8000/rpc")
    mock_surreal_instance.use.assert_awaited_once_with("coretext", "coretext")
    
    mock_schema_mapper_cls.assert_called_once()
    mock_graph_manager_cls.assert_called_once_with(mock_surreal_instance, mock_schema_mapper_cls.return_value)
    
    mock_parser_cls.assert_called_once()
    mock_sync_engine_cls.assert_called_once_with(parser=mock_parser_instance, graph_manager=mock_graph_manager_instance, project_root=tmp_path)
    mock_sync_engine_instance.process_files.assert_awaited_once_with(
        mock_get_last_commit_files.return_value,
        mode=SyncMode.WRITE,
        content_provider=ANY,
        commit_hash=ANY
    )
    mock_echo.assert_any_call("Running CoreText post-commit hook (detached process)...")
    mock_echo.assert_any_call("Synchronizing 1 Markdown files from last commit...")
    mock_echo.assert_any_call("SurrealDB is not running, attempting to start for synchronization.", err=True)
    mock_echo.assert_any_call("✅ CoreText Post-commit Synchronization COMPLETE.")
    mock_db_client_instance.stop_surreal_db.assert_awaited_once()

@pytest.mark.asyncio
@patch("coretext.cli.commands.typer.echo")
@patch("coretext.cli.commands.get_last_commit_files")
@patch("coretext.cli.commands.get_head_content")
@patch("coretext.cli.commands.SyncEngine")
@patch("coretext.cli.commands.MarkdownParser")
@patch("coretext.cli.commands.GraphManager")
@patch("coretext.cli.commands.SchemaMapper") # Added SchemaMapper patch
@patch("coretext.cli.commands.SurrealDBClient")
@patch("coretext.cli.commands.AsyncSurreal", new_callable=MagicMock)
async def test_post_commit_hook_detached_fail(
    mock_surreal_cls, mock_db_client_cls, mock_schema_mapper_cls, mock_graph_manager_cls, mock_parser_cls, 
    mock_sync_engine_cls, mock_get_head_content, mock_get_last_commit_files, 
    mock_echo, tmp_path: Path
):
    # Mock SurrealDBClient
    mock_db_client_instance = mock_db_client_cls.return_value
    mock_db_client_instance.is_running = AsyncMock(return_value=True)
    mock_db_client_instance.stop_surreal_db = AsyncMock()

    # Mock get_last_commit_files
    mock_get_last_commit_files.return_value = ["commit_file1.md"]
    mock_get_head_content.return_value = "# Committed File Content"

    # Mock Surreal context manager
    mock_surreal_cls_instance = AsyncMock()
    mock_surreal_cls.return_value = mock_surreal_cls_instance
    mock_surreal_instance = AsyncMock()
    mock_surreal_cls_instance.__aenter__.return_value = mock_surreal_instance

    # Mock GraphManager
    mock_graph_manager_instance = mock_graph_manager_cls.return_value

    # Mock MarkdownParser
    mock_parser_instance = mock_parser_cls.return_value

    # Mock SyncEngine to fail
    mock_sync_engine_instance = mock_sync_engine_cls.return_value
    mock_sync_report = MagicMock()
    mock_sync_report.success = False
    mock_sync_report.message = "Ingestion failed"
    mock_sync_report.errors = ["Error 1", "Error 2"]
    mock_sync_engine_instance.process_files = AsyncMock(return_value=mock_sync_report)

    # Call _post_commit_hook_logic directly
    with pytest.raises(typer.Exit) as excinfo:
        await _post_commit_hook_logic(project_root=tmp_path, detached=True)
    
    assert excinfo.value.exit_code == 0 # Fail-open

    # Assertions for fail-open
    mock_get_last_commit_files.assert_called_once_with(tmp_path)
    mock_sync_engine_instance.process_files.assert_awaited_once()
    mock_echo.assert_any_call("⚠️ CoreText Post-commit Synchronization FAILED:", err=True)
    mock_echo.assert_any_call("  - Error 1", err=True)
    mock_echo.assert_any_call("  - Error 2", err=True)
    mock_db_client_instance.stop_surreal_db.assert_not_awaited()

@pytest.mark.asyncio
@patch("coretext.cli.commands.run_with_timeout_or_detach") 
@patch("coretext.cli.commands.typer.echo")
@patch("coretext.cli.commands.get_last_commit_files")
async def test_post_commit_hook_non_detached_calls_timeout_utils(
    mock_get_last_commit_files, mock_echo, mock_run_with_timeout_or_detach, tmp_path: Path
):
    mock_get_last_commit_files.return_value = ["file1.md", "file2.md"]
    # Call _post_commit_hook_logic directly
    await _post_commit_hook_logic(project_root=tmp_path, detached=False)
    
    mock_echo.assert_any_call("Running CoreText post-commit hook...")
    mock_echo.assert_any_call("Synchronizing 2 Markdown files from last commit...")
    mock_run_with_timeout_or_detach.assert_called_once()
    args, kwargs = mock_run_with_timeout_or_detach.call_args
    assert args[0] == tmp_path
    assert args[1] == ["file1.md", "file2.md"]
    assert callable(args[2])
    assert asyncio.iscoroutinefunction(args[2])

@pytest.mark.asyncio
@patch("coretext.cli.commands.typer.echo")
@patch("coretext.cli.commands.get_last_commit_files", return_value=[])
async def test_post_commit_hook_no_files_detached(
    mock_get_last_commit_files, mock_echo, tmp_path: Path
):
    # Call _post_commit_hook_logic directly
    with pytest.raises(typer.Exit) as excinfo:
        await _post_commit_hook_logic(project_root=tmp_path, detached=True)
    
    mock_echo.assert_any_call("Running CoreText post-commit hook (detached process)...")
    mock_echo.assert_any_call("No Markdown files changed in last commit to synchronize.")
    assert excinfo.value.exit_code == 0

@pytest.mark.asyncio
@patch("coretext.cli.commands.typer.echo")
@patch("coretext.cli.commands.get_last_commit_files", side_effect=Exception("Git error"))
async def test_post_commit_hook_git_error_non_detached(
    mock_get_last_commit_files, mock_echo, tmp_path: Path
):
    # Call _post_commit_hook_logic directly
    await _post_commit_hook_logic(project_root=tmp_path, detached=False)
    mock_echo.assert_any_call("Running CoreText post-commit hook...")
    mock_echo.assert_any_call("Warning: Could not detect last commit files: Git error", err=True)
    mock_get_last_commit_files.assert_called_once_with(tmp_path)

@pytest.mark.asyncio
@patch("coretext.cli.commands.typer.echo")
@patch("coretext.cli.commands.get_last_commit_files", side_effect=Exception("Git error"))
async def test_post_commit_hook_git_error_detached(
    mock_get_last_commit_files, mock_echo, tmp_path: Path
):
    # Call _post_commit_hook_logic directly
    with pytest.raises(typer.Exit) as excinfo:
        await _post_commit_hook_logic(project_root=tmp_path, detached=True)
    
    mock_echo.assert_any_call("Running CoreText post-commit hook (detached process)...")
    mock_echo.assert_any_call("Warning: Could not detect last commit files: Git error", err=True)
    assert excinfo.value.exit_code == 0
