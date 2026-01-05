from pathlib import Path
from pydantic import BaseModel, Field
import yaml

class PropertySchema(BaseModel):
    # For now, just a string type. Can be extended to include more validation.
    type: str

class NodeTypeSchema(BaseModel):
    db_table: str
    properties: dict[str, PropertySchema] = Field(default_factory=dict)

class EdgeTypeSchema(BaseModel):
    db_table: str
    source_type: str
    target_type: str
    properties: dict[str, PropertySchema] = Field(default_factory=dict)

class SchemaMap(BaseModel):
    node_types: dict[str, NodeTypeSchema] = Field(default_factory=dict)
    edge_types: dict[str, EdgeTypeSchema] = Field(default_factory=dict)

DEFAULT_SCHEMA_MAP_CONTENT = """
node_types:
  file:
    db_table: node
    properties:
      path:
        type: str
      title:
        type: str
      summary:
        type: str
      content:
        type: str
      commit_hash:
        type: str
      created_at:
        type: datetime
      updated_at:
        type: datetime
  header:
    db_table: node
    properties:
      path:
        type: str
      level:
        type: int
      title:
        type: str
      content:
        type: str
      content_hash:
        type: str
      commit_hash:
        type: str
      created_at:
        type: datetime
      updated_at:
        type: datetime
  
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
  references:
    db_table: references
    source_type: file
    target_type: file
    properties: {}

"""

class SchemaMapper:
    def __init__(self, schema_map_path: Path):
        self.schema_map_path = schema_map_path
        self._schema_map: SchemaMap | None = None

    def load_schema(self) -> SchemaMap:
        if not self.schema_map_path.exists():
            raise FileNotFoundError(f"Schema map file not found: {self.schema_map_path}")
        
        with open(self.schema_map_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self._schema_map = SchemaMap.model_validate(data)
        return self._schema_map
    
    @property
    def schema_map(self) -> SchemaMap:
        if self._schema_map is None:
            self.load_schema()
        return self._schema_map

    def get_node_table(self, node_type: str) -> str:
        return self.schema_map.node_types[node_type].db_table

    def get_edge_table(self, edge_type: str) -> str:
        return self.schema_map.edge_types[edge_type].db_table
