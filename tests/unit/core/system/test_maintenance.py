import pytest
from unittest.mock import AsyncMock, MagicMock
from coretext.core.system.maintenance import MaintenanceService
from coretext.core.graph.manager import GraphManager

@pytest.mark.asyncio
async def test_maintenance_routine_calls_pruning():
    mock_graph_manager = AsyncMock(spec=GraphManager)
    # Mock return values
    mock_graph_manager.prune_dangling_edges.return_value = 5
    mock_graph_manager.prune_orphan_headers.return_value = 2

    service = MaintenanceService(mock_graph_manager)
    
    # Act - Should fail with NotImplementedError initially
    report = await service.run_self_healing()

    # Assertions
    mock_graph_manager.prune_dangling_edges.assert_awaited_once()
    mock_graph_manager.prune_orphan_headers.assert_awaited_once()
    
    assert report["dangling_edges_removed"] == 5
    assert report["orphan_headers_removed"] == 2