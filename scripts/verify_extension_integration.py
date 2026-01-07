
import yaml
import httpx
import sys
import time
from pathlib import Path
from coretext.config import load_config

def verify_extension_integration():
    print("Verifying extension.yaml integration...")
    manifest_path = Path("extension.yaml")
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
        print("❌ extension.yaml not found")
        sys.exit(1)
        
    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)
        
    mcp_config = manifest.get("mcpServers", {}).get("coretext", {})
    url = mcp_config.get("url")
    
    if not url:
        print("❌ No URL found in extension.yaml mcpServers.coretext")
        sys.exit(1)
        
    print(f"✅ Found MCP URL in manifest: {url}")

    # Validate Port Match
    if str(config_mcp_port) not in url:
        print(f"⚠️  WARNING: Mismatch detected! Config port is {config_mcp_port}, but manifest uses {url}.")
        print("    The extension might fail to connect if the daemon respects config.yaml.")
    
    # 2. Construct Manifest URL
    manifest_url = url
    if not manifest_url.endswith("/manifest"):
        if manifest_url.endswith("/"):
            manifest_url += "manifest"
        else:
            manifest_url += "/manifest"
            
    print(f"Checking Manifest Endpoint: {manifest_url}")
    
    try:
        response = httpx.get(manifest_url, timeout=5.0)
        if response.status_code == 200:
            print("✅ Connection Successful (200 OK)")
            data = response.json()
            tools = data.get("tools", [])
            print(f"✅ Found {len(tools)} tools")
            
            tool_names = [t["name"] for t in tools]
            if "query_knowledge" in tool_names:
                print("✅ Found 'query_knowledge' tool")
            else:
                print("❌ 'query_knowledge' tool missing from manifest")
                sys.exit(1)
        else:
            print(f"❌ Connection Failed: {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except httpx.RequestError:
        print(f"❌ Could not connect to {manifest_url}. Is the daemon running?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_extension_integration()
