
import yaml
from pathlib import Path

def test_extension_manifest_structure():
    """Verify extension.yaml contains the required MCP configuration."""
    manifest_path = Path("extension.yaml")
    assert manifest_path.exists()
    
    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)
        
    # Check for mcpServers section
    assert "mcpServers" in manifest, "Manifest missing 'mcpServers' section"
    
    # Check for coretext server definition
    assert "coretext" in manifest["mcpServers"], "Manifest missing 'coretext' server definition"
    
    # Check for HTTP configuration (as per Dev Notes preference)
    server_config = manifest["mcpServers"]["coretext"]
    assert "url" in server_config, "CoreText server missing 'url' configuration"
    assert server_config["url"] == "http://127.0.0.1:8001/mcp", "Incorrect URL for CoreText MCP server" 
    # Note: Standard MCP HTTP often uses /sse for Server-Sent Events, or we might point to the base /mcp depending on implementation.
    # The routes.py showed /mcp/manifest. 
    # Usually MCP over HTTP uses SSE for events and POST for JSON-RPC.
    # Let's check routes.py again for SSE endpoint.
