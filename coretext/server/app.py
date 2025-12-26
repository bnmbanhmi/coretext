from fastapi import FastAPI
from coretext.server.health import router as health_router
from coretext.server.mcp.routes import router as mcp_router

app = FastAPI(title="CoreText MCP Server")

# Include the health check router
app.include_router(health_router)

# Include the MCP router
app.include_router(mcp_router, prefix="/mcp")
