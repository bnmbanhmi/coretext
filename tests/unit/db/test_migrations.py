# tests/unit/db/test_migrations.py
import pytest
from unittest.mock import AsyncMock, patch
from coretext.db.migrations import SchemaManager

@pytest.mark.asyncio
async def test_apply_schema(tmp_path):
    mock_db = AsyncMock()
    # Pass tmp_path as project_root
    manager = SchemaManager(mock_db, project_root=tmp_path)

    # Create a dummy schema_map.yaml so _load_schema_map doesn't fail or returns empty
    # We want it to return the dict that drives the test assertions
    # OR we can mock _load_schema_map
    
    with patch.object(SchemaManager, '_load_schema_map') as mock_load:
        # Define the schema map that corresponds to the assertions
        mock_load.return_value = {
            "node_types": {
                "file": {},
                "header": {}
            },
            "edge_types": {
                "contains": {
                    "db_table": "contains"
                },
                "parent_of": {
                    "db_table": "parent_of"
                }
            }
        }

        await manager.apply_schema()

    assert mock_db.query.called
    
    # Collect all queries executed
    queries = []
    for call_args in mock_db.query.call_args_list:
        queries.append(call_args[0][0]) # First arg is the query string
    
    combined_query = "\n".join(queries)

    assert "DEFINE TABLE node" in combined_query
    assert "DEFINE INDEX node_path ON TABLE node" in combined_query
    assert "DEFINE TABLE contains" in combined_query
    assert "DEFINE TABLE parent_of" in combined_query

@pytest.mark.asyncio
async def test_apply_schema_vector_search(tmp_path):
    """Test that vector search schema definitions are applied."""
    mock_db = AsyncMock()
    manager = SchemaManager(mock_db, project_root=tmp_path)

    with patch.object(SchemaManager, '_load_schema_map') as mock_load:
        mock_load.return_value = {} # Minimal schema map

        await manager.apply_schema()

    queries = [call_args[0][0] for call_args in mock_db.query.call_args_list]
    combined_query = "\n".join(queries)

    # These should be present per AC 4
    assert "DEFINE FIELD embedding ON node TYPE array<float>" in combined_query
    assert "DEFINE INDEX node_embedding_index ON node FIELDS embedding HNSW DIMENSION 768" in combined_query