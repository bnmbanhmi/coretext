import pytest
from unittest.mock import AsyncMock, MagicMock
from coretext.server.mcp.routes import get_dependencies, GetDependenciesRequest

@pytest.mark.asyncio
async def test_get_dependencies_normalizes_paths():
    """Verify that relative paths like ./docs/prd.md are normalized to docs/prd.md."""
    
    # Mock dependencies
    mock_graph_manager = AsyncMock()
    mock_graph_manager.get_dependencies.return_value = []
    
    mock_schema_mapper = MagicMock()
    mock_schema_mapper.get_node_table.return_value = "file"
    
    # Test case 1: User provides relative path with dot
    request = GetDependenciesRequest(node_identifier="./docs/prd.md", depth=1)
    
    await get_dependencies(request, mock_graph_manager, mock_schema_mapper)
    
    # Expectation: The ID passed to graph_manager should be normalized
    # It should be file:`docs/prd.md`, NOT file:`./docs/prd.md`
    mock_graph_manager.get_dependencies.assert_called_with("file:`docs/prd.md`", depth=1)

@pytest.mark.asyncio
async def test_get_dependencies_simple_filename():
    """Verify that simple filenames like README.md are handled correctly."""
    
    mock_graph_manager = AsyncMock()
    mock_graph_manager.get_dependencies.return_value = []
    
    mock_schema_mapper = MagicMock()
    mock_schema_mapper.get_node_table.return_value = "file"
    
    request = GetDependenciesRequest(node_identifier="README.md", depth=1)
    
    await get_dependencies(request, mock_graph_manager, mock_schema_mapper)
    
    mock_graph_manager.get_dependencies.assert_called_with("file:`README.md`", depth=1)
