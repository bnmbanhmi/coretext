from pathlib import Path
from fastapi import Depends
from surrealdb import AsyncSurreal
from coretext.core.parser.schema import SchemaMapper
from coretext.core.graph.manager import GraphManager
from coretext.core.vector.embedder import VectorEmbedder

# Singletons to avoid reloading heavy resources on every request
_schema_mapper: SchemaMapper | None = None
_vector_embedder: VectorEmbedder | None = None

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

def get_vector_embedder() -> VectorEmbedder:
    """
    Dependency to provide VectorEmbedder.
    """
    global _vector_embedder
    if _vector_embedder is None:
        _vector_embedder = VectorEmbedder()
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
