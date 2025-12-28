from fastapi.routing import APIRoute
from pydantic import BaseModel
from typing import List, Any

def generate_manifest(routes: List[Any]) -> dict:
    """
    Generates an MCP manifest by inspecting FastAPI routes.
    
    Args:
        routes: A list of FastAPI routes (e.g., app.routes or router.routes).
        
    Returns:
        dict: The MCP manifest containing tool definitions.
    """
    tools = []
    
    for route in routes:
        if not isinstance(route, APIRoute):
            continue
            
        # We assume tools are exposed via POST at /tools/{tool_name}
        if "/tools/" in route.path and "POST" in route.methods:
            tool_name = route.path.strip("/").split("/")[-1]
            
            # Extract description from docstring (route.description is populated from docstring by FastAPI)
            description = route.description or route.summary or ""
            # Clean up: take the first paragraph/line to avoid cluttering with Args/Returns/Examples
            # (Agents prefer a concise summary first)
            description = description.split("\n\n")[0].split("\r\n\r\n")[0].strip()
            
            input_schema = {}
            if route.body_field:
                # The body field type is the Pydantic model
                model = route.body_field.type_
                # Check if it's a Pydantic model
                if hasattr(model, "model_json_schema"):
                    input_schema = model.model_json_schema()
                
            tools.append({
                "name": tool_name,
                "description": description.strip(),
                "input_schema": input_schema
            })
            
    return {"tools": tools}
