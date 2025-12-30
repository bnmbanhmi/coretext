from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Any
from coretext.core.parser.schema import SchemaMapper
from coretext.core.graph.manager import GraphManager
from coretext.server.dependencies import get_graph_manager, get_schema_mapper
from coretext.server.mcp.manifest import generate_manifest

router = APIRouter()

class ToolResponse(BaseModel):
    """
    Schema for tool response.
    """
    status: str = Field(..., description="The status of the tool execution or retrieval.")
    tool: str = Field(..., description="The name or identifier of the tool.")

class SearchTopologyRequest(BaseModel):
    query: str = Field(..., description="The semantic search query.")
    limit: int = Field(default=5, ge=1, le=20, description="Max results to return.")

class SearchTopologyResponse(BaseModel):
    results: List[dict[str, Any]] = Field(..., description="List of nodes matching the search query with relevance scores.")

class DependencyItem(BaseModel):
    node_id: str = Field(..., description="The unique identifier of the dependent node.")
    from_node_id: str = Field(..., description="The ID of the node that this dependency originates from.")
    relationship_type: str = Field(..., description="The type of relationship (e.g., 'IMPORTS', 'INHERITS').")
    direction: str = Field(..., description="The direction of the dependency ('in' or 'out').")

class GetDependenciesRequest(BaseModel):
    node_identifier: str = Field(..., description="The ID or file path of the node (e.g., 'file:path/to/file').")
    depth: int = Field(default=1, ge=1, le=5, description="Traversal depth.")

class GetDependenciesResponse(BaseModel):
    dependencies: List[DependencyItem] = Field(..., description="List of direct and indirect dependencies found.")

# Simple cache for the manifest to avoid re-generating on every get_tool call
_manifest_cache = None

@router.post("/tools/get_dependencies", response_model=GetDependenciesResponse)
async def get_dependencies(
    request: GetDependenciesRequest,
    graph_manager: GraphManager = Depends(get_graph_manager),
    schema_mapper: SchemaMapper = Depends(get_schema_mapper)
):
    """
    Retrieve direct and indirect dependencies for a given node.
    
    Args:
        request: The dependency retrieval request.
        graph_manager: Injected GraphManager instance.
        schema_mapper: Injected SchemaMapper instance.
        
    Returns:
        GetDependenciesResponse: List of dependencies with relationship details.

    Example I/O:
        Input: {"node_identifier": "file:main.py", "depth": 1}
        Output: {"dependencies": [{"node_id": "file:utils.py", "relationship_type": "IMPORTS", "direction": "out"}]}
    """
    try:
        node_id = request.node_identifier
        
        # Basic path normalization for relative paths
        if node_id.startswith("./"):
            node_id = node_id[2:]
        elif node_id.startswith("../"):
             import os
             node_id = os.path.normpath(node_id)

        # Resolve prefix if present
        if ":" in node_id:
            prefix, rest = node_id.split(":", 1)
            # Normalize the path part even if prefixed
            if rest.startswith("./"):
                rest = rest[2:]
            elif rest.startswith("../"):
                import os
                rest = os.path.normpath(rest)

            try:
                table = schema_mapper.get_node_table(prefix)
                # If prefix is a known node type, use the mapped table
                node_id = f"{table}:`{rest.strip('`')}`"
            except KeyError:
                # If prefix is not a known node type, it might be a raw table name (e.g. 'node')
                pass
        else:
            # No prefix, handle path heuristic
            if "/" in node_id or "." in node_id:
                table = schema_mapper.get_node_table("file")
                node_id = f"{table}:`{node_id}`"

        results = await graph_manager.get_dependencies(node_id, depth=request.depth)
        
        # If no dependencies found, verify if node exists to distinguish between "leaf node" and "node not found"
        if not results:
             node = await graph_manager.get_node(node_id)
             if not node:
                 raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

        return GetDependenciesResponse(dependencies=results)
    except HTTPException:
        raise
    except Exception as e:
        # In a real app, log the exception: logger.error(f"Dependency retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during dependency retrieval: {str(e)}")

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

    Example I/O:
        Input: {"query": "authentication logic", "limit": 2}
        Output: {"results": [{"id": "file:auth.py", "score": 0.92}, {"id": "file:main.py", "score": 0.85}]}
    """
    try:
        results = await graph_manager.search_topology(request.query, limit=request.limit)
        return SearchTopologyResponse(results=results)
    except Exception as e:
        # Log error here if logging is set up
        raise HTTPException(status_code=500, detail="Internal server error during topology search.")

@router.get("/manifest")
async def get_manifest(request: Request):
    """
    Get the MCP tool manifest.
    
    Returns:
        dict: The manifest containing available tools and their schemas.
    """
    global _manifest_cache
    _manifest_cache = generate_manifest(request.app.routes)
    return _manifest_cache

