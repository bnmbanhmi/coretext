import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from coretext.server.app import app
from coretext.server.dependencies import get_db_client

# Override DB client to avoid connection logic inside dependencies.py
# (Though AsyncSurreal patch also helps)
async def override_get_db_client():
    return AsyncMock()

app.dependency_overrides[get_db_client] = override_get_db_client

# Patch AsyncSurreal globally to prevent connection attempts
@pytest.fixture(autouse=True)
def mock_surreal_connection():
    with patch("coretext.server.dependencies.AsyncSurreal") as MockSurreal:
        mock_instance = MockSurreal.return_value
        mock_instance.connect = AsyncMock()
        mock_instance.use = AsyncMock()
        mock_instance.close = AsyncMock()
        yield MockSurreal

# Patch GraphManager class so dependencies.py instantiates a Mock
@pytest.fixture(autouse=True)
def mock_graph_manager_class():
    with patch("coretext.server.dependencies.GraphManager") as MockGraphManager:
        yield MockGraphManager

# Patch VectorEmbedder to avoid model download
@pytest.fixture(autouse=True)
def mock_vector_embedder():
    with patch("coretext.server.dependencies.VectorEmbedder") as MockEmbedder:
        yield MockEmbedder

client = TestClient(app)

def test_mcp_tool_stub_returns_501():
    """Test that the MCP tool endpoint exists but returns 501 for now."""
    response = client.get("/mcp/tools/test_tool")
    assert response.status_code == 501
    assert response.json() == {"detail": "Tool 'test_tool' not implemented."}

def test_search_topology(mock_graph_manager_class):
    """Test the search_topology endpoint."""
    # Get the mock instance that dependencies.py would have created
    mock_instance = mock_graph_manager_class.return_value
    mock_instance.search_topology = AsyncMock(return_value=[{"id": "1", "score": 0.9}])
    
    response = client.post(
        "/mcp/tools/search_topology",
        json={"query": "test query", "limit": 5}
    )
    
    if response.status_code != 200:
        print(f"FAILED Response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "1"
    
    # Verify mock call
    mock_instance.search_topology.assert_awaited_with("test query", limit=5)

def test_search_topology_validation():
    """Test validation on search_topology endpoint."""
    # Limit too high
    response = client.post(
        "/mcp/tools/search_topology",
        json={"query": "test", "limit": 100}
    )
    assert response.status_code == 422

    # Missing query
    response = client.post(
        "/mcp/tools/search_topology",
        json={"limit": 5}
    )
    assert response.status_code == 422