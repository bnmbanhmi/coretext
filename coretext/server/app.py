from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from coretext.server.health import router as health_router
from coretext.server.mcp.routes import router as mcp_router
from coretext.server.routers.lint import router as lint_router
from coretext.config import load_config
from coretext.core.system.process import set_background_priority
from coretext.server.dependencies import get_memory_watchdog

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI app.
    Handles startup configuration and shutdown cleanup.
    """
    # Load configuration
    # Assuming CWD is project root when running the server
    config = load_config()
    
    # Set process priority if configured
    if config.system.background_priority:
        logger.info("Configuring daemon for background priority")
        set_background_priority()
        
    # Initialize and start MemoryWatchdog via dependency provider (singleton)
    watchdog = get_memory_watchdog()
    await watchdog.start()
    
    try:
        yield
    finally:
        # Cleanup on shutdown
        await watchdog.stop()

app = FastAPI(title="CoreText MCP Server", lifespan=lifespan)

# Include the health check router
app.include_router(health_router)

# Include the MCP router
app.include_router(mcp_router, prefix="/mcp")

# Include the Lint router
app.include_router(lint_router)