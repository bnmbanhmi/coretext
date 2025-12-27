
import inspect
from fastapi.routing import APIRoute
from coretext.server.mcp.routes import (
    ToolResponse, SearchTopologyResponse, DependencyItem, GetDependenciesResponse,
    get_dependencies, search_topology, router
)

def test_pydantic_models_have_descriptions():
    """
    Verify that all fields in Pydantic models used in MCP routes have descriptions.
    This is critical for MCP manifest generation.
    """
    models_to_check = [
        ToolResponse,
        SearchTopologyResponse,
        DependencyItem,
        GetDependenciesResponse
    ]

    for model in models_to_check:
        schema = model.model_json_schema()
        properties = schema.get("properties", {})
        for field_name, field_info in properties.items():
            assert "description" in field_info, f"Field '{field_name}' in model '{model.__name__}' is missing a description."

def test_routes_have_google_style_docstrings():
    """
    Verify that MCP route handlers have docstrings.
    """
    # Check get_dependencies
    doc = inspect.getdoc(get_dependencies)
    assert doc is not None
    assert "Args:" in doc
    assert "Returns:" in doc
    
    # Check search_topology
    doc = inspect.getdoc(search_topology)
    assert doc is not None
    assert "Args:" in doc
    assert "Returns:" in doc

def test_routes_are_documented_in_openapi():
    """
    Ensure routes are properly registered and have names/summaries.
    """
    for route in router.routes:
        if isinstance(route, APIRoute):
            assert route.summary or route.name, f"Route {route.path} missing summary/name"
            assert route.description or route.summary, f"Route {route.path} missing description"
