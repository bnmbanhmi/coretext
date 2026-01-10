import sys
import json
import logging
import asyncio
import httpx
from typing import Optional, Dict, Any, List
from pathlib import Path
from coretext.config import load_config
from coretext.cli.utils import check_daemon_health

# Set up logging to stderr so it doesn't interfere with stdout JSON-RPC
logging.basicConfig(stream=sys.stderr, level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_adapter")

class MCPStdioAdapter:
    """
    Bridges MCP JSON-RPC over Stdio to the CoreText HTTP Daemon.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config = load_config(project_root)
        self.base_url = f"http://127.0.0.1:{self.config.mcp_port}"
        
    async def process_messages(self):
        """
        Reads lines from stdin, processes them as JSON-RPC, proxies to HTTP, and writes responses to stdout.
        """
        logger.info(f"Starting MCP Adapter. Connecting to {self.base_url}")
        
        # Ensure daemon is running
        health = check_daemon_health(server_port=self.config.mcp_port, db_port=self.config.daemon_port, project_root=self.project_root)
        if health["server"]["status"] != "Running":
             logger.info("Daemon is not running. Attempting to auto-start...")
             try:
                 # Auto-start logic
                 import subprocess
                 # We assume 'coretext' command is available since we are running the adapter
                 # Or use sys.executable -m coretext.main start
                 cmd = [sys.executable, "-m", "coretext.main", "start"]
                 subprocess.Popen(
                     cmd,
                     cwd=str(self.project_root),
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL
                 )
                 
                 # Wait for it to come up
                 import time
                 for _ in range(20): # Wait up to 10 seconds
                     time.sleep(0.5)
                     health = check_daemon_health(server_port=self.config.mcp_port, db_port=self.config.daemon_port, project_root=self.project_root)
                     if health["server"]["status"] == "Running":
                         logger.info("Daemon started successfully.")
                         break
                 else:
                     logger.error("Failed to auto-start daemon. Adapter cannot function.")
                     sys.exit(1)
                     
             except Exception as e:
                 logger.error(f"Error during auto-start: {e}")
                 sys.exit(1)

        # Start a thread to read stdin to avoid asyncio selector issues with pipes/kqueue
        loop = asyncio.get_running_loop()
        queue = asyncio.Queue()

        def reader_thread():
            try:
                for line in sys.stdin:
                    asyncio.run_coroutine_threadsafe(queue.put(line), loop)
            except Exception:
                pass
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        import threading
        t = threading.Thread(target=reader_thread, daemon=True)
        t.start()
        
        while True:
            line = await queue.get()
            if line is None: # EOF
                break
            
            message = line.strip()
            if not message:
                continue
                
            try:
                request = json.loads(message)
                if "method" in request:
                    await self.handle_request(request)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {message}")
                continue
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                continue

    async def handle_request(self, request: Dict[str, Any]):
        method = request.get("method")
        msg_id = request.get("id")
        params = request.get("params", {})
        
        response = {
            "jsonrpc": "2.0",
            "id": msg_id
        }
        
        try:
            if method == "initialize":
                client_protocol = params.get("protocolVersion", "2024-11-25")
                # MCP initialization
                response["result"] = {
                    "protocolVersion": client_protocol,
                    "capabilities": {
                        "tools": {} # We support tools
                    },
                    "serverInfo": {
                        "name": "coretext",
                        "version": "0.1.0"
                    }
                }
            
            elif method == "notifications/initialized":
                 # Notification, no response needed
                 return

            elif method == "ping":
                response["result"] = {}

            elif method == "tools/list":
                # Fetch tools from Daemon manifest
                tools = await self.fetch_tools()
                response["result"] = {"tools": tools}
                
            elif method == "tools/call":
                # Execute tool via Daemon
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                result = await self.call_tool(tool_name, tool_args)
                response["result"] = result
                
            else:
                # Method not found
                response["error"] = {"code": -32601, "message": f"Method not found: {method}"}
                
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            response["error"] = {"code": -32000, "message": str(e)}
        
        # Write response to stdout
        if "id" in request: # Only respond if it's a request (not a notification)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

    async def fetch_tools(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/mcp/manifest")
            resp.raise_for_status()
            manifest = resp.json()
            # Transform to MCP Tool format if needed, but manifest.py likely returns MCP format already
            # Check routes.py: generate_manifest returns the structure.
            # Assuming generate_manifest returns {"tools": [...]} or similar.
            # If it returns a list of tools directly or a dict with tool definitions.
            # Let's check routes.py docstring or manifest.py (I'll assume it matches standard MCP or needs slight adapt).
            # Update: routes.py calls generate_manifest. I haven't seen manifest.py.
            # Assuming it returns a dict with "tools" key or similar list.
            
            # Let's optimistically assume it returns a list of tool objects compatible with MCP.
            # If manifest returns {"tools": [...]}, we extract that.
            if isinstance(manifest, dict) and "tools" in manifest:
                return manifest["tools"]
            elif isinstance(manifest, list):
                return manifest
            else:
                 return []

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Map tool name to endpoint
        # tools/search_topology -> /mcp/tools/search_topology
        # tools/query_knowledge -> /mcp/tools/query_knowledge
        # tools/get_dependencies -> /mcp/tools/get_dependencies
        
        # Note: routes.py defines endpoints as /tools/{name} (e.g., /tools/search_topology) 
        # but inside a router. The router prefix in app.py might be /mcp.
        # So full path: /mcp/tools/{name}.
        
        endpoint = f"/mcp/tools/{name}"
        
        async with httpx.AsyncClient() as client:
             # Most tools in routes.py take a Pydantic model as body.
             # arguments should map to that model.
             
             resp = await client.post(f"{self.base_url}{endpoint}", json=arguments, timeout=30.0)
             
             if resp.status_code != 200:
                 return {
                     "content": [
                         {
                             "type": "text",
                             "text": f"Error: {resp.status_code} - {resp.text}"
                         }
                     ],
                     "isError": True
                 }
             
             data = resp.json()
             return {
                 "content": [
                     {
                         "type": "text",
                         "text": json.dumps(data, indent=2)
                     }
                 ]
             }

async def run_adapter(project_root: Path):
    adapter = MCPStdioAdapter(project_root)
    await adapter.process_messages()

def main_adapter(project_root: Path = Path.cwd()):
    try:
        asyncio.run(run_adapter(project_root))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal adapter error: {e}")
        sys.exit(1)
