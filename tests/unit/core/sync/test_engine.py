import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path
from coretext.core.sync.engine import SyncEngine, SyncMode, SyncResult
from coretext.core.graph.models import BaseNode, BaseEdge, ParsingErrorNode

@pytest.fixture
def mock_parser(tmp_path: Path):
    parser = MagicMock()
    parser.parse.return_value = ([], []) # Default empty nodes/edges
    return parser

@pytest.fixture
def mock_graph_manager():
    manager = AsyncMock()
    mock_report = MagicMock()
    mock_report.success = True
    manager.ingest.return_value = mock_report
    return manager

@pytest.mark.asyncio
async def test_sync_engine_initialization(mock_parser, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser, graph_manager=mock_graph_manager, project_root=tmp_path)
    assert engine.parser == mock_parser
    assert engine.graph_manager == mock_graph_manager
    assert engine.project_root == tmp_path

@pytest.mark.asyncio
async def test_sync_engine_dry_run_mode(mock_parser, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser, graph_manager=mock_graph_manager, project_root=tmp_path)
    
    files = ["test.md"]
    mock_node = MagicMock(spec=BaseNode)
    mock_parser.parse.return_value = ([mock_node], [])
    
    result = await engine.process_files(files, mode=SyncMode.DRY_RUN)
    
    assert isinstance(result, SyncResult)
    assert result.success is True
    assert result.processed_count == 1
    
    mock_parser.parse.assert_called_once()
    mock_graph_manager.ingest.assert_not_called()

@pytest.mark.asyncio
async def test_sync_engine_write_mode(mock_parser, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser, graph_manager=mock_graph_manager, project_root=tmp_path)
    
    files = ["test.md"]
    mock_node = MagicMock(spec=BaseNode)
    mock_parser.parse.return_value = ([mock_node], [])
    
    result = await engine.process_files(files, mode=SyncMode.WRITE)
    
    assert result.success is True
    assert result.processed_count == 1
    
    mock_parser.parse.assert_called_once()
    mock_graph_manager.ingest.assert_called_once()

@pytest.mark.asyncio
async def test_sync_engine_parsing_error_dry_run(mock_parser, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser, graph_manager=mock_graph_manager, project_root=tmp_path)
    
    files = ["bad.md"]
    # Mock parser to return a ParsingErrorNode
    mock_error_node = MagicMock(spec=ParsingErrorNode)
    mock_error_node.error_message = "Malformed content"
    mock_parser.parse.return_value = ([mock_error_node], [])
    
    result = await engine.process_files(files, mode=SyncMode.DRY_RUN)
    
    assert result.success is False
    assert result.error_count == 1
    assert "Malformed content" in result.errors[0]
    mock_graph_manager.ingest.assert_not_called()

@pytest.mark.asyncio
async def test_sync_engine_commit_hash_propagation(mock_parser, mock_graph_manager, tmp_path: Path):
    engine = SyncEngine(parser=mock_parser, graph_manager=mock_graph_manager, project_root=tmp_path)

    files = ["test.md"]
    test_commit_hash = "abcdef12345"

    mock_node = MagicMock(spec=BaseNode)
    mock_edge = MagicMock(spec=BaseEdge)
    mock_parser.parse.return_value = ([mock_node], [mock_edge])

    result = await engine.process_files(files, mode=SyncMode.WRITE, commit_hash=test_commit_hash)

    assert result.success is True
    assert mock_node.commit_hash == test_commit_hash
    assert mock_edge.commit_hash == test_commit_hash
    mock_graph_manager.ingest.assert_called_once()
