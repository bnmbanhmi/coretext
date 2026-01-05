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

def test_get_dependencies_endpoint(mock_graph_manager, override_dependency):
    # Setup mock return
    mock_graph_manager.get_dependencies.return_value = [
        {"node_id": "file:test.py", "from_node_id": "file:main.py", "relationship_type": "depends_on", "direction": "outgoing"},
        {"node_id": "file:parent.py", "from_node_id": "file:main.py", "relationship_type": "parent_of", "direction": "incoming"}
    ]
    
    payload = {
        "node_identifier": "file:main.py",
        "depth": 1
    }
    
    response = client.post("/mcp/tools/get_dependencies", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "dependencies" in data
    assert len(data["dependencies"]) == 2
    assert data["dependencies"][0]["node_id"] == "file:test.py"
    assert data["dependencies"][0]["relationship_type"] == "depends_on"
    
    # Verify graph manager called correctly
    mock_graph_manager.get_dependencies.assert_called_with("node:`main.py`", depth=1)

def test_get_manifest_endpoint(override_dependency):
    """
    Test that the /mcp/manifest endpoint returns a valid tool list.
    """
    response = client.get("/mcp/manifest")
    
    # Note: If endpoint is not implemented yet, this will fail (404)
    assert response.status_code == 200
    data = response.json()
    
    assert "tools" in data
    tool_names = [t["name"] for t in data["tools"]]
    assert "search_topology" in tool_names
    assert "get_dependencies" in tool_names

