import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
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

def test_mcp_tool_not_found_returns_404():
    """Test that requesting a non-existent tool returns 404."""
    response = client.get("/mcp/tools/unknown_tool")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

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