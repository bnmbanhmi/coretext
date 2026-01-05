import pytest
from datetime import datetime
from coretext.core.graph.models import BaseNode, BaseEdge

def test_basenode_creation():
    node = BaseNode(id="file:///path/to/file.md", node_type="file", content="some content", metadata={"key": "value"})
    assert node.id == "file:///path/to/file.md"
    assert node.node_type == "file"
    assert node.content == "some content"
    assert node.metadata == {"key": "value"}
    assert isinstance(node.created_at, datetime)
    assert isinstance(node.updated_at, datetime)

def test_basenode_default_values():
    node = BaseNode(id="file:///path/to/file.md", node_type="file")
    assert node.content == ""
    assert node.metadata == {}

def test_basenode_validation_failure():
    with pytest.raises(Exception): # Pydantic ValidationError
        BaseNode(node_type="file") # Missing id

def test_baseedge_creation():
    edge = BaseEdge(id="edge_id_123", edge_type="contains", source="node_a", target="node_b", metadata={"weight": 1.0})
    assert edge.id == "edge_id_123"
    assert edge.edge_type == "contains"
    assert edge.source == "node_a"
    assert edge.target == "node_b"
    assert edge.metadata == {"weight": 1.0}
    assert isinstance(edge.created_at, datetime)
    assert isinstance(edge.updated_at, datetime)

def test_baseedge_default_values():
    edge = BaseEdge(id="edge_id_123", edge_type="contains", source="node_a", target="node_b")
    assert edge.metadata == {}

def test_baseedge_validation_failure():
    with pytest.raises(Exception): # Pydantic ValidationError
        BaseEdge(edge_type="contains", source="node_a", target="node_b") # Missing id
    with pytest.raises(Exception):
        BaseEdge(id="edge_id", source="node_a", target="node_b") # Missing edge_type
