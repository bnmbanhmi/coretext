import pytest
from unittest.mock import AsyncMock, MagicMock
from coretext.core.graph.manager import GraphManager
from coretext.core.graph.models import BaseNode, BaseEdge
from coretext.core.parser.schema import SchemaMapper
from datetime import datetime

@pytest.fixture
def mock_surreal_client():
    return AsyncMock()

@pytest.fixture
def mock_schema_mapper():
    mapper = MagicMock(spec=SchemaMapper)
    # Setup default return values for typical test cases
    mapper.get_node_table.return_value = "node"
    mapper.get_edge_table.side_effect = lambda x: x # Map edge type to itself (e.g. contains -> contains)
    return mapper

@pytest.fixture
def graph_manager(mock_surreal_client, mock_schema_mapper):
    return GraphManager(mock_surreal_client, mock_schema_mapper)

@pytest.mark.asyncio
async def test_create_node(graph_manager, mock_surreal_client):
    node_data = BaseNode(id="test_node_1", node_type="file", content="content", metadata={"author": "Minh"})
    
    # Mock the return value to include generated timestamps
    mock_return_value = node_data.model_dump(mode='json')
    mock_return_value["created_at"] = datetime.utcnow().isoformat()
    mock_return_value["updated_at"] = datetime.utcnow().isoformat()
    mock_surreal_client.create.return_value = mock_return_value

    created_node = await graph_manager.create_node(node_data)
    
    mock_surreal_client.create.assert_awaited_once() # Check that create was called
    call_args = mock_surreal_client.create.call_args.args
    # Expected: 'node:⟨test_node_1⟩' because get_node_table returns 'node'
    assert call_args[0] == f"node:⟨{node_data.id}⟩"
    
    # Check the data passed to create. It should be a dict representation of the model.
    # We can't directly compare datetime objects in mock args due to slight differences,
    # so we'll check the structure and key fields.
    sent_data = call_args[1]
    assert sent_data["id"] == node_data.id
    assert sent_data["node_type"] == node_data.node_type
    assert sent_data["content"] == node_data.content
    assert sent_data["metadata"] == node_data.metadata
    assert "created_at" in sent_data
    assert "updated_at" in sent_data

    assert isinstance(created_node, BaseNode)
    assert created_node.id == node_data.id
    assert created_node.created_at is not None
    assert created_node.updated_at is not None

