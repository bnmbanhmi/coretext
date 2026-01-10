import pytest
import yaml
import requests
import os
from pathlib import Path
import json

CONFIG_PATH = Path(".coretext/config.yaml")
EXTENSION_PATH = Path("gemini-extension.json")

def test_extension_config():
    """Verify extension points to local daemon MCP."""
    if not EXTENSION_PATH.exists():
        pytest.skip("gemini-extension.json not created yet")

    with open(EXTENSION_PATH, "r") as f:
        data = json.load(f)
    
    assert "mcpServers" in data
    assert "coretext" in data["mcpServers"]
    # Check checks based on type...

def test_coretext_config_for_dogfooding():
    """Verify .coretext/config.yaml is configured safely."""
    assert CONFIG_PATH.exists()
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    
    docs_dir = config.get("docs_dir")
    # Should be the specific knowledge directory
    assert docs_dir == "_coretext-knowledge", "docs_dir should be configured to '_coretext-knowledge' for safe isolation"

@pytest.mark.asyncio
async def test_daemon_health():
    """Verify daemon is running and healthy."""
    try:
        response = requests.get("http://127.0.0.1:8001/health", timeout=2)
        assert response.status_code == 200
        assert response.json().get("status") == "OK"
    except requests.exceptions.ConnectionError:
        pytest.fail("CoreText daemon is not reachable at http://127.0.0.1:8001/health")