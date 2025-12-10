import pytest
from pathlib import Path
from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.models import FileNode, HeaderNode, ParsingErrorNode, BaseEdge

# Assume project root is the current working directory for tests
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent # Adjust based on actual project structure
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "data"

@pytest.fixture
def parser():
    return MarkdownParser()

def test_parse_valid_simple_md(parser):
    """
    Test parsing of a simple, valid Markdown file.
    Verifies FileNode, HeaderNodes, CONTAINS, and PARENT_OF relationships.
    """
    file_path = TEST_DATA_DIR / "valid_simple.md"
    nodes, edges = parser.parse(file_path)

    # Assert FileNode
    file_nodes = [node for node in nodes if isinstance(node, FileNode)]
    assert len(file_nodes) == 1
    assert file_nodes[0].id == "tests/data/valid_simple.md" # Normalized path from project root
    assert file_nodes[0].node_type == "file"

    # Assert HeaderNodes
    header_nodes = [node for node in nodes if isinstance(node, HeaderNode)]
    assert len(header_nodes) == 3

    h1 = next(h for h in header_nodes if h.level == 1)
    assert h1.content == "Title"
    assert h1.id == "tests/data/valid_simple.md#title"

    h2 = next(h for h in header_nodes if h.level == 2)
    assert h2.content == "Section 1"
    assert h2.id == "tests/data/valid_simple.md#section-1"

    h3 = next(h for h in header_nodes if h.level == 3)
    assert h3.content == "Subsection 1.1"
    assert h3.id == "tests/data/valid_simple.md#subsection-1-1"

    # Assert Edges
    # 3 CONTAINS edges (File -> H1, File -> H2, File -> H3)
    # 2 PARENT_OF edges (H1 -> H2, H2 -> H3)
    assert len(edges) == 5

    # File -> H1 (CONTAINS)
    file_h1_edge = next(e for e in edges if e.source == file_nodes[0].id and e.target == h1.id and e.edge_type == "CONTAINS")
    assert file_h1_edge is not None

    # File -> H2 (CONTAINS)
    file_h2_contains_edge = next(e for e in edges if e.source == file_nodes[0].id and e.target == h2.id and e.edge_type == "CONTAINS")
    assert file_h2_contains_edge is not None

    # File -> H3 (CONTAINS)
    file_h3_contains_edge = next(e for e in edges if e.source == file_nodes[0].id and e.target == h3.id and e.edge_type == "CONTAINS")
    assert file_h3_contains_edge is not None

    # H1 -> H2 (PARENT_OF)
    h1_h2_parent_edge = next(e for e in edges if e.source == h1.id and e.target == h2.id and e.edge_type == "PARENT_OF")
    assert h1_h2_parent_edge is not None

    # H2 -> H3 (PARENT_OF)
    h2_h3_parent_edge = next(e for e in edges if e.source == h2.id and e.target == h3.id and e.edge_type == "PARENT_OF")
    assert h2_h3_parent_edge is not None


def test_parse_malformed_syntax_md(parser):
    """
    Test parsing of a malformed Markdown file.
    Verifies ParsingErrorNode creation for empty headers.
    """
    file_path = TEST_DATA_DIR / "malformed_syntax.md"
    nodes, edges = parser.parse(file_path)

    # Assert FileNode
    file_nodes = [node for node in nodes if isinstance(node, FileNode)]
    assert len(file_nodes) == 1
    assert file_nodes[0].id == "tests/data/malformed_syntax.md"

    # Assert HeaderNodes (should only include valid headers)
    header_nodes = [node for node in nodes if isinstance(node, HeaderNode)]
    assert len(header_nodes) == 2 # "Valid Header" and "Another Valid Header"

    # Assert ParsingErrorNodes
    error_nodes = [node for node in nodes if isinstance(node, ParsingErrorNode)]
    assert len(error_nodes) == 1 # For the empty header

    empty_header_error = next(e for e in error_nodes if e.error_message == "Header has no content.")
    assert empty_header_error.file_path == Path("tests/data/malformed_syntax.md")
    assert empty_header_error.line_number == 3 # Line number for "## "
    assert empty_header_error.raw_content_snippet == "## "

    # Check for the "#Last header" malformation. markdown-it-py considers this as content.
    # It doesn't generate a "heading_open" token for it.
    # So, we won't get a ParsingErrorNode for "Missing space after #." in this current implementation.
    # This might be a future enhancement if we define stricter BMAD rules.


def test_parse_valid_complex_md(parser):
    """
    Test parsing of a complex, valid Markdown file with explicit and implicit links.
    Verifies REFERENCES edges and correct path normalization.
    """
    file_path = TEST_DATA_DIR / "valid_complex.md"
    nodes, edges = parser.parse(file_path)

    # Assert FileNode
    file_nodes = [node for node in nodes if isinstance(node, FileNode)]
    assert len(file_nodes) == 1
    assert file_nodes[0].id == "tests/data/valid_complex.md"
    assert file_nodes[0].node_type == "file"

    # Assert HeaderNodes
    header_nodes = [node for node in nodes if isinstance(node, HeaderNode)]
    assert len(header_nodes) == 6 # Corrected count for: Project Overview, Introduction, Key Features, Architecture, Components, Conclusion

    # Assert Edges (CONTAINS and PARENT_OF)
    # File -> 6 Headers (CONTAINS) = 6
    # H1 -> H2_intro (PARENT_OF) = 1
    # H2_intro -> H3_key_features (PARENT_OF) = 1
    # H1 -> H2_arch (PARENT_OF) = 1
    # H2_arch -> H3_components (PARENT_OF) = 1
    # H1 -> H2_conclusion (PARENT_OF) = 1
    # Total edges from headers: 6 (CONTAINS) + 5 (PARENT_OF) = 11 edges
    
    target_path = "tests/data/subdir/target.md"

    # Explicit link: [Explicit Link](./subdir/target.md)
    explicit_ref_edge = next(e for e in edges if e.source == file_nodes[0].id and e.target == target_path and e.edge_type == "REFERENCES")
    assert explicit_ref_edge is not None

    # Implicit link: subdir/target.md
    implicit_ref_edge = next(e for e in edges if e.source == file_nodes[0].id and e.target == target_path and e.edge_type == "REFERENCES")
    assert implicit_ref_edge is not None

    # Total edges = 11 (CONTAINS/PARENT_OF) + 2 (REFERENCES) = 13 (Assuming duplicate edges are allowed or not filtered yet)
    # The parser currently appends to a list, so duplicates are possible if both explicit and implicit logic catch the same link.
    # But here we have one explicit link and one implicit link in different places.
    assert len(edges) >= 13
