import pytest
from fastapi.testclient import TestClient
from coretext.server.app import app

client = TestClient(app)

def test_mcp_tool_stub_returns_501():
    """Test that the MCP tool endpoint exists but returns 501 for now."""
    response = client.get("/mcp/tools/test_tool")
    assert response.status_code == 501
    assert response.json() == {"detail": "Tool 'test_tool' not implemented."}
