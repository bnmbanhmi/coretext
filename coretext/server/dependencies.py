from pathlib import Path
from fastapi import Depends
from surrealdb import AsyncSurreal
from coretext.core.parser.schema import SchemaMapper
from coretext.core.graph.manager import GraphManager

from coretext.core.vector.embedder import VectorEmbedder

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
    Assumes current working directory is the project root.
    """
    project_root = Path.cwd() 
    schema_map_path = project_root / ".coretext" / "schema_map.yaml"
    # Fallback/Default handling could be added here if needed
    return SchemaMapper(schema_map_path)

def get_vector_embedder() -> VectorEmbedder:
    """
    Dependency to provide VectorEmbedder.
    Uses default cache location.
    """
    return VectorEmbedder()

async def get_graph_manager(
    db: AsyncSurreal = Depends(get_db_client),
    schema_mapper: SchemaMapper = Depends(get_schema_mapper),
    embedder: VectorEmbedder = Depends(get_vector_embedder)
) -> GraphManager:
    """
    Dependency to provide GraphManager instance.
    """
    return GraphManager(db, schema_mapper, embedder)
