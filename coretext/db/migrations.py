# coretext/db/migrations.py
from surrealdb import Surreal

class SchemaManager:
    def __init__(self, db_client: Surreal):
        self.db = db_client

    async def apply_schema(self):
        # Define Node Table
        await self.db.query("DEFINE TABLE node SCHEMAFULL")
        await self.db.query("DEFINE FIELD path ON TABLE node TYPE string ASSERT $value != NONE")
        await self.db.query("DEFINE INDEX node_path ON TABLE node COLUMNS path UNIQUE")
        await self.db.query("DEFINE FIELD type ON TABLE node TYPE string") # e.g., 'file', 'header'
        await self.db.query("DEFINE FIELD content ON TABLE node TYPE string")
        await self.db.query("DEFINE FIELD metadata ON TABLE node TYPE object")

        # Define Edges
        # CONTAINS: File -> Header
        await self.db.query("DEFINE TABLE contains SCHEMAFULL TYPE RELATION FROM node TO node")
        
        # PARENT_OF: H1 -> H2
        await self.db.query("DEFINE TABLE parent_of SCHEMAFULL TYPE RELATION FROM node TO node")
