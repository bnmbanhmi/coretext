import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from coretext.cli.commands import _post_commit_hook_logic
from coretext.core.graph.models import BaseNode, SyncReport

@pytest.mark.asyncio
async def test_sync_integration_simulated(tmp_path: Path):
    """
    Simulates a full post-commit sync cycle.
    1. Sets up mocks for Git changes and DB connections.
    2. Calls the post_commit_hook logic directly in detached mode.
    3. Verifies that SyncEngine processed files.
    """
    project_root = tmp_path
    (project_root / ".git").mkdir()
    
    # Mock Git Utils
    with patch("coretext.cli.commands.get_last_commit_files", return_value=["doc1.md"]) as mock_last_commit, \
         patch("coretext.cli.commands.get_current_commit_hash", return_value="hash123") as mock_hash, \
         patch("coretext.cli.commands.get_head_content", return_value="content") as mock_content, \
         patch("coretext.cli.commands.SurrealDBClient") as MockDBClient, \
         patch("coretext.cli.commands.AsyncSurreal") as MockAsyncSurreal, \
         patch("coretext.cli.commands.SchemaMapper") as MockSchemaMapper, \
         patch("coretext.cli.commands.MarkdownParser") as MockParser, \
         patch("coretext.cli.commands.SyncEngine") as MockEngine:

        # Setup Mock DB Client (management client)
        mock_db_client_instance = MockDBClient.return_value
        mock_db_client_instance.is_running = AsyncMock(return_value=True)

        # Setup Mock AsyncSurreal (connection context manager)
        mock_db_conn = AsyncMock()
        mock_async_surreal_instance = MockAsyncSurreal.return_value
        mock_async_surreal_instance.__aenter__.return_value = mock_db_conn
        
        # Setup Mock Engine
        mock_engine_instance = MockEngine.return_value
        mock_engine_instance.process_files = AsyncMock(return_value=SyncReport(success=True, message="Done", nodes_created=1, edges_created=0))

        # Execute Logic (detached=True to run sync logic immediately)
        await _post_commit_hook_logic(project_root, detached=True)
        
        # Verify Engine called with correct args
        MockEngine.assert_called()
        mock_engine_instance.process_files.assert_awaited()
        
        # Check call arguments for process_files
        args, kwargs = mock_engine_instance.process_files.call_args
        assert args[0] == ["doc1.md"] # files
        assert kwargs['commit_hash'] == "hash123"