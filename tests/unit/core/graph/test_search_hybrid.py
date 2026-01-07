import pytest
from unittest.mock import AsyncMock, MagicMock, call
from coretext.core.graph.manager import GraphManager
from coretext.core.parser.schema import SchemaMapper
from coretext.core.vector.embedder import VectorEmbedder

@pytest.fixture
def mock_surreal_client():
    return AsyncMock()

@pytest.fixture
def mock_schema_mapper():
    mapper = MagicMock(spec=SchemaMapper)
    mapper.get_node_table.return_value = "node"
    mapper.get_edge_table.side_effect = lambda x: x
    
    # Mock schema_map structure for _get_all_node_tables
    mock_node_type = MagicMock()
    mock_node_type.db_table = "node"
    
    # Configure schema_map.node_types.values()
    mapper.schema_map.node_types.values.return_value = [mock_node_type]

    # Mock schema_map.edge_types for search_hybrid dynamic loading
    def create_edge_def(table):
        m = MagicMock()
        m.db_table = table
        return m

    mapper.schema_map.edge_types.items.return_value = [
        ("depends_on", create_edge_def("depends_on")),
        ("governed_by", create_edge_def("governed_by")),
        ("contains", create_edge_def("contains")),
        ("references", create_edge_def("references")),
        ("parent_of", create_edge_def("parent_of"))
    ]
    
    # Ensure _schema_map exists so the check doesn't fail or trigger load_schema
    mapper._schema_map = MagicMock()
    
    return mapper

@pytest.fixture
def mock_embedder():
    return AsyncMock(spec=VectorEmbedder)

@pytest.fixture
def graph_manager(mock_surreal_client, mock_schema_mapper, mock_embedder):
    return GraphManager(mock_surreal_client, mock_schema_mapper, embedder=mock_embedder)

@pytest.mark.asyncio
async def test_search_hybrid_vector_only(graph_manager, mock_surreal_client, mock_embedder):
    query = "test query"
    embedding = [0.1] * 768
    mock_embedder.encode.return_value = embedding
    
    # Mock search result (anchors)
    mock_surreal_client.query.side_effect = [
        [ # Anchor query result
            {"id": "node:1", "score": 0.9, "content": "result 1", "node_type": "file"},
            {"id": "node:2", "score": 0.8, "content": "result 2", "node_type": "header"}
        ],
        [], # Traversal batch 1
        [], # Node fetch (if any)
    ]
    
    # We are not testing traversal deeply here, just that search works
    graph_manager.get_dependencies = AsyncMock(return_value=[])
    
    results = await graph_manager.search_hybrid(query=query, top_k=5, depth=1)
    
    mock_embedder.encode.assert_awaited_once_with(query, task_type="search_query")
    
    # Verify SQL query (First call is the anchor search)
    call_args = mock_surreal_client.query.call_args_list[0]
    sql_query = call_args[0][0]
    params = call_args[0][1]
    
    assert "vector::similarity::cosine" in sql_query
    assert params["embedding"] == embedding
    assert "LIMIT $limit" in sql_query
    assert params["limit"] == 5

@pytest.mark.asyncio
async def test_search_hybrid_regex(graph_manager, mock_surreal_client, mock_embedder):
    query = "test"
    embedding = [0.1] * 768
    mock_embedder.encode.return_value = embedding
    
    graph_manager.get_dependencies = AsyncMock(return_value=[])
    mock_surreal_client.query.return_value = [[]]
    
    await graph_manager.search_hybrid(query=query, top_k=5, depth=1, regex="^/src/.*")
    
    # Since anchors are empty, only one call happens
    call_args = mock_surreal_client.query.call_args
    sql_query = call_args[0][0]
    params = call_args[0][1]
    
    assert "(id ~ $regex OR path ~ $regex OR content ~ $regex)" in sql_query
    assert params["regex"] == "^/src/.*"

@pytest.mark.asyncio
async def test_search_hybrid_keywords(graph_manager, mock_surreal_client, mock_embedder):
    query = "test"
    embedding = [0.1] * 768
    mock_embedder.encode.return_value = embedding
    
    graph_manager.get_dependencies = AsyncMock(return_value=[])
    mock_surreal_client.query.return_value = [[]]
    
    await graph_manager.search_hybrid(query=query, top_k=5, depth=1, keywords="API")
    
    call_args = mock_surreal_client.query.call_args
    sql_query = call_args[0][0]
    params = call_args[0][1]
    
    assert "AND content CONTAINS $keyword" in sql_query
    assert params["keyword"] == "API"

@pytest.mark.asyncio
async def test_search_hybrid_returns_subgraph(graph_manager, mock_surreal_client, mock_embedder):
    query = "test"
    embedding = [0.1] * 768
    mock_embedder.encode.return_value = embedding
    
    # Mock anchors (Call 1)
    anchors = [{"id": "node:1", "node_type": "file", "score": 0.9, "embedding": embedding}]
    
    # Mock Traversal (Call 2) - 5 queries in batch
    # Order: Sorted Outgoing [contains, depends_on, governed_by, references] 
    #        Then Sorted Incoming [parent_of]
    
    # Let's return one edge for "depends_on" (index 1)
    edge_res = {"id": "depends_on:1", "in": "node:1", "out": "node:2", "edge_type": "depends_on"}
    traversal_results = [
        {"status": "OK", "result": []}, # contains (index 0)
        {"status": "OK", "result": [edge_res]}, # depends_on (index 1)
        {"status": "OK", "result": []}, # governed_by
        {"status": "OK", "result": []}, # references
        {"status": "OK", "result": []}, # parent_of
    ]
    
    # Mock Node Fetch (Call 3) - fetching node:2
    node_res = [{"id": "node:2", "node_type": "file", "content": "dep content", "embedding": embedding}]
    
    mock_surreal_client.query.side_effect = [
        [{"status": "OK", "result": anchors}], # Anchors
        traversal_results, # Traversal batch
        [{"status": "OK", "result": node_res}] # Fetch new nodes
    ]
    
    # Run
    result = await graph_manager.search_hybrid(query=query, top_k=5, depth=1)
    
    assert len(result["nodes"]) == 2 # node:1 and node:2
    assert len(result["edges"]) == 1 # depends_on:1
    
    node_ids = [n.id for n in result["nodes"]]
    assert "node:1" in node_ids
    assert "node:2" in node_ids

    # Verify embeddings are stripped (Fix verification)
    for node in result["nodes"]:
        assert node.embedding is None