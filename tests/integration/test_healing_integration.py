import pytest
from surrealdb import AsyncSurreal
from coretext.core.graph.manager import GraphManager
from coretext.core.graph.models import BaseNode, BaseEdge
from coretext.server.dependencies import get_schema_mapper # leveraging dependency logic if possible

# Helper to get graph manager with real DB
async def get_real_graph_manager(db):
    schema_mapper = get_schema_mapper()
    # Mock embedder or use real one if available (might fail without watchdog)
    # Use None for embedder as healing doesn't need it
    return GraphManager(db, schema_mapper, None)

@pytest.mark.asyncio
async def test_healing_dangling_edges():
    """
    Integration test for dangling edge cleanup.
    Requires running SurrealDB at localhost:8000.
    """
    db = AsyncSurreal("ws://localhost:8000/rpc")
    try:
        await db.connect()
        await db.use("coretext", "coretext")
    except Exception:
        pytest.skip("SurrealDB not running at localhost:8000")
        return

    try:
        manager = await get_real_graph_manager(db)

        # 1. Create Nodes
        node_a = BaseNode(id="file:test/a", node_type="file", content="A")
        node_b = BaseNode(id="file:test/b", node_type="file", content="B")
        
        await manager.create_node(node_a)
        await manager.create_node(node_b)
        
        # 2. Create Edge
        edge = BaseEdge(source="file:test/a", target="file:test/b", edge_type="references", id="references:test_a_b")
        await manager.create_edge(edge)
        
        # Verify edge exists
        stored_edge = await manager.get_edge("references:test_a_b")
        assert stored_edge is not None
        
        # 3. Create Dangling Edge Situation
        # Manually delete node B (target) without removing edge
        # Using DB directly to bypass any potential GraphManager cascading logic (if it existed)
        await db.delete("node:`file:test/b`")
        
        # Verify node B is gone
        stored_b = await manager.get_node("file:test/b")
        assert stored_b is None
        
        # Verify edge still exists (it should be dangling now)
        # Note: SurrealDB might auto-cleanup if cascading is set, but we assume it's not
        stored_edge_check = await manager.get_edge("references:test_a_b")
        # If it's already gone, then our healing isn't needed (or DB does it)
        # But we assume we need to prune.
        
        # 4. Run Healing
        deleted_count = await manager.prune_dangling_edges()
        
        # 5. Assert
        # If DB auto-cleaned, count might be 0. If not, should be 1.
        # Check if edge is gone from DB
        stored_edge_final = await manager.get_edge("references:test_a_b")
        assert stored_edge_final is None
        
        # If edge existed before prune, count should be >= 1
        if stored_edge_check is not None:
             assert deleted_count >= 1

    finally:
        # Cleanup
        await db.delete("node:`file:test/a`")
        await db.delete("node:`file:test/b`") # Should be already gone
        await db.delete("references:test_a_b")
        await db.close()
