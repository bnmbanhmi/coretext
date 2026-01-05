import pytest
import pytest_asyncio
import asyncio
import random
import uuid
import shutil
from pathlib import Path
from surrealdb import AsyncSurreal
from coretext.core.graph.manager import GraphManager
from coretext.core.graph.models import BaseNode, BaseEdge
from coretext.server.dependencies import get_schema_mapper
from coretext.db.client import SurrealDBClient

@pytest_asyncio.fixture
async def surreal_db(tmp_path):
    # Setup temp project
    project_root = tmp_path
    (project_root / ".coretext").mkdir()
    (project_root / ".coretext" / "config.yaml").write_text("daemon_port: 8005\nmcp_port: 8006")
    (project_root / ".coretext" / "schema_map.yaml").write_text("node_types: {}\\nedge_types: {}")
    
    # Locate binary
    # Client puts it in ~/.coretext/bin/surreal
    real_binary = Path.home() / ".coretext" / "bin" / "surreal"
    
    if not real_binary.exists():
        # Fallback to repo root check (maybe local dev setup)
        repo_root = Path.cwd()
        real_binary = repo_root / ".coretext" / "surreal"
    
    if not real_binary.exists():
        pytest.skip("SurrealDB binary not found. Run 'coretext init' first.")
        
    # Symlink or Copy binary
    target_binary = project_root / ".coretext" / "surreal"
    shutil.copy(real_binary, target_binary)
    target_binary.chmod(0o755)
    
    client = SurrealDBClient(project_root=project_root)
    try:
        await asyncio.wait_for(client.start_surreal_db(port=8005), timeout=10.0)
    except Exception as e:
        raise
    
    # Wait for DB to be up
    await asyncio.sleep(1)
    
    yield "ws://localhost:8005/rpc"
    
    await client.stop_surreal_db()

@pytest.mark.performance
@pytest.mark.asyncio
async def test_healing_at_scale(surreal_db):
    """
    Performance test for self-healing on a large graph (100+ nodes).
    Verifies that the system integrity is maintained when nodes are deleted.
    Note: SurrealDB automatically cascades deletes to edges in graph tables.
    So this test verifies that edges ARE removed, and that our manual prune tool 
    runs without error (even if it finds nothing to prune).
    """
    db_url = surreal_db
    db = AsyncSurreal(db_url)
    try:
        await db.connect()
        await db.use("coretext", "coretext")
    except Exception as e:
        pytest.fail(f"Failed to connect to test DB: {e}")

    prefix = f"scale_test_{uuid.uuid4().hex[:8]}"
    
    try:
        schema_mapper = get_schema_mapper()
        # Use None for embedder as we don't need embeddings for this test
        manager = GraphManager(db, schema_mapper, None)
        
        # 1. Generate Data (100 nodes, 300 edges)
        nodes = []
        edges = []
        
        node_ids = [f"file:{prefix}/node_{i}" for i in range(100)]
        
        for nid in node_ids:
            nodes.append(BaseNode(id=nid, node_type="file", content=f"Content for {nid}"))
            
        for i in range(300):
            src = random.choice(node_ids)
            tgt = random.choice(node_ids)
            edge_id = f"references:{prefix}/edge_{i}"
            edges.append(BaseEdge(id=edge_id, source=src, target=tgt, edge_type="references"))
            
        # Ingest in batches
        report = await manager.ingest(nodes, edges)
        assert report.success
        assert report.nodes_created == 100
        assert report.edges_created == 300
        
        # 2. Introduce Corruption (Delete nodes)
        nodes_to_delete = random.sample(node_ids, 20)
        
        for nid in nodes_to_delete:
            await db.delete(f"node:`{nid}`")
        
        # 3. Verify Graph Integrity (Auto-Healing)
        # Identify edges that SHOULD have been deleted
        edges_connected_to_deleted = [
            e for e in edges
            if e.source in nodes_to_delete or e.target in nodes_to_delete
        ]
        
        # Verify they are gone
        for edge in edges_connected_to_deleted:
             # Must check using proper ID format: table:`full_id`
             full_id = f"references:`{edge.id}`"
             exists = await manager.get_edge(full_id)
             assert exists is None, f"Edge {edge.id} linked to deleted node should have been auto-pruned"

        # 4. Run Manual Healing (Redundant but safety check)
        deleted_edges_count = await manager.prune_dangling_edges()
        
        # Should be 0 since DB did it
        assert deleted_edges_count == 0

        # 5. Verify Valid Edges Preserved
        valid_edges = [e for e in edges if e not in edges_connected_to_deleted]
        for edge in random.sample(valid_edges, min(len(valid_edges), 20)):
            full_id = f"references:`{edge.id}`"
            exists = await manager.get_edge(full_id)
            assert exists is not None, f"Valid edge {edge.id} should NOT have been pruned"
            
    finally:
        # Cleanup
        await db.query(f"DELETE node WHERE id CONTAINS '{prefix}';")
        await db.query(f"DELETE references WHERE id CONTAINS '{prefix}';")
        await db.close()