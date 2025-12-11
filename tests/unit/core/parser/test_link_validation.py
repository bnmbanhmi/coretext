import re
import pytest
from pathlib import Path
from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.models import ParsingErrorNode, BaseEdge

@pytest.fixture
def parser(tmp_path: Path):
    return MarkdownParser(project_root=tmp_path)

@pytest.fixture
def create_md_file(tmp_path: Path):
    """Fixture to create a markdown file in the temporary directory."""
    def _create(filename: str, content: str = "") -> Path:
        file_path = tmp_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    return _create

def test_broken_link_generates_error(parser: MarkdownParser, create_md_file):
    """
    Test that an explicit link to a non-existent file generates a ParsingErrorNode.
    """
    md_content = "# Title\n[Broken Link](./does_not_exist_at_all.md)"
    file_path = create_md_file("temp_test_broken_link.md", md_content)
    
    nodes, edges = parser.parse(file_path)
    
    # Should have a ParsingErrorNode
    error_nodes = [n for n in nodes if isinstance(n, ParsingErrorNode)]
    assert len(error_nodes) == 1
    assert "Dangling Reference: Target './does_not_exist_at_all.md' does not exist." in error_nodes[0].error_message
    
    # Should NOT have a REFERENCES edge for this
    ref_edges = [e for e in edges if "does_not_exist_at_all.md" in e.target]
    assert len(ref_edges) == 0

def test_duplicate_links_have_unique_ids(parser: MarkdownParser, create_md_file):
    """
    Test that multiple links to the same target get unique Edge IDs.
    """
    # Create the target file within tmp_path
    target_file_path = create_md_file("valid_simple.md", "# Valid Simple Content")
    
    file_path = create_md_file("temp_test_dup_link.md", 
        f"# Title\n[Link 1](./valid_simple.md)\nSome text.\n[Link 2](./valid_simple.md)"
    )
    
    nodes, edges = parser.parse(file_path)
    
    # Find edges to valid_simple.md
    # Normalized path will be relative to tmp_path (parser.project_root)
    normalized_target_path = str(target_file_path.relative_to(parser.project_root))
    target_edges = [e for e in edges if normalized_target_path in e.target and e.edge_type == "REFERENCES"]
    assert len(target_edges) == 2
    
    # Verify IDs are unique
    ids = [e.id for e in target_edges]
    assert len(set(ids)) == 2
    
    # Verify IDs end with index (the counter in _process_link_token)
    # The actual suffix might vary based on the order of link processing,
    # but they should be unique integers. We'll check for the format.
    assert all(re.search(r'-\d+$', e.id) for e in target_edges)

