# tests/unit/db/test_migrations.py
import pytest
from unittest.mock import AsyncMock, MagicMock, call
from coretext.db.migrations import SchemaManager

@pytest.mark.asyncio
async def test_apply_schema():
    mock_db = AsyncMock()
    manager = SchemaManager(mock_db)

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
