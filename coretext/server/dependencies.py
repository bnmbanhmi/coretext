from pathlib import Path
from fastapi import Depends
from surrealdb import AsyncSurreal
from coretext.core.parser.schema import SchemaMapper
from coretext.core.graph.manager import GraphManager
from coretext.core.vector.embedder import VectorEmbedder
from coretext.core.system.memory import MemoryWatchdog
from coretext.config import load_config

# Singletons to avoid reloading heavy resources on every request
_schema_mapper: SchemaMapper | None = None
_vector_embedder: VectorEmbedder | None = None
_memory_watchdog: MemoryWatchdog | None = None

async def get_db_client():
    """
    Dependency to provide a SurrealDB client connection.
    Connects to the local daemon at default port.
    """
    db = AsyncSurreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.use("coretext", "coretext")
    try:
        yield db
    finally:
        await db.close()

def get_schema_mapper() -> SchemaMapper:
    """
    Dependency to provide SchemaMapper.
    """
    global _schema_mapper
    if _schema_mapper is None:
        project_root = Path.cwd() 
        schema_map_path = project_root / ".coretext" / "schema_map.yaml"
        _schema_mapper = SchemaMapper(schema_map_path)
    return _schema_mapper

def get_memory_watchdog() -> MemoryWatchdog:
    """
    Dependency to provide MemoryWatchdog.
    """
    global _memory_watchdog
    if _memory_watchdog is None:
        config = load_config()
        _memory_watchdog = MemoryWatchdog(
            soft_limit_mb=config.system.memory_limit_mb,
            check_interval=60
        )
    return _memory_watchdog

def get_vector_embedder(
    watchdog: MemoryWatchdog = Depends(get_memory_watchdog)
) -> VectorEmbedder:
    """
    Dependency to provide VectorEmbedder.
    """
    global _vector_embedder
    if _vector_embedder is None:
        _vector_embedder = VectorEmbedder(memory_watchdog=watchdog)
    return _vector_embedder

async def get_graph_manager(
    db: AsyncSurreal = Depends(get_db_client),
    schema_mapper: SchemaMapper = Depends(get_schema_mapper),
    embedder: VectorEmbedder = Depends(get_vector_embedder)
) -> GraphManager:
    """
    Dependency to provide GraphManager instance.
    """
    return GraphManager(db, schema_mapper, embedder)
