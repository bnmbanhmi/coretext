from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

class ToolResponse(BaseModel):
    """
    Schema for tool response.
    """
    status: str
    tool: str

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
