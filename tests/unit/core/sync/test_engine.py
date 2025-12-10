import pytest
from unittest.mock import AsyncMock, MagicMock
from coretext.core.sync.engine import SyncEngine, SyncMode, SyncResult
from coretext.core.graph.models import BaseNode, BaseEdge # Added import

@pytest.mark.asyncio
async def test_sync_engine_initialization():
    parser = MagicMock()
    graph_manager = AsyncMock()
    engine = SyncEngine(parser=parser, graph_manager=graph_manager)
    assert engine.parser == parser
    assert engine.graph_manager == graph_manager

@pytest.mark.asyncio
async def test_sync_engine_dry_run_mode():
    parser = MagicMock()
    graph_manager = AsyncMock()
    engine = SyncEngine(parser=parser, graph_manager=graph_manager)
    
    files = ["test.md"]
    # Mock parser to return (nodes, edges)
    mock_node = MagicMock()
    parser.parse.return_value = ([mock_node], [])
    
    result = await engine.process_files(files, mode=SyncMode.DRY_RUN)
    
    assert isinstance(result, SyncResult)
    assert result.success is True
    assert result.processed_count == 1
    
    # Check parse call (not parse_file)
    # The engine converts string to Path, so we check if it was called
    assert parser.parse.called
    # In dry run, we should NOT call ingest_node
    graph_manager.ingest.assert_not_called()

@pytest.mark.asyncio
async def test_sync_engine_write_mode():
    parser = MagicMock()
    graph_manager = AsyncMock()
    engine = SyncEngine(parser=parser, graph_manager=graph_manager)
    
    files = ["test.md"]
    # Mock parser to return (nodes, edges)
    mock_node = MagicMock()
    parser.parse.return_value = ([mock_node], [])
    
    # Mock ingest to return success report
    mock_report = MagicMock()
    mock_report.success = True
    graph_manager.ingest.return_value = mock_report
    
    result = await engine.process_files(files, mode=SyncMode.WRITE)
    
    assert result.success is True
    assert result.processed_count == 1
    
    assert parser.parse.called
    # In write mode, we SHOULD call ingest
    graph_manager.ingest.assert_called_once()

@pytest.mark.asyncio
async def test_sync_engine_parsing_error_dry_run():
    parser = MagicMock()
    graph_manager = AsyncMock()
    engine = SyncEngine(parser=parser, graph_manager=graph_manager)
    
    files = ["bad.md"]
    # Mock parser to raise an exception
    parser.parse.side_effect = Exception("Parsing error")
    
    result = await engine.process_files(files, mode=SyncMode.DRY_RUN)
    
    assert result.success is False
    assert result.error_count == 1
    graph_manager.ingest.assert_not_called()

@pytest.mark.asyncio
async def test_sync_engine_commit_hash_propagation():
    parser = MagicMock()
    graph_manager = AsyncMock()
    engine = SyncEngine(parser=parser, graph_manager=graph_manager)

    files = ["test.md"]
    test_commit_hash = "abcdef12345"

    mock_node = MagicMock(spec=BaseNode)
    mock_edge = MagicMock(spec=BaseEdge)
    parser.parse.return_value = ([mock_node], [mock_edge])

    mock_report = MagicMock()
    mock_report.success = True
    graph_manager.ingest.return_value = mock_report

    result = await engine.process_files(files, mode=SyncMode.WRITE, commit_hash=test_commit_hash)

    assert result.success is True
    assert mock_node.commit_hash == test_commit_hash
    assert mock_edge.commit_hash == test_commit_hash
    graph_manager.ingest.assert_called_once()
