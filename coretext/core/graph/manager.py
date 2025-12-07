from typing import Type
from surrealdb import Surreal
from coretext.core.graph.models import BaseNode, BaseEdge
from datetime import datetime

class GraphManager:
    def __init__(self, db_client: Surreal):
        self.db = db_client

    async def create_node(self, node: BaseNode) -> BaseNode:
        node.created_at = datetime.utcnow()
        node.updated_at = datetime.utcnow()
        data = node.model_dump(mode='json')
        # SurrealDB uses `id` as part of the table name for records
        # e.g., `node:some_id`
        created_record = await self.db.create(f"{node.node_type}:{node.id}", data)
        return BaseNode.model_validate(created_record)

    async def get_node(self, node_id: str, node_model: Type[BaseNode] = BaseNode) -> BaseNode | None:
        # SurrealDB select returns a list of records
        fetched_record = await self.db.select(node_id)
        if fetched_record:
            return node_model.model_validate(fetched_record)
        return None

    async def update_node(self, node: BaseNode) -> BaseNode:
        node.updated_at = datetime.utcnow()
        data = node.model_dump(mode='json')
        updated_record = await self.db.update(node.id, data)
        return BaseNode.model_validate(updated_record)

    async def delete_node(self, node_id: str) -> None:
        await self.db.delete(node_id)
    
    async def create_edge(self, edge: BaseEdge) -> BaseEdge:
        edge.created_at = datetime.utcnow()
        edge.updated_at = datetime.utcnow()
        data = edge.model_dump(mode='json')
        # Map source/target to in/out for SurrealDB relations
        data["in"] = data.pop("source")
        data["out"] = data.pop("target")

        # SurrealDB automatically creates the relation table if it doesn't exist
        # and links records as `source_node_id->edge_type->target_node_id`
        created_record = await self.db.create(f"{edge.edge_type}:{edge.id}", data)
        # Need to map 'in' and 'out' back to 'source' and 'target' for the Pydantic model validation
        created_record['source'] = created_record.pop('in')
        created_record['target'] = created_record.pop('out')
        return BaseEdge.model_validate(created_record)

    async def get_edge(self, edge_id: str, edge_model: Type[BaseEdge] = BaseEdge) -> BaseEdge | None:
        fetched_record = await self.db.select(edge_id)
        if fetched_record:
            # Map 'in' and 'out' to 'source' and 'target' for Pydantic model
            fetched_record['source'] = fetched_record.pop('in')
            fetched_record['target'] = fetched_record.pop('out')
            return edge_model.model_validate(fetched_record)
        return None

    async def update_edge(self, edge: BaseEdge) -> BaseEdge:
        edge.updated_at = datetime.utcnow()
        data = edge.model_dump(mode='json')
        # Map source/target to in/out for SurrealDB relations
        data["in"] = data.pop("source")
        data["out"] = data.pop("target")

        updated_record = await self.db.update(edge.id, data)
        updated_record['source'] = updated_record.pop('in')
        updated_record['target'] = updated_record.pop('out')
        return BaseEdge.model_validate(updated_record)

    async def delete_edge(self, edge_id: str) -> None:
        await self.db.delete(edge_id)
