import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from coretext.core.graph.manager import GraphManager
from coretext.core.graph.models import BaseNode, BaseEdge
from coretext.core.parser.schema import SchemaMapper
from coretext.core.vector.embedder import VectorEmbedder
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
def mock_embedder():
    return AsyncMock(spec=VectorEmbedder)

@pytest.fixture
def graph_manager(mock_surreal_client, mock_schema_mapper, mock_embedder):
    return GraphManager(mock_surreal_client, mock_schema_mapper, embedder=mock_embedder)

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
    assert call_args[0] == f"node:`{node_data.id}`"
    
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
    assert call_args[0] == f"node:`{node_data.id}`"
    
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

    # create_edge uses query (RELATE), so we mock query
    mock_surreal_client.query.return_value = [mock_return_value]

    created_edge = await graph_manager.create_edge(edge_data)

    mock_surreal_client.query.assert_awaited_once() # Check that query was called
    call_args = mock_surreal_client.query.call_args.args
    assert "RELATE" in call_args[0]
    
    sent_params = call_args[1]["data"]
    assert sent_params["edge_type"] == edge_data.edge_type
    assert sent_params["metadata"] == edge_data.metadata
    assert "created_at" in sent_params
    assert "updated_at" in sent_params

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
    
    # update_edge uses query (RELATE), so we mock query
    mock_surreal_client.query.return_value = [mock_return_value]

    updated_edge = await graph_manager.update_edge(edge_data)

    mock_surreal_client.query.assert_awaited_once() # Check that query was called
    call_args = mock_surreal_client.query.call_args.args
    assert "RELATE" in call_args[0]
    
    sent_params = call_args[1]["data"]
    assert sent_params["edge_type"] == edge_data.edge_type
    assert sent_params["metadata"] == edge_data.metadata
    assert "created_at" in sent_params
    assert "updated_at" in sent_params

    assert isinstance(updated_edge, BaseEdge)
    assert updated_edge.metadata == {"weight": 2.0}

@pytest.mark.asyncio
async def test_delete_edge(graph_manager, mock_surreal_client):
    edge_id = "contains:edge_1"

    await graph_manager.delete_edge(edge_id)

    mock_surreal_client.delete.assert_awaited_once_with(edge_id)

@pytest.mark.asyncio
async def test_search_topology(graph_manager, mock_surreal_client, mock_embedder):
    query = "test query"
    embedding = [0.1] * 768
    
    # Mock the VectorEmbedder to return a dummy embedding
    mock_embedder.encode.return_value = embedding
    
    # Mock DB query result
    # SurrealDB returns a list of results (one for each statement in the query string)
    # Our query has one statement.
    mock_surreal_client.query.return_value = [
        {
            "status": "OK",
            "time": "100us",
            "result": [
                {"id": "node:1", "score": 0.9, "content": "result 1"},
                {"id": "node:2", "score": 0.8, "content": "result 2"}
            ]
        }
    ]
    
    results = await graph_manager.search_topology(query, limit=5)
    
    # Check if embedder was called with correct task type
    mock_embedder.encode.assert_awaited_once_with(query, task_type="search_query")
    
    # Check if DB query was called
    mock_surreal_client.query.assert_awaited_once()
    call_args = mock_surreal_client.query.call_args
    sql_query = call_args[0][0]
    params = call_args[0][1]
    
    assert "vector::similarity::cosine" in sql_query
    assert params["embedding"] == embedding
    assert "embedding <|5|> $embedding" in sql_query or "embedding <| 5 |> $embedding" in sql_query.replace(" ", "")
    
    assert len(results) == 2
    assert results[0]["id"] == "node:1"

@pytest.mark.asyncio
async def test_get_dependencies(graph_manager, mock_surreal_client):
    node_id = "node:test_node_1"
    depth = 1
    
    # Mock DB query result for dependencies
    # Expecting a list of {node_id, relationship, direction}
    # But the raw SQL result will be more complex, likely nodes with edge info.
    # For now, let's assume the method normalizes it.
    
    # Mocking the raw response from SurrealDB for a graph traversal query
    # The actual query structure will be determined in implementation, but we expect
    # the manager to process it into a clean list.
    mock_surreal_client.query.return_value = [
        {
            "status": "OK",
            "time": "100us",
            "result": [
                {
                    "dependency": "node:dep_1",
                    "relationship": "depends_on",
                    "direction": "outgoing"
                },
                {
                    "dependency": "node:gov_1",
                    "relationship": "governed_by",
                    "direction": "outgoing"
                },
                 {
                    "dependency": "node:parent_1",
                    "relationship": "parent_of",
                    "direction": "incoming"
                }
            ]
        }
    ]

    dependencies = await graph_manager.get_dependencies(node_id, depth=depth)

    mock_surreal_client.query.assert_awaited_once()
    call_args = mock_surreal_client.query.call_args
    sql_query = call_args[0][0]
    params = call_args[0][1]

    assert "SELECT" in sql_query
    assert node_id in params.values() or node_id in sql_query
    # Check if important edge types are mentioned
    assert "depends_on" in sql_query
    assert "governed_by" in sql_query
    
    assert len(dependencies) == 3
    assert dependencies[0]["node_id"] == "node:dep_1"
    assert dependencies[0]["relationship_type"] == "depends_on"
    assert dependencies[0]["direction"] == "outgoing"
