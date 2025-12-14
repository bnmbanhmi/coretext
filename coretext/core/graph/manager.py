from typing import Type, List
from surrealdb import Surreal
from coretext.core.graph.models import BaseNode, BaseEdge, ParsingErrorNode, SyncReport
from coretext.core.parser.schema import SchemaMapper
from datetime import datetime

class GraphManager:
    def __init__(self, db_client: Surreal, schema_mapper: SchemaMapper):
        self.db = db_client
        self.schema_mapper = schema_mapper

    async def create_node(self, node: BaseNode) -> BaseNode:
        node.created_at = datetime.utcnow()
        node.updated_at = datetime.utcnow()
        data = node.model_dump(mode='json')
        
        table = self.schema_mapper.get_node_table(node.node_type)
        # Use table from schema map (e.g., 'node')
        created_record = await self.db.create(f"{table}:⟨{node.id}⟩", data)
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
        
        table = self.schema_mapper.get_node_table(node.node_type)
        updated_record = await self.db.update(f"{table}:⟨{node.id}⟩", data)
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

        table = self.schema_mapper.get_edge_table(edge.edge_type)
        # SurrealDB automatically creates the relation table if it doesn't exist
        created_record = await self.db.create(f"{table}:⟨{edge.id}⟩", data)
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

        table = self.schema_mapper.get_edge_table(edge.edge_type)
        updated_record = await self.db.update(f"{table}:⟨{edge.id}⟩", data)
        updated_record['source'] = updated_record.pop('in')
        updated_record['target'] = updated_record.pop('out')
        return BaseEdge.model_validate(updated_record)

    async def delete_edge(self, edge_id: str) -> None:
        await self.db.delete(edge_id)

    async def ingest(self, nodes: List[BaseNode], edges: List[BaseEdge], batch_size: int = 100) -> SyncReport:
        """
        Ingests a list of nodes and edges into the graph database using batched transactions.
        If any ParsingErrorNode is present, the ingestion is rejected.

        Args:
            nodes (List[BaseNode]): A list of nodes to ingest.
            edges (List[BaseEdge]): A list of edges to ingest.
            batch_size (int): Number of operations per transaction batch.

        Returns:
            SyncReport: A report detailing the outcome of the ingestion.
        """
        parsing_errors = [node for node in nodes if isinstance(node, ParsingErrorNode)]
        if parsing_errors:
            return SyncReport(
                success=False,
                message=f"Ingestion rejected due to {len(parsing_errors)} parsing errors.",
                parsing_errors=parsing_errors
            )

        nodes_created = 0
        edges_created = 0

        # Process Nodes in batches
        for i in range(0, len(nodes), batch_size):
            batch_nodes = nodes[i:i + batch_size]
            transaction_query = "BEGIN TRANSACTION;\n"
            params = {}
            
            for idx, node in enumerate(batch_nodes):
                node.updated_at = datetime.utcnow()
                data = node.model_dump(mode='json')
                param_name = f"node_{i}_{idx}"
                params[param_name] = data
                
                table = self.schema_mapper.get_node_table(node.node_type)
                # Using UPDATE (upsert behavior)
                transaction_query += f"UPDATE {table}:⟨{node.id}⟩ CONTENT ${param_name};\n"
            
            transaction_query += "COMMIT TRANSACTION;"
            await self.db.query(transaction_query, params)
            nodes_created += len(batch_nodes)

        # Process Edges in batches
        for i in range(0, len(edges), batch_size):
            batch_edges = edges[i:i + batch_size]
            transaction_query = "BEGIN TRANSACTION;\n"
            params = {}

            for idx, edge in enumerate(batch_edges):
                edge.updated_at = datetime.utcnow()
                data = edge.model_dump(mode='json')
                # Map source/target to in/out
                data["in"] = data.pop("source")
                data["out"] = data.pop("target")
                
                param_name = f"edge_{i}_{idx}"
                params[param_name] = data
                
                table = self.schema_mapper.get_edge_table(edge.edge_type)
                transaction_query += f"UPDATE {table}:⟨{edge.id}⟩ CONTENT ${param_name};\n"

            transaction_query += "COMMIT TRANSACTION;"
            await self.db.query(transaction_query, params)
            edges_created += len(batch_edges)
        
        return SyncReport(
            success=True,
            message="Nodes and edges ingested successfully.",
            nodes_created=nodes_created,
            edges_created=edges_created
        )
