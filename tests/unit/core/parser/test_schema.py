import pytest
from pathlib import Path
import yaml
from coretext.core.parser.schema import SchemaMapper, SchemaMap, NodeTypeSchema, EdgeTypeSchema, PropertySchema

@pytest.fixture
def temp_schema_map_file(tmp_path: Path):
    schema_content = """
node_types:
  file:
    db_table: node
    properties:
      path:
        type: str
      title:
        type: str
  header:
    db_table: node
    properties:
      path:
        type: str
      level:
        type: int

edge_types:
  contains:
    db_table: contains
    source_type: file
    target_type: header
    properties:
      order:
        type: int
  parent_of:
    db_table: parent_of
    source_type: header
    target_type: header
    properties: {}
"""
    schema_path = tmp_path / ".coretext" / "schema_map.yaml"
    schema_path.parent.mkdir(exist_ok=True)
    schema_path.write_text(schema_content)
    return schema_path

def test_load_schema_success(temp_schema_map_file: Path):
    mapper = SchemaMapper(temp_schema_map_file)
    schema_map = mapper.load_schema()

    assert isinstance(schema_map, SchemaMap)
    assert "file" in schema_map.node_types
    assert "header" in schema_map.node_types
    assert "contains" in schema_map.edge_types
    assert "parent_of" in schema_map.edge_types

    file_node = schema_map.node_types["file"]
    assert isinstance(file_node, NodeTypeSchema)
    assert file_node.db_table == "node"
    assert "path" in file_node.properties
    assert file_node.properties["path"].type == "str"

    contains_edge = schema_map.edge_types["contains"]
    assert isinstance(contains_edge, EdgeTypeSchema)
    assert contains_edge.db_table == "contains"
    assert contains_edge.source_type == "file"
    assert contains_edge.target_type == "header"
    assert "order" in contains_edge.properties
    assert contains_edge.properties["order"].type == "int"

def test_load_schema_file_not_found(tmp_path: Path):
    non_existent_path = tmp_path / "non_existent.yaml"
    mapper = SchemaMapper(non_existent_path)
    with pytest.raises(FileNotFoundError, match=f"Schema map file not found: {non_existent_path}"):
        mapper.load_schema()

def test_schema_map_property(temp_schema_map_file: Path):
    mapper = SchemaMapper(temp_schema_map_file)
    # Accessing property should trigger load_schema
    schema_map = mapper.schema_map
    assert isinstance(schema_map, SchemaMap)
    assert mapper._schema_map is not None # Should be loaded
