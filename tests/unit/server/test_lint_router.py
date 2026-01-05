import pytest
from fastapi.testclient import TestClient
from coretext.server.app import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_lint_endpoint_success():
    # We will mock the router implementation later, but for now we expect 404
    # Wait, RED phase means writing the test that SHOULD pass once implemented.
    # So checking for 200.
    
    # We need to mock the logic inside the route.
    # Since the route hasn't been imported in app.py yet, we can't patch it there easily unless we patch where it's defined.
    # But it's not defined yet.
    
    # So I will just expect 404 for now to confirm it's failing? 
    # No, RED means "Write failing tests first for the task/subtask functionality".
    # The test should fail because the feature isn't there.
    
    response = client.post("/lint", json={"files": ["test.md"]})
    assert response.status_code == 200 # Should be 404 now
