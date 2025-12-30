import pytest
from fastapi.testclient import TestClient
from coretext.server.app import app

client = TestClient(app)

from fastapi import HTTPException
from coretext.server.health import verify_localhost

def test_health_check_ok():
    """Test that /health returns 200 OK (default TestClient is from 127.0.0.1)."""
    response = client.get("/health")
    # By default TestClient uses "testclient" which might fail if we stripped it, 
    # BUT we can override the dependency to force success if needed, 
    # OR we rely on TestClient behaving correctly. 
    # Let's override the dependency to be safe and pure unit test logic.
    app.dependency_overrides[verify_localhost] = lambda: None
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    
    # Reset overrides
    app.dependency_overrides = {}

def test_health_check_localhost_only():
    """
    Test that /health forbids non-localhost requests.
    We verify this by overriding the dependency to raise the exception,
    proving that if the logic fails, the route handles it (or rather the dependency does).
    
    Better yet: We test the DEPENDENCY logic itself or usage of it.
    Input: Override verify_localhost to raise 403.
    Output: 403.
    """
    # 1. Test that the Endpoint PROTECTS itself (integration of dependency)
    def mock_forbidden():
        raise HTTPException(status_code=403, detail="Access forbidden: Localhost only.")
        
    app.dependency_overrides[verify_localhost] = mock_forbidden
    
    response = client.get("/health")
    assert response.status_code == 403
    assert response.json() == {"detail": "Access forbidden: Localhost only."}
    
    app.dependency_overrides = {}

def test_verify_localhost_logic():
    """
    Directly test the dependency logic with mocked Request.
    """
    import asyncio
    from unittest.mock import MagicMock
    from coretext.server.health import verify_localhost

    # Case 1: External IP
    req = MagicMock()
    req.client.host = "1.2.3.4"
    
    # dependencies are async/sync? verify_localhost is async
    try:
        asyncio.run(verify_localhost(req))
        assert False, "Should raise HTTPException"
    except HTTPException as e:
        assert e.status_code == 403

    # Case 2: Localhost
    req.client.host = "127.0.0.1"
    asyncio.run(verify_localhost(req)) # Should not raise

