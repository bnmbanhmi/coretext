from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Any
from coretext.core.graph.manager import GraphManager
from coretext.server.dependencies import get_graph_manager

router = APIRouter()

class ToolResponse(BaseModel):
    """
    Schema for tool response.
    """
    status: str
    tool: str

class SearchTopologyRequest(BaseModel):
    query: str = Field(..., description="The semantic search query.")
    limit: int = Field(default=5, ge=1, le=20, description="Max results to return.")

class SearchTopologyResponse(BaseModel):
    results: List[dict[str, Any]]

class DependencyItem(BaseModel):
    node_id: str
    relationship_type: str
    direction: str

class GetDependenciesRequest(BaseModel):
    node_identifier: str = Field(..., description="The ID or file path of the node (e.g., 'file:path/to/file').")
    depth: int = Field(default=1, ge=1, le=5, description="Traversal depth.")

class GetDependenciesResponse(BaseModel):
    dependencies: List[DependencyItem]

@router.get("/tools/{tool_name}", response_model=ToolResponse)
async def get_tool(tool_name: str):
    """
    Get a specific MCP tool.

    Args:
        tool_name: The name of the tool to retrieve.

    Returns:
        ToolResponse: Details about the tool.

    Raises:
        HTTPException: 501 Not Implemented (Tools are currently stubs).
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Tool '{tool_name}' not implemented."
    )

@router.post("/tools/get_dependencies", response_model=GetDependenciesResponse)
async def get_dependencies(
    request: GetDependenciesRequest,
    graph_manager: GraphManager = Depends(get_graph_manager)
):
    """
    Retrieve direct and indirect dependencies for a given node.
    
    Args:
        request: The dependency retrieval request.
        graph_manager: Injected GraphManager instance.
        
    Returns:
        GetDependenciesResponse: List of dependencies with relationship details.
    """
    try:
        # Simple heuristic: if no table prefix, assume it's a file path and prepend 'file:'
        # This makes it easier for the agent to just pass a path.
        node_id = request.node_identifier
        if ":" not in node_id:
            # We assume it's a file path.
            # We also need to handle potential quoting if needed, but for now we trust the client handles binding
            # However, if we construct the string 'file:path', we rely on SurrealDB to parse 'path' as the ID.
            # If path has special chars, it might be tricky without backticks, but let's try strict first.
            # If the user passes "core/manager.py", we convert to "file:core/manager.py".
            node_id = f"file:{node_id}"

        results = await graph_manager.get_dependencies(node_id, depth=request.depth)
        return GetDependenciesResponse(dependencies=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/search_topology", response_model=SearchTopologyResponse)
async def search_topology(
    request: SearchTopologyRequest,
    graph_manager: GraphManager = Depends(get_graph_manager)
):
    """
    Search the knowledge graph for topological connections using semantic similarity.
    
    This tool allows AI agents to understand project structure and dependencies by finding
    nodes (Files, Headers) relevant to a natural language query.
    
    Args:
        request: The search request containing query and limit.
        graph_manager: Injected GraphManager instance.
        
    Returns:
        SearchTopologyResponse: List of matching nodes with scores.
    """
    try:
        results = await graph_manager.search_topology(request.query, limit=request.limit)
        return SearchTopologyResponse(results=results)
    except Exception as e:
        # Log error here if logging is set up
        raise HTTPException(status_code=500, detail=str(e))

