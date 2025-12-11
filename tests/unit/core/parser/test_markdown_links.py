import pytest
from pathlib import Path
from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.models import FileNode, ParsingErrorNode, BaseEdge

@pytest.fixture
def parser(tmp_path):
    return MarkdownParser(project_root=tmp_path)

def test_extract_valid_link(parser, tmp_path):
    # Setup
    file_a = tmp_path / "file_a.md"
    file_b = tmp_path / "file_b.md"
    file_a.write_text("Link to [File B](./file_b.md)")
    file_b.write_text("# File B")

    # Execute
    nodes, edges = parser.parse(file_a)

    # Verify
    assert len(edges) >= 1
    # Find the REFERENCES edge
    ref_edges = [e for e in edges if e.edge_type == "REFERENCES"]
    assert len(ref_edges) == 1
    edge = ref_edges[0]
    assert edge.source == "file_a.md"
    assert edge.target == "file_b.md"

def test_extract_broken_link(parser, tmp_path):
    # Setup
    file_a = tmp_path / "file_a.md"
    file_a.write_text("Link to [Non Existent](./non_existent.md)")

    # Execute
    nodes, edges = parser.parse(file_a)

    # Verify
    # Should have a ParsingErrorNode
    error_nodes = [n for n in nodes if isinstance(n, ParsingErrorNode)]
    assert len(error_nodes) == 1
    assert "Dangling Reference" in error_nodes[0].error_message
    assert error_nodes[0].line_number == 1

def test_extract_implicit_link(parser, tmp_path):
    # Setup
    file_a = tmp_path / "file_a.md"
    file_c = tmp_path / "file_c.md"
    file_a.write_text("Check out file_c.md for more info.")
    file_c.write_text("# File C")

    # Execute
    nodes, edges = parser.parse(file_a)

    # Verify
    ref_edges = [e for e in edges if e.edge_type == "REFERENCES"]
    assert len(ref_edges) == 1
    assert ref_edges[0].target == "file_c.md"