@pytest.mark.asyncio
async def test_get_node(graph_manager, mock_surreal_client):
    node_id = "node:test_node_1" # SurrealDB ID format
    mock_surreal_client.select.return_value = {
        "id": node_id, 
        "node_type": "file", 
        "content": "content", 
        "metadata": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    retrieved_node = await graph_manager.get_node(node_id)

    mock_surreal_client.select.assert_awaited_once_with(node_id)
    assert isinstance(retrieved_node, BaseNode)
    assert retrieved_node.id == node_id

@pytest.mark.asyncio
async def test_get_node_not_found(graph_manager, mock_surreal_client):
    node_id = "node:non_existent_node"
    mock_surreal_client.select.return_value = None

    retrieved_node = await graph_manager.get_node(node_id)

    mock_surreal_client.select.assert_awaited_once_with(node_id)
    assert retrieved_node is None

@pytest.mark.asyncio
async def test_update_node(graph_manager, mock_surreal_client):
    node_data = BaseNode(id="test_node_1", node_type="file", content="updated content")
    
    # Mock the return value to include generated timestamps
    mock_return_value = node_data.model_dump(mode='json')
    mock_return_value["created_at"] = datetime.utcnow().isoformat()
    mock_return_value["updated_at"] = datetime.utcnow().isoformat()
    mock_surreal_client.update.return_value = mock_return_value

    updated_node = await graph_manager.update_node(node_data)

    mock_surreal_client.update.assert_awaited_once() # Check that update was called
    call_args = mock_surreal_client.update.call_args.args
    # Expected: 'node:⟨test_node_1⟩'
    assert call_args[0] == f"node:⟨{node_data.id}⟩"
    
    sent_data = call_args[1]
    assert sent_data["node_type"] == node_data.node_type
    assert sent_data["content"] == node_data.content
    assert sent_data["metadata"] == node_data.metadata
    assert "created_at" in sent_data
    assert "updated_at" in sent_data

    assert isinstance(updated_node, BaseNode)
    assert updated_node.content == "updated content"

@pytest.mark.asyncio
async def test_delete_node(graph_manager, mock_surreal_client):
    node_id = "node:test_node_1"

    await graph_manager.delete_node(node_id)

    mock_surreal_client.delete.assert_awaited_once_with(node_id)

@pytest.mark.asyncio
async def test_create_edge(graph_manager, mock_surreal_client):
    edge_data = BaseEdge(id="edge_1", edge_type="contains", source="node:node_a", target="node:node_b", metadata={"weight": 1.0})
    
    # Mock the return value to include generated timestamps and SurrealDB's 'in'/'out' format
    mock_return_value = edge_data.model_dump(mode='json')
    mock_return_value["created_at"] = datetime.utcnow().isoformat()
    mock_return_value["updated_at"] = datetime.utcnow().isoformat()
    mock_return_value["in"] = mock_return_value.pop("source")
    mock_return_value["out"] = mock_return_value.pop("target")

    mock_surreal_client.create.return_value = mock_return_value

    created_edge = await graph_manager.create_edge(edge_data)

    mock_surreal_client.create.assert_awaited_once() # Check that create was called
    call_args = mock_surreal_client.create.call_args.args
    assert call_args[0] == f"{edge_data.edge_type}:⟨{edge_data.id}⟩"

    sent_data = call_args[1]
    assert sent_data["in"] == edge_data.source
    assert sent_data["out"] == edge_data.target
    assert sent_data["edge_type"] == edge_data.edge_type
    assert sent_data["metadata"] == edge_data.metadata
    assert "created_at" in sent_data
    assert "updated_at" in sent_data

    assert isinstance(created_edge, BaseEdge)
    assert created_edge.id == edge_data.id
    assert created_edge.created_at is not None
    assert created_edge.updated_at is not None

@pytest.mark.asyncio
async def test_get_edge(graph_manager, mock_surreal_client):
    edge_id = "contains:edge_1"
    mock_surreal_client.select.return_value = {
        "id": edge_id, 
        "edge_type": "contains", 
        "in": "node:node_a", 
        "out": "node:node_b",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    retrieved_edge = await graph_manager.get_edge(edge_id)

    mock_surreal_client.select.assert_awaited_once_with(edge_id)
    assert isinstance(retrieved_edge, BaseEdge)
    assert retrieved_edge.id == edge_id

@pytest.mark.asyncio
async def test_get_edge_not_found(graph_manager, mock_surreal_client):
    edge_id = "contains:non_existent_edge"
    mock_surreal_client.select.return_value = None

    retrieved_edge = await graph_manager.get_edge(edge_id)

    mock_surreal_client.select.assert_awaited_once_with(edge_id)
    assert retrieved_edge is None

@pytest.mark.asyncio
async def test_update_edge(graph_manager, mock_surreal_client):
    edge_data = BaseEdge(id="edge_1", edge_type="contains", source="node:node_a", target="node:node_b", metadata={"weight": 2.0})
    
    # Mock the return value to include generated timestamps and SurrealDB's 'in'/'out' format
    mock_return_value = edge_data.model_dump(mode='json')
    mock_return_value["created_at"] = datetime.utcnow().isoformat()
    mock_return_value["updated_at"] = datetime.utcnow().isoformat()
    mock_return_value["in"] = mock_return_value.pop("source")
    mock_return_value["out"] = mock_return_value.pop("target")
    mock_surreal_client.update.return_value = mock_return_value

    updated_edge = await graph_manager.update_edge(edge_data)

    mock_surreal_client.update.assert_awaited_once() # Check that update was called
    call_args = mock_surreal_client.update.call_args.args
    assert call_args[0] == f"{edge_data.edge_type}:⟨{edge_data.id}⟩"
    
    sent_data = call_args[1]
    assert sent_data["in"] == edge_data.source
    assert sent_data["out"] == edge_data.target
    assert sent_data["edge_type"] == edge_data.edge_type
    assert sent_data["metadata"] == edge_data.metadata
    assert "created_at" in sent_data
    assert "updated_at" in sent_data

    assert isinstance(updated_edge, BaseEdge)
    assert updated_edge.metadata == {"weight": 2.0}

@pytest.mark.asyncio
async def test_delete_edge(graph_manager, mock_surreal_client):
    edge_id = "contains:edge_1"

    await graph_manager.delete_edge(edge_id)

    mock_surreal_client.delete.assert_awaited_once_with(edge_id)