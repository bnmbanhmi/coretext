import pytest
from pathlib import Path
from coretext.core.parser.markdown import MarkdownParser
from coretext.core.graph.models import FileNode, HeaderNode, ParsingErrorNode, BaseEdge

# Assume project root is the current working directory for tests
# PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent # Adjust based on actual project structure
# TEST_DATA_DIR = PROJECT_ROOT / "tests" / "data"

@pytest.fixture
def parser(tmp_path: Path):
    return MarkdownParser(project_root=tmp_path)

@pytest.fixture
def create_md_file(tmp_path: Path):
    def _create(filename: str, content: str):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path
    return _create

def test_parse_valid_simple_md(parser: MarkdownParser, create_md_file):
    md_content = "# Hello World"
    # Create the test data directory within tmp_path to simulate project structure
    test_data_dir = parser.project_root / "tests" / "data"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    file_path = test_data_dir / "valid_simple.md"
    file_path.write_text(md_content) # Use create_md_file for creating file content

    nodes, edges = parser.parse(file_path)

    # Assert FileNode
    file_nodes = [node for node in nodes if isinstance(node, FileNode)]
    assert len(file_nodes) == 1
    assert file_nodes[0].id == str(file_path.relative_to(parser.project_root)) # Normalized path from project root
    assert file_nodes[0].node_type == "file"

    # Assert HeaderNodes
    header_nodes = [node for node in nodes if isinstance(node, HeaderNode)]
    assert len(header_nodes) == 1

    h1 = next(h for h in header_nodes if h.level == 1)
    assert h1.content == "Hello World"
    assert h1.id == str(file_path.relative_to(parser.project_root)) + "#hello-world"

    # Assert Edges
    # 1 CONTAINS edge (File -> H1)
    assert len(edges) == 1

    # File -> H1 (CONTAINS)
    file_h1_edge = next(e for e in edges if e.source == file_nodes[0].id and e.target == h1.id and e.edge_type == "CONTAINS")
    assert file_h1_edge is not None


def test_parse_malformed_syntax_md(parser: MarkdownParser, create_md_file):
    md_content = "# Header\n## \n# Another Valid Header"
    # Create the test data directory within tmp_path to simulate project structure
    test_data_dir = parser.project_root / "tests" / "data"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    file_path = test_data_dir / "malformed_syntax.md"
    file_path.write_text(md_content) # Use create_md_file for creating file content

    nodes, edges = parser.parse(file_path)

    # Assert FileNode
    file_nodes = [node for node in nodes if isinstance(node, FileNode)]
    assert len(file_nodes) == 1
    assert file_nodes[0].id == str(file_path.relative_to(parser.project_root))

    # Assert HeaderNodes (should only include valid headers)
    header_nodes = [node for node in nodes if isinstance(node, HeaderNode)]
    assert len(header_nodes) == 2 # "Header" and "Another Valid Header"

    # Assert ParsingErrorNodes
    error_nodes = [node for node in nodes if isinstance(node, ParsingErrorNode)]
    assert len(error_nodes) == 1 # For the empty header

    empty_header_error = next(e for e in error_nodes if e.error_message == "Header has no content.")
    assert empty_header_error.file_path == Path(str(file_path.relative_to(parser.project_root)))
    assert empty_header_error.line_number == 2 # Line number for "## "
    assert empty_header_error.raw_content_snippet == "## "


def test_parse_valid_complex_md(parser: MarkdownParser, create_md_file):
    md_content = """
# Project Overview
## Introduction
### Key Features
## Architecture
### Components
## Conclusion

[Explicit Link](./subdir/target.md)

Implicit Link: subdir/target.md
"""
    # Create the test data directory within tmp_path to simulate project structure
    test_data_dir = parser.project_root / "tests" / "data"
    test_data_dir.mkdir(parents=True, exist_ok=True)
    (test_data_dir / "subdir").mkdir()
    (test_data_dir / "subdir" / "target.md").write_text("target content")

    file_path = test_data_dir / "valid_complex.md"
    file_path.write_text(md_content)

    nodes, edges = parser.parse(file_path)

    # Assert FileNode
    file_nodes = [node for node in nodes if isinstance(node, FileNode)]
    assert len(file_nodes) == 1
    assert file_nodes[0].id == str(file_path.relative_to(parser.project_root))
    assert file_nodes[0].node_type == "file"

    # Assert HeaderNodes
    header_nodes = [node for node in nodes if isinstance(node, HeaderNode)]
    assert len(header_nodes) == 6 # Project Overview, Introduction, Key Features, Architecture, Components, Conclusion

    # Assert Edges (CONTAINS and PARENT_OF)
    # File -> 6 Headers (CONTAINS) = 6
    # Project Overview -> Introduction (PARENT_OF)
    # Introduction -> Key Features (PARENT_OF)
    # Project Overview -> Architecture (PARENT_OF)
    # Architecture -> Components (PARENT_OF)
    # Project Overview -> Conclusion (PARENT_OF)
    # Total PARENT_OF = 5
    # Total CONTAINS = 6
    # Total Header related edges = 11

    target_path = "tests/data/subdir/target.md"

    # Explicit link: [Explicit Link](./subdir/target.md)
    explicit_ref_edge = next(e for e in edges if e.source == file_nodes[0].id and e.target == target_path and e.edge_type == "REFERENCES")
    assert explicit_ref_edge is not None

    # Implicit link: subdir/target.md
    implicit_ref_edge = next(e for e in edges if e.source == file_nodes[0].id and e.target == target_path and e.edge_type == "REFERENCES")
    assert implicit_ref_edge is not None
    
    # Total edges = 11 (CONTAINS/PARENT_OF) + 2 (REFERENCES) = 13
    assert len(edges) == 13

    # Add a test for malformed link
def test_malformed_link_in_complex_md(parser: MarkdownParser, create_md_file):
    md_content = """
# Title
[Broken File Link](./non_existent_file.md)
"""
    test_data_dir = parser.project_root / "tests" / "data"
    test_data_dir.mkdir(parents=True, exist_ok=True)
    file_path = test_data_dir / "malformed_link.md"
    file_path.write_text(md_content)

    nodes, edges = parser.parse(file_path)

    assert any(isinstance(node, ParsingErrorNode) for node in nodes)
    error_node = next(node for node in nodes if isinstance(node, ParsingErrorNode))
    assert "Broken link: Target './non_existent_file.md' does not exist." in error_node.error_message

