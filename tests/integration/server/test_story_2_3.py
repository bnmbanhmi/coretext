import httpx
import pytest

# Story 2.3: Semantic Tool for Dependency Retrieval
# Acceptance Criteria:
# 1. Given the MCP server is running and the graph contains data
# 2. When the AI agent calls POST /mcp/tools/get_dependencies with a node identifier
# 3. Then coretext traverses depends_on, governed_by, or PARENT_OF edges in the graph.
# 4. And coretext returns a structured list of dependent nodes and their relationships.
# 5. And the tool is implemented to handle different types of relationships.

@pytest.fixture
def api_base_url():
    return "http://127.0.0.1:8001"

@pytest.mark.asyncio
async def test_get_dependencies_returns_tree(api_base_url):
    """
    GIVEN a known node in the graph
    WHEN the AI agent calls POST /mcp/tools/get_dependencies
    THEN the server returns its dependencies and relationships
    """
    # Use a dummy node ID that we expect to be in the seeded test DB
    node_id = "docs/prd.md"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{api_base_url}/mcp/tools/get_dependencies", 
            json={"node_id": node_id, "depth": 2}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "node" in data
    assert "dependencies" in data
    assert isinstance(data["dependencies"], list)
    
    if len(data["dependencies"]) > 0:
        dep = data["dependencies"][0]
        assert "id" in dep
        assert "relationship" in dep # e.g., "depends_on", "PARENT_OF"

@pytest.mark.asyncio
async def test_get_dependencies_not_found(api_base_url):
    """
    WHEN a non-existent node ID is provided
    THEN the server returns a 404
    """
    node_id = "non/existent/file.md"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{api_base_url}/mcp/tools/get_dependencies", 
            json={"node_id": node_id}
        )
    
    assert response.status_code == 404
