import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from coretext.core.sync.engine import SyncEngine, SyncMode, SyncResult
from coretext.core.graph.models import BaseNode, BaseEdge, ParsingErrorNode
import asyncio

@pytest.fixture
def mock_parser_instance():
    """Returns a MagicMock for MarkdownParser, which will be the instance used by SyncEngine."""
    parser = MagicMock()
    # Default return for the parse method, which is now called inside _parse_single_file
    parser.parse.return_value = ([], []) 
    return parser

@pytest.fixture
def mock_graph_manager():
    manager = AsyncMock()
    mock_report = MagicMock()
    mock_report.success = True
    manager.ingest.return_value = mock_report
    return manager

@pytest.mark.asyncio
async def test_sync_engine_initialization(mock_parser_instance, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser_instance, graph_manager=mock_graph_manager, project_root=tmp_path)
    assert engine.parser == mock_parser_instance
    assert engine.graph_manager == mock_graph_manager
    assert engine.project_root == tmp_path

@pytest.mark.asyncio
@patch("coretext.core.sync.engine.asyncio.to_thread")
async def test_sync_engine_dry_run_mode(mock_to_thread, mock_parser_instance, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser_instance, graph_manager=mock_graph_manager, project_root=tmp_path)
    
    files = ["test.md"]
    mock_node = MagicMock(spec=BaseNode)
    
    # Configure mock_to_thread for both content_provider and _parse_single_file
    # First call will be content_provider, second will be _parse_single_file
    mock_to_thread.side_effect = [
        "file content", # Content from content_provider
        ([mock_node], [], []) # Result from _parse_single_file: nodes, edges, file_errors
    ]

    result = await engine.process_files(files, mode=SyncMode.DRY_RUN, content_provider=lambda x: "mock content")
    
    assert isinstance(result, SyncResult)
    assert result.success is True
    assert result.processed_count == 1
    
    # Ensure asyncio.to_thread was called for content_provider and _parse_single_file
    assert mock_to_thread.call_count == 2
    mock_graph_manager.ingest.assert_not_called()

@pytest.mark.asyncio
@patch("coretext.core.sync.engine.asyncio.to_thread")
async def test_sync_engine_write_mode(mock_to_thread, mock_parser_instance, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser_instance, graph_manager=mock_graph_manager, project_root=tmp_path)
    
    files = ["test.md"]
    mock_node = MagicMock(spec=BaseNode)

    mock_to_thread.side_effect = [
        "file content", 
        ([mock_node], [], []) 
    ]
    
    result = await engine.process_files(files, mode=SyncMode.WRITE, content_provider=lambda x: "mock content")
    
    assert result.success is True
    assert result.processed_count == 1
    
    assert mock_to_thread.call_count == 2
    mock_graph_manager.ingest.assert_called_once()


@pytest.mark.asyncio
@patch("coretext.core.sync.engine.asyncio.to_thread")
async def test_sync_engine_parsing_error_dry_run(mock_to_thread, mock_parser_instance, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser_instance, graph_manager=mock_graph_manager, project_root=tmp_path)
    
    files = ["bad.md"]
    mock_error_node = MagicMock(spec=ParsingErrorNode)
    mock_error_node.error_message = "Malformed content"

    mock_to_thread.side_effect = [
        "file content",
        ([mock_error_node], [], ["File bad.md: Malformed content"]) # Simulate error from _parse_single_file
    ]
    
    result = await engine.process_files(files, mode=SyncMode.DRY_RUN, content_provider=lambda x: "mock content")
    
    assert result.success is False
    assert result.error_count == 1
    assert "Malformed content" in result.errors[0]
    assert mock_to_thread.call_count == 2
    mock_graph_manager.ingest.assert_not_called()

@pytest.mark.asyncio
@patch("coretext.core.sync.engine.asyncio.to_thread")
async def test_sync_engine_commit_hash_propagation(mock_to_thread, mock_parser_instance, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser_instance, graph_manager=mock_graph_manager, project_root=tmp_path)

    files = ["test.md"]
    test_commit_hash = "abcdef12345"

    mock_node = MagicMock(spec=BaseNode)
    mock_edge = MagicMock(spec=BaseEdge)
    
    mock_to_thread.side_effect = [
        "file content",
        ([mock_node], [mock_edge], []) 
    ]

    result = await engine.process_files(files, mode=SyncMode.WRITE, commit_hash=test_commit_hash, content_provider=lambda x: "mock content")

    assert result.success is True
    assert mock_node.commit_hash == test_commit_hash
    assert mock_edge.commit_hash == test_commit_hash
    assert mock_to_thread.call_count == 2
    mock_graph_manager.ingest.assert_called_once()

@pytest.mark.asyncio
@patch("coretext.core.sync.engine.asyncio.to_thread")
async def test_sync_engine_content_provider_error(mock_to_thread, mock_parser_instance, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser_instance, graph_manager=mock_graph_manager, project_root=tmp_path)
    
    files = ["error.md"]
    
    # Simulate content_provider raising an exception
    mock_to_thread.side_effect = [
        Exception("Failed to read content"), # First call for content_provider
    ]

    result = await engine.process_files(files, mode=SyncMode.DRY_RUN, content_provider=lambda x: "mock content")
    
    assert result.success is False
    assert result.processed_count == 1
    assert result.error_count == 1
    assert "Failed to read content" in result.errors[0]
    assert mock_to_thread.call_count == 1 # Only content_provider was called
    mock_parser_instance.parse.assert_not_called()
    mock_graph_manager.ingest.assert_not_called()

@pytest.mark.asyncio
@patch("coretext.core.sync.engine.asyncio.to_thread")
async def test_sync_engine_ingestion_error_write_mode(mock_to_thread, mock_parser_instance, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser_instance, graph_manager=mock_graph_manager, project_root=tmp_path)
    
    files = ["test.md"]
    mock_node = MagicMock(spec=BaseNode)

    mock_to_thread.side_effect = [
        "file content", 
        ([mock_node], [], []) 
    ]
    
    # Configure ingest to return a failed report
    mock_report = MagicMock()
    mock_report.success = False
    mock_report.message = "Ingestion failed"
    mock_report.parsing_errors = []
    mock_graph_manager.ingest.return_value = mock_report

    result = await engine.process_files(files, mode=SyncMode.WRITE, content_provider=lambda x: "mock content")
    
    assert result.success is False
    assert result.error_count == 1
    assert "Ingestion failed" in result.message
    mock_graph_manager.ingest.assert_called_once()
