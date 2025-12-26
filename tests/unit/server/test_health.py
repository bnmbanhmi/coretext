import pytest
from fastapi.testclient import TestClient
from coretext.server.app import app

client = TestClient(app)

def test_health_check_ok():
    """Test that /health returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_health_check_localhost_only():
    """
    Test that /health forbids non-localhost requests.
    Note: TestClient defaults to 127.0.0.1 (or 'testclient').
    We need to simulate a non-local request.
    """
    # This requires looking at how we implement the check. 
    # If we check request.client.host, we need to mock it.
    # For now, just a placeholder or we can inject a dependency.
    pass
