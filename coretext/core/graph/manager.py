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
            source_table = "node"
            target_table = "node"
        else:
            source_type = edge_def.source_type
            target_type = edge_def.target_type
            source_table = self.schema_mapper.get_node_table(source_type)
            target_table = self.schema_mapper.get_node_table(target_type)

        # Store separate parts for robust type::thing() construction
        data["in_table"] = source_table
        data["in_id"] = edge.source
        data["out_table"] = target_table
        data["out_id"] = edge.target
        
        # Remove original source/target
        del data["source"]
        del data["target"]
        
        return data

    def _build_set_clause(self, data: dict, param_name: str) -> str:
        parts = []
        
        # Explicitly handle 'in' and 'out' using type::thing
        parts.append(f"in = type::thing(${param_name}.in_table, ${param_name}.in_id)")
        parts.append(f"out = type::thing(${param_name}.out_table, ${param_name}.out_id)")
        
        for k in data.keys():
            # Skip the helper fields we added
            if k in ['in_table', 'in_id', 'out_table', 'out_id']:
                continue
            parts.append(f"{k} = ${param_name}.{k}")
            
        return ", ".join(parts)

    async def create_node(self, node: BaseNode) -> BaseNode:
        node.created_at = datetime.utcnow()
        node.updated_at = datetime.utcnow()
        data = node.model_dump(mode='json')
        
        table = self.schema_mapper.get_node_table(node.node_type)
        # Use table from schema map (e.g., 'node')
        created_record = await self.db.create(f"{table}:`{node.id}`", data)
        return BaseNode.model_validate(created_record)

    async def get_node(self, node_id: str, node_model: Type[BaseNode] = BaseNode) -> BaseNode | None:
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
        
        set_clause = self._build_set_clause(data, "data")
        query = f"CREATE {table}:`{edge.id}` SET {set_clause} RETURN AFTER;"
        
        results = await self.db.query(query, {"data": data})
        created_record = results[0] if results else {}
        
        # Map back for response (simplified)
        created_record['source'] = created_record.get('in', '')
        created_record['target'] = created_record.get('out', '')
        return BaseEdge.model_validate(created_record)

    async def get_edge(self, edge_id: str, edge_model: Type[BaseEdge] = BaseEdge) -> BaseEdge | None:
        fetched_record = await self.db.select(edge_id)
        if fetched_record:
            fetched_record['source'] = fetched_record.pop('in')
            fetched_record['target'] = fetched_record.pop('out')
            return edge_model.model_validate(fetched_record)
        return None

    async def update_edge(self, edge: BaseEdge) -> BaseEdge:
        edge.updated_at = datetime.utcnow()
        
        data = self._prepare_edge_data(edge)
        table = self.schema_mapper.get_edge_table(edge.edge_type)
        
        set_clause = self._build_set_clause(data, "data")
        query = f"UPDATE {table}:`{edge.id}` SET {set_clause} RETURN AFTER;"
        
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
                
                param_name = f"edge_{i}_{idx}"
                params[param_name] = data
                
                table = self.schema_mapper.get_edge_table(edge.edge_type)
                
                # Dynamic SET clause with type::thing
                set_clause = self._build_set_clause(data, param_name)
                
                # Using UPSERT with SET
                transaction_query += f"UPSERT {table}:`{edge.id}` SET {set_clause};\n"

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
