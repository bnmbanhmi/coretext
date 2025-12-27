
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from coretext.server.app import app
from coretext.server.dependencies import get_graph_manager
from coretext.core.graph.manager import GraphManager

client = TestClient(app)

@pytest.fixture
def mock_graph_manager():
    return AsyncMock(spec=GraphManager)

@pytest.fixture
def override_dependency(mock_graph_manager):
    app.dependency_overrides[get_graph_manager] = lambda: mock_graph_manager
    yield
    app.dependency_overrides = {}

def test_get_tool_not_found():
    """
    Test that requesting a non-existent tool returns 404.
    """
    # Currently checks implementation which raises 501 for everything.
    # We want to change this to 404 for unknown tools.
    response = client.get("/mcp/tools/unknown_tool")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_search_topology_generic_error(override_dependency, mock_graph_manager):
    """
    Test that internal errors are masked and return 500.
    """
    mock_graph_manager.search_topology.side_effect = Exception("Sensitive DB Info")
    
    response = client.post("/mcp/tools/search_topology", json={"query": "test"})
    
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error during topology search."
    # Should NOT leak "Sensitive DB Info"
