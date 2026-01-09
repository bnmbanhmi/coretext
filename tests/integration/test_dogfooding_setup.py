import pytest
import yaml
import requests
import os
from pathlib import Path

CONFIG_PATH = Path(".coretext/config.yaml")
EXTENSION_PATH = Path("extension.yaml")

def test_extension_yaml_config():
    """Verify extension.yaml points to local daemon MCP."""
    assert EXTENSION_PATH.exists()
    with open(EXTENSION_PATH, "r") as f:
        data = yaml.safe_load(f)
    
    assert "mcpServers" in data
    assert "coretext" in data["mcpServers"]
    assert data["mcpServers"]["coretext"]["url"] == "http://127.0.0.1:8001/mcp"

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
