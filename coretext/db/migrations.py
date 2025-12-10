# coretext/db/migrations.py
import yaml
from pathlib import Path
from surrealdb import Surreal

class SchemaManager:
    def __init__(self, db_client: Surreal, project_root: Path):
        self.db = db_client
        self.project_root = project_root

    def _load_schema_map(self) -> dict:
        schema_path = self.project_root / ".coretext" / "schema_map.yaml"
        if not schema_path.exists():
            return {}
        with open(schema_path, "r") as f:
            return yaml.safe_load(f)

    async def apply_schema(self):
        schema_map = self._load_schema_map()
        
        # 1. Define Node Types (merged into 'node' table for graph simplicity)
        # We enforce a single 'node' table but allow differentiation via 'type' field
        await self.db.query("DEFINE TABLE node SCHEMAFULL")
        await self.db.query("DEFINE FIELD path ON TABLE node TYPE string ASSERT $value != NONE")
        await self.db.query("DEFINE INDEX node_path ON TABLE node COLUMNS path UNIQUE")
        # 'node_type' is the discriminator (e.g., 'file', 'header')
        await self.db.query("DEFINE FIELD node_type ON TABLE node TYPE string") 
        await self.db.query("DEFINE FIELD content ON TABLE node TYPE string")
        await self.db.query("DEFINE FIELD metadata ON TABLE node TYPE object")
        
        # Apply specific property definitions from YAML for nodes
        node_types = schema_map.get("node_types", {})
        for node_type_name, config in node_types.items():
            # Check if this node type maps to the 'node' table (it should)
            if config.get("db_table") == "node":
                properties = config.get("properties", {})
                for prop_name, prop_type_def in properties.items():
                    # Check if property is already defined (base fields)
                    if prop_name in ["path", "node_type", "content", "metadata"]:
                        continue

                    # Map Python/YAML types to SurrealDB types
                    surreal_type = "string" # default
                    if isinstance(prop_type_def, dict):
                         pt = prop_type_def.get("type", "str")
                    else:
                         pt = prop_type_def # assume string if just value, though yaml parses as dict usually if structured

                    if pt == "int": surreal_type = "int"
                    elif pt == "float": surreal_type = "float"
                    elif pt == "bool": surreal_type = "bool"
                    elif pt == "datetime": surreal_type = "datetime"
                    
                    await self.db.query(f"DEFINE FIELD {prop_name} ON TABLE node TYPE {surreal_type}")

        # 2. Define Edge Types
        edge_types = schema_map.get("edge_types", {})
        for edge_name, config in edge_types.items():
            db_table = config.get("db_table", edge_name)
            # FROM/TO constraints could be added if we had specific tables for each node type,
            # but since everything is 'node', we constrain relations FROM node TO node.
            await self.db.query(f"DEFINE TABLE {db_table} SCHEMAFULL TYPE RELATION FROM node TO node")
            
            # Define specific fields for the edge
            properties = config.get("properties", {})
            for prop_name, prop_type in properties.items():
                # Simple mapping: python type str -> surreal type
                surreal_type = "string"
                if isinstance(prop_type, dict):
                    pt = prop_type.get("type", "str")
                else:
                    pt = prop_type

                if pt == "int": surreal_type = "int"
                elif pt == "float": surreal_type = "float"
                elif pt == "bool": surreal_type = "bool"
                
                await self.db.query(f"DEFINE FIELD {prop_name} ON TABLE {db_table} TYPE {surreal_type}")
