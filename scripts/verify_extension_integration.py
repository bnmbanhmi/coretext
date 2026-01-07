
import yaml
import requests
import sys
import time
from pathlib import Path

def verify_extension_integration():
    print("Verifying extension.yaml integration...")
    manifest_path = Path("extension.yaml")
    
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
        
    print(f"✅ Found MCP URL: {url}")
    
    # 2. Construct Manifest URL
    # Assuming the URL in manifest points to the base of the MCP or the manifest endpoint directly.
    # If it points to /mcp, the manifest is likely at /mcp/manifest.
    # Let's try appending /manifest if it doesn't end with it.
    
    manifest_url = url
    if not manifest_url.endswith("/manifest"):
        if manifest_url.endswith("/"):
            manifest_url += "manifest"
        else:
            manifest_url += "/manifest"
            
    print(f"Checking Manifest Endpoint: {manifest_url}")
    
    try:
        response = requests.get(manifest_url)
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
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {manifest_url}. Is the daemon running?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_extension_integration()
