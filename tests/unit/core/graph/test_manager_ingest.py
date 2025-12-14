import pytest
from unittest.mock import AsyncMock, MagicMock, call
from coretext.core.graph.manager import GraphManager, SyncReport
from coretext.core.graph.models import BaseNode, BaseEdge, ParsingErrorNode
from coretext.core.parser.schema import SchemaMapper

@pytest.fixture
def mock_surreal_client():
    return AsyncMock()

@pytest.fixture
def mock_schema_mapper():
    mapper = MagicMock(spec=SchemaMapper)
    mapper.get_node_table.return_value = "node"
    mapper.get_edge_table.side_effect = lambda x: x
    return mapper

@pytest.fixture
def graph_manager(mock_surreal_client, mock_schema_mapper):
    return GraphManager(mock_surreal_client, mock_schema_mapper)

@pytest.mark.asyncio
async def test_ingest_success(graph_manager, mock_surreal_client):
    nodes = [BaseNode(id="n1", node_type="file", content="c1"), BaseNode(id="n2", node_type="file", content="c2")]
    edges = [BaseEdge(id="e1", edge_type="contains", source="n1", target="n2")]
    
    mock_surreal_client.query.return_value = None # query doesn't need to return anything for this test

    report = await graph_manager.ingest(nodes, edges, batch_size=2)

    assert report.success is True
    assert report.nodes_created == 2
    assert report.edges_created == 1
    assert mock_surreal_client.query.call_count == 2 # 1 for nodes, 1 for edges

@pytest.mark.asyncio
async def test_ingest_parsing_error(graph_manager):
    nodes = [BaseNode(id="n1", node_type="file", content="c1"), ParsingErrorNode(id="err", node_type="parsing_error", error_message="fail", file_path="test.md", line_number=1, raw_content_snippet="bad")]
    edges = []

    report = await graph_manager.ingest(nodes, edges)

    assert report.success is False
    assert len(report.parsing_errors) == 1
    assert report.parsing_errors[0].id == "err"

@pytest.mark.asyncio
async def test_ingest_transaction_batches(graph_manager, mock_surreal_client):
    nodes = [BaseNode(id=f"n{i}", node_type="file", content=f"c{i}") for i in range(5)]
    edges = []

    await graph_manager.ingest(nodes, edges, batch_size=2)
    
    # Should result in 3 batches: [2, 2, 1]
    assert mock_surreal_client.query.call_count == 3
