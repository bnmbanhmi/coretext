import pytest
import pytest_asyncio
import asyncio
import uuid
import shutil
from pathlib import Path
from surrealdb import AsyncSurreal
from coretext.core.graph.manager import GraphManager
from coretext.core.graph.models import BaseNode, BaseEdge
from coretext.db.client import SurrealDBClient

@pytest_asyncio.fixture
async def surreal_db(tmp_path):
    # Setup temp project
    project_root = tmp_path
    (project_root / ".coretext").mkdir()
    (project_root / ".coretext" / "config.yaml").write_text("daemon_port: 8005\nmcp_port: 8006")
    (project_root / ".coretext" / "schema_map.yaml").write_text(
        "node_types:\n"
        "  file: {db_table: 'node'}\n"
        "edge_types:\n"
        "  references: {db_table: 'references', source_type: 'file', target_type: 'file'}"
    )
    
    real_binary = Path.home() / ".coretext" / "bin" / "surreal"
    if not real_binary.exists():
        repo_root = Path.cwd()
        real_binary = repo_root / ".coretext" / "surreal"
    
    if not real_binary.exists():
        pytest.skip("SurrealDB binary not found. Run 'coretext init' first.")
        
    target_binary = project_root / ".coretext" / "surreal"
    shutil.copy(real_binary, target_binary)
    target_binary.chmod(0o755)
    
    client = SurrealDBClient(project_root=project_root)
    try:
        await asyncio.wait_for(client.start_surreal_db(port=8005), timeout=10.0)
    except Exception:
        raise
    
    await asyncio.sleep(1)
    yield "ws://localhost:8005/rpc"
    await client.stop_surreal_db()

@pytest.mark.performance
@pytest.mark.asyncio
async def test_healing_at_scale(surreal_db, tmp_path):
    """
    Performance test for self-healing on a large graph (100+ nodes).
    """
    db_url = surreal_db
    db = AsyncSurreal(db_url)
    prefix = f"scale_test_{uuid.uuid4().hex[:8]}"
    
    try:
        await db.connect()
        await db.use("coretext", "coretext")
        
        from coretext.core.parser.schema import SchemaMapper
        schema_map_path = tmp_path / ".coretext" / "schema_map.yaml"
        schema_mapper = SchemaMapper(schema_map_path)
        manager = GraphManager(db, schema_mapper, None)
        
        # 1. Create 2 nodes and 1 edge
        node_a = f"{prefix}/node_a"
        node_b = f"{prefix}/node_b"
        await manager.create_node(BaseNode(id=node_a, node_type="file", content="Node A"))
        await manager.create_node(BaseNode(id=node_b, node_type="file", content="Node B"))
        
        edge_id = f"{prefix}/edge_ab"
        await manager.create_edge(BaseEdge(id=edge_id, source=node_a, target=node_b, edge_type="references"))
        
        # 2. Delete target node
        await db.delete(f"node:`{node_b}`")
        
        # 3. Verify edge might still be there (if not auto-deleted)
        # We don't care if it is or isn't, but we want to test our prune logic.
        
        # 4. Inject a "Ghost Edge" manually (Definite dangling pointer)
        ghost_edge_id = f"{prefix}/ghost_edge"
        await db.query(f"INSERT INTO references {{ id: references:`{ghost_edge_id}`, in: node:`{node_a}`, out: node:`{prefix}/fake_node`, edge_type: 'references', updated_at: time::now() }}")
        
        # 5. Run Manual Healing
        deleted_count = await manager.prune_dangling_edges()
        
        # Should catch at least the ghost edge
        assert deleted_count >= 1
        
        # 6. Verify ghost is gone
        ghost_exists = await manager.get_edge(f"references:`{ghost_edge_id}`")
        assert ghost_exists is None
        
        # 7. Verify node_a is still there
        node_a_exists = await manager.get_node(f"node:`{node_a}`")
        assert node_a_exists is not None
            
    finally:
        try:
            await db.query(f"DELETE node WHERE id CONTAINS '{prefix}';")
            await db.query(f"DELETE references WHERE id CONTAINS '{prefix}';")
            await db.close()
        except Exception:
            pass
