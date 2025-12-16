from typing import Type, List
from surrealdb import Surreal
from coretext.core.graph.models import BaseNode, BaseEdge, ParsingErrorNode, SyncReport
from coretext.core.parser.schema import SchemaMapper
from datetime import datetime

class GraphManager:
    def __init__(self, db_client: Surreal, schema_mapper: SchemaMapper):
        self.db = db_client
        self.schema_mapper = schema_mapper

    def _get_relation_id(self, node_id: str, node_type: str) -> str:
        table = self.schema_mapper.get_node_table(node_type)
        return f"{table}:`{node_id}`"

    def _prepare_edge_data(self, edge: BaseEdge) -> dict:
        data = edge.model_dump(mode='json')
        
        # Get schema definition for this edge type
        edge_def = self.schema_mapper.schema_map.edge_types.get(edge.edge_type)
        if not edge_def:
            # Fallback if unknown type (shouldn't happen with valid schema)
            # Assume 'node' table as default
            source_table = "node"
            target_table = "node"
        else:
            source_type = edge_def.source_type
            target_type = edge_def.target_type
            source_table = self.schema_mapper.get_node_table(source_type)
            target_table = self.schema_mapper.get_node_table(target_type)

        # Store lookup info for RELATE query construction
        data["_source_rec"] = f"{source_table}:`{edge.source}`"
        data["_target_rec"] = f"{target_table}:`{edge.target}`"
        
        # Ensure ID is backticked for safety if it contains special chars
        # But we pass the raw ID string to SurrealDB inside the content object?
        # No, we pass `id` field.
        data["id"] = f"`{edge.id}`"
        
        # Remove source/target/in/out from data payload if they exist to avoid confusion,
        # although RELATE handles in/out automatically.
        data.pop("source", None)
        data.pop("target", None)
        data.pop("in", None)
        data.pop("out", None)

        # Hotfix for 'contains' edges requiring 'order'
        if edge.edge_type == "contains" and "order" not in data:
            data["order"] = 0
        
        return data

    async def create_node(self, node: BaseNode) -> BaseNode:
        node.created_at = datetime.utcnow()
        node.updated_at = datetime.utcnow()
        data = node.model_dump(mode='json')
        
        table = self.schema_mapper.get_node_table(node.node_type)
        # Use table from schema map (e.g., 'node')
        created_record = await self.db.create(f"{table}:`{node.id}`", data)
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
        updated_record = await self.db.update(f"{table}:`{node.id}`", data)
        return BaseNode.model_validate(updated_record)

    async def delete_node(self, node_id: str) -> None:
        await self.db.delete(node_id)
    
    async def create_edge(self, edge: BaseEdge) -> BaseEdge:
        edge.created_at = datetime.utcnow()
        edge.updated_at = datetime.utcnow()
        
        data = self._prepare_edge_data(edge)
        table = self.schema_mapper.get_edge_table(edge.edge_type)
        
        in_rec = data.pop("_source_rec")
        out_rec = data.pop("_target_rec")
        
        # RELATE query
        query = f"RELATE {in_rec} -> {table} -> {out_rec} CONTENT $data RETURN AFTER;"
        
        results = await self.db.query(query, {"data": data})
        created_record = results[0] if results else {}
        
        # Map back
        created_record['source'] = created_record.get('in', '')
        created_record['target'] = created_record.get('out', '')
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
        
        data = self._prepare_edge_data(edge)
        table = self.schema_mapper.get_edge_table(edge.edge_type)
        
        # For update, we can just use UPDATE/UPSERT if ID is known?
        # Or RELATE again? RELATE is upsert if ID matches.
        
        in_rec = data.pop("_source_rec")
        out_rec = data.pop("_target_rec")
        
        query = f"RELATE {in_rec} -> {table} -> {out_rec} CONTENT $data RETURN AFTER;"
        
        results = await self.db.query(query, {"data": data})
        updated_record = results[0] if results else {}
        
        updated_record['source'] = updated_record.get('in', '')
        updated_record['target'] = updated_record.get('out', '')
        return BaseEdge.model_validate(updated_record)

    async def delete_edge(self, edge_id: str) -> None:
        await self.db.delete(edge_id)

    async def ingest(self, nodes: List[BaseNode], edges: List[BaseEdge], batch_size: int = 100) -> SyncReport:
        """
        Ingests a list of nodes and edges using batched transactions.
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
                
                # Using UPSERT
                transaction_query += f"UPSERT {table}:`{node.id}` CONTENT ${param_name};\n"
            
            transaction_query += "COMMIT TRANSACTION;"
            results = await self.db.query(transaction_query, params)
            
            # Check for top-level error (SurrealDB 2.0 returns dict on error)
            if isinstance(results, dict) and results.get('status') == 'ERR':
                 raise Exception(f"SurrealDB Transaction Error (Nodes): {results.get('detail')}")

            if isinstance(results, list):
                for res in results:
                    if isinstance(res, dict) and res.get('status') == 'ERR':
                        raise Exception(f"SurrealDB Transaction Error (Nodes): {res.get('detail')}")
            
            nodes_created += len(batch_nodes)

        # Process Edges in batches
        for i in range(0, len(edges), batch_size):
            batch_edges = edges[i:i + batch_size]
            transaction_query = "BEGIN TRANSACTION;\n"
            params = {}

            for idx, edge in enumerate(batch_edges):
                edge.updated_at = datetime.utcnow()
                data = self._prepare_edge_data(edge)
                
                # Extract pre-calculated record IDs
                in_rec = data.pop("_source_rec")
                out_rec = data.pop("_target_rec")
                
                param_name = f"edge_{i}_{idx}"
                params[param_name] = data
                
                table = self.schema_mapper.get_edge_table(edge.edge_type)
                
                # Using RELATE for edges
                transaction_query += f"RELATE {in_rec} -> {table} -> {out_rec} CONTENT ${param_name};\n"

            transaction_query += "COMMIT TRANSACTION;"
            results = await self.db.query(transaction_query, params)
            
            # Check for transaction errors
            if isinstance(results, list):
                for res in results:
                    if isinstance(res, dict) and res.get('status') == 'ERR':
                        raise Exception(f"SurrealDB Transaction Error (Edges): {res.get('detail')}")
            
            edges_created += len(batch_edges)
        
        return SyncReport(
            success=True,
            message="Nodes and edges ingested successfully.",
            nodes_created=nodes_created,
            edges_created=edges_created
        )