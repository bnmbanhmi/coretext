import pytest
from pathlib import Path
from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.models import ParsingErrorNode, BaseEdge

# Assume project root is the current working directory for tests
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent 
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "data"

@pytest.fixture
def parser():
    return MarkdownParser()

def test_broken_link_generates_error(parser, tmp_path):
    """
    Test that an explicit link to a non-existent file generates a ParsingErrorNode.
    """
    # Create a temporary markdown file in the test data dir logic
    # We use tmp_path but we need to ensure it's treated as within project root for normalization to work
    # ideally. But our normalization logic looks for pyproject.toml up the tree.
    # So we'll use a file in tests/data/ and ensure we clean it up.
    
    file_path = TEST_DATA_DIR / "temp_test_broken_link.md"
    file_path.write_text("# Title\n[Broken Link](./does_not_exist_at_all.md)")
    
    try:
        nodes, edges = parser.parse(file_path)
        
        # Should have a ParsingErrorNode
        error_nodes = [n for n in nodes if isinstance(n, ParsingErrorNode)]
        assert len(error_nodes) == 1
        assert "does_not_exist_at_all.md" in error_nodes[0].error_message
        
        # Should NOT have a REFERENCES edge for this
        ref_edges = [e for e in edges if "does_not_exist_at_all.md" in e.target]
        assert len(ref_edges) == 0
        
    finally:
        if file_path.exists():
            file_path.unlink()

def test_duplicate_links_have_unique_ids(parser):
    """
    Test that multiple links to the same target get unique Edge IDs.
    """
    # Use an existing target
    target_file = TEST_DATA_DIR / "valid_simple.md"
    assert target_file.exists()
    
    file_path = TEST_DATA_DIR / "temp_test_dup_link.md"
    # Create content with two links to same target
    content = f"# Title\n[Link 1](./valid_simple.md)\nSome text.\n[Link 2](./valid_simple.md)"
    file_path.write_text(content)
    
    try:
        nodes, edges = parser.parse(file_path)
        
        # Find edges to valid_simple.md
        target_edges = [e for e in edges if "valid_simple.md" in e.target]
        assert len(target_edges) == 2
        
        # Verify IDs are unique
        ids = [e.id for e in target_edges]
        assert len(set(ids)) == 2
        
        # Verify IDs end with index
        assert any(e.id.endswith("-1") for e in target_edges)
        assert any(e.id.endswith("-2") for e in target_edges)

    finally:
        if file_path.exists():
            file_path.unlink()
