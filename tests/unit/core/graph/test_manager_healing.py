import pytest
from unittest.mock import AsyncMock, MagicMock
from coretext.core.graph.manager import GraphManager
from coretext.core.parser.schema import SchemaMapper

@pytest.mark.asyncio
async def test_prune_dangling_edges_logic():
    mock_db = AsyncMock()
    mock_mapper = MagicMock()
    manager = GraphManager(mock_db, mock_mapper)
    
    # Mock Schema: Need to provide at least one edge type so it generates a query
    edge_def = MagicMock()
    edge_def.db_table = "contains"
    mock_mapper.schema_map.edge_types.values.return_value = [edge_def]

    # Mock return value for delete query
    # Standard SurrealDB query response is a list of result objects (dicts)
    mock_db.query.return_value = [
        {"status": "OK", "result": [{"id": "contains:1"}, {"id": "contains:2"}]}
    ]

    deleted_count = await manager.prune_dangling_edges()

    assert deleted_count == 2
    
    # Verify the query
    calls = mock_db.query.call_args_list
    assert len(calls) > 0
    query_str = calls[0][0][0]
    # We expect a DELETE command on edges
    assert "DELETE" in query_str.upper()
    assert "contains" in query_str.lower()
    # Check for the condition
    assert "out.id IS NONE" in query_str
    assert "in.id IS NONE" in query_str

@pytest.mark.asyncio
async def test_prune_orphan_headers_logic():
    mock_db = AsyncMock()
    mock_mapper = MagicMock()
    manager = GraphManager(mock_db, mock_mapper)

    # Mock DB response
    mock_db.query.return_value = [
        {"status": "OK", "result": [{"id": "header:1"}]}
    ]

    deleted_count = await manager.prune_orphan_headers()

    assert deleted_count == 1
    
    calls = mock_db.query.call_args_list
    assert len(calls) > 0
    query_str = calls[0][0][0]
    assert "DELETE" in query_str.upper()
    assert "node" in query_str.lower() # Default table for headers
    # Check for logic that checks for incoming 'contains' edges
    assert "contains" in query_str.lower()
