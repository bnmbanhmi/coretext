import httpx
import pytest

# Story 2.2: Semantic Tool for Topology Search
# Acceptance Criteria:
# 1. Given the MCP server is running and the graph contains data
# 2. When the AI agent calls POST /mcp/tools/search_topology with a query
# 3. Then coretext uses nomic-embed-text-v1.5 for query embedding.
# 4. And coretext performs a vector similarity search in SurrealDB.
# 5. And coretext traverses graph relationships to find topologically relevant nodes.
# 6. And coretext returns a list of relevant graph nodes as context.

@pytest.fixture
def api_base_url():
    return "http://127.0.0.1:8001" # Default test port

@pytest.mark.skip(reason="Integration environment not available (requires running server + DB)")
@pytest.mark.asyncio
async def test_search_topology_returns_relevant_nodes(api_base_url):
    """
    GIVEN the MCP server is running and the graph contains data
    WHEN the AI agent calls POST /mcp/tools/search_topology with a query
    THEN the server returns a list of relevant graph nodes
    """
    query_data = {
        "query": "authentication service patterns",
        "top_k": 5
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{api_base_url}/mcp/tools/search_topology", json=query_data)
    
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    # Each result should have at least id, type, and content/metadata
    if len(results) > 0:
        assert "id" in results[0]
        assert "type" in results[0]
        assert "score" in results[0] # Evidence of vector similarity search

@pytest.mark.skip(reason="Integration environment not available (requires running server + DB)")
@pytest.mark.asyncio
async def test_search_topology_handles_empty_results(api_base_url):
    """
    WHEN searching for something non-existent
    THEN the server returns an empty list
    """
    query_data = {
        "query": "nonexistent_random_string_xyz_123",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{api_base_url}/mcp/tools/search_topology", json=query_data)
    
    assert response.status_code == 200
    assert response.json() == []
