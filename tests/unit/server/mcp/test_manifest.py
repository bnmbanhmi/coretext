
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field
from coretext.server.mcp.manifest import generate_manifest
from coretext.server.mcp.routes import router as mcp_router

class MockRequest(BaseModel):
    param: str = Field(..., description="A parameter.")

class MockResponse(BaseModel):
    result: str = Field(..., description="The result.")

def test_generate_manifest_extracts_tools():
    """
    Test that generate_manifest correctly inspects a FastAPI app/router
    and produces the MCP manifest format.
    """
    app = FastAPI()
    router = APIRouter()

    @router.post("/tools/mock_tool", response_model=MockResponse)
    async def mock_tool(request: MockRequest):
        """
        A mock tool for testing.
        
        Args:
            request: The mock request.
            
        Returns:
            MockResponse: The mock response.
        """
        pass

    app.include_router(router)
    
    # We will likely pass the router or the app.
    # If we pass the router, we need to inspect its routes.
    # The implementation might require the app to fully resolve OpenAPI, 
    # but let's see if we can do it with just the router or a list of routes.
    # For now, let's assume we pass the list of routes or the app.
    # The story says "inspect FastAPI routes".
    
    manifest = generate_manifest(app.routes)
    
    assert "tools" in manifest
    tools = manifest["tools"]
    assert len(tools) >= 1
    
    tool = next((t for t in tools if t["name"] == "mock_tool"), None)
    assert tool is not None
    assert tool["description"].strip().startswith("A mock tool for testing.")
    assert "inputSchema" in tool
    assert "properties" in tool["inputSchema"]
    assert "param" in tool["inputSchema"]["properties"]
    assert tool["inputSchema"]["properties"]["param"]["description"] == "A parameter."

def test_mcp_routes_manifest_generation():
    """
    Test that the actual MCP router generates a valid manifest.
    """
    # We can mock the routes list by taking them from mcp_router
    # But mcp_router routes might not be fully populated until included in an app?
    # Actually, APIRouter.routes works.
    
    manifest = generate_manifest(mcp_router.routes)
    
    tool_names = [t["name"] for t in manifest["tools"]]
    assert "search_topology" in tool_names
    assert "get_dependencies" in tool_names
    
    search_tool = next(t for t in manifest["tools"] if t["name"] == "search_topology")
    assert "The semantic search query." in str(search_tool["inputSchema"])

