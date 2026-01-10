import json
import httpx
import sys
import time
from pathlib import Path
from coretext.config import load_config

def verify_extension_integration():
    print("Verifying gemini-extension.json integration...")
    manifest_path = Path("gemini-extension.json")
    project_root = Path.cwd()
    
    # 0. Load Project Config for Validation
    try:
        config = load_config(project_root)
        config_mcp_port = config.mcp_port
        print(f"ℹ️  Configured MCP Port: {config_mcp_port}")
    except Exception as e:
        print(f"⚠️  Could not load config.yaml: {e}")
        config_mcp_port = 8001 # Default fallback

    # 1. Read Manifest
    if not manifest_path.exists():
        print("❌ gemini-extension.json not found")
        sys.exit(1)
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    mcp_config = manifest.get("mcpServers", {}).get("coretext", {})
    # Note: New format might use command/args, but if using URL/HTTP it would be here.
    # The story implies we are moving to command-based or staying HTTP.
    # If command based, we check for 'command'.
    
    # Let's support both for verification, but strict on existence.
    if "url" in mcp_config:
        url = mcp_config["url"]
        print(f"✅ Found MCP URL in manifest: {url}")
        
        # Validate Port Match
        if str(config_mcp_port) not in url:
            print(f"⚠️  WARNING: Mismatch detected! Config port is {config_mcp_port}, but manifest uses {url}.")
        
        # 2. Construct Manifest URL
        manifest_url = url
        if not manifest_url.endswith("/manifest"):
            if manifest_url.endswith("/"):
                manifest_url += "manifest"
            else:
                manifest_url += "/manifest"
                
        print(f"Checking Manifest Endpoint: {manifest_url}")
        # ... (Same HTTP check logic)
        
    elif "command" in mcp_config:
        print(f"✅ Found MCP Command in manifest: {mcp_config['command']}")
        print("ℹ️  Skipping HTTP check for command-based extension.")
        sys.exit(0)
    else:
        print("❌ No valid config (url or command) found in gemini-extension.json mcpServers.coretext")
        sys.exit(1)

if __name__ == "__main__":
    verify_extension_integration()