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
    
    # Startup Maintenance Task
    async def run_startup_maintenance():
        from surrealdb import AsyncSurreal
        from coretext.server.dependencies import get_schema_mapper, get_vector_embedder
        from coretext.core.graph.manager import GraphManager
        from coretext.core.system.maintenance import MaintenanceService
        import asyncio

        # Connect to DB (using default local address matching dependencies.py)
        # In a real scenario, this should come from config
        db = AsyncSurreal("ws://localhost:8000/rpc")
        try:
            # We add a small delay to ensure DB might be up if they started together
            # though usually the daemon should be running.
            await db.connect()
            await db.use("coretext", "coretext")
            
            schema_mapper = get_schema_mapper()
            embedder = get_vector_embedder(watchdog)
            
            manager = GraphManager(db, schema_mapper, embedder)
            service = MaintenanceService(manager)
            
            await service.run_self_healing()
        except Exception as e:
            logger.error(f"Startup maintenance failed: {e}")
        finally:
            await db.close()

    import asyncio
    # Fire and forget (non-blocking)
    asyncio.create_task(run_startup_maintenance())
    
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