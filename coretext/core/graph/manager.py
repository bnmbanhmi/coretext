from typing import Type, List, Any
from surrealdb import Surreal
from coretext.core.graph.models import BaseNode, BaseEdge, ParsingErrorNode, SyncReport
from coretext.core.parser.schema import SchemaMapper
from coretext.core.vector.embedder import VectorEmbedder
from datetime import datetime

class GraphManager:
    def __init__(self, db_client: Surreal, schema_mapper: SchemaMapper, embedder: VectorEmbedder | None = None):
        self.db = db_client
        self.schema_mapper = schema_mapper
        self.embedder = embedder or VectorEmbedder()

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
        # FIX: Do not wrap in backticks here. pass raw string.
        data["id"] = edge.id
        
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
        fetched_records = await self.db.select(node_id)
        if fetched_records:
            # If it's a list, take the first item
            record = fetched_records[0] if isinstance(fetched_records, list) else fetched_records
            record = self._convert_ids(record)
            return node_model.model_validate(record)
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
        fetched_records = await self.db.select(edge_id)
        if fetched_records:
            # If it's a list, take the first item
            record = fetched_records[0] if isinstance(fetched_records, list) else fetched_records
            record = self._convert_ids(record)
            # Map 'in' and 'out' to 'source' and 'target' for Pydantic model
            record['source'] = record.pop('in')
            record['target'] = record.pop('out')
            return edge_model.model_validate(record)
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

    def _convert_ids(self, data: Any) -> Any:
        """
        Recursively converts SurrealDB RecordID objects to strings.
        """
        from surrealdb.data.types.record_id import RecordID
        
        if isinstance(data, RecordID):
            return str(data)
        elif isinstance(data, list):
            return [self._convert_ids(item) for i, item in enumerate(data)]
        elif isinstance(data, dict):
            return {k: self._convert_ids(v) for k, v in data.items()}
        return data

    async def search_topology(self, query: str, limit: int = 5) -> List[dict]:
        """
        Search for nodes semantically similar to the query.

        Args:
            query: The search query string.
            limit: Maximum number of results to return.

        Returns:
            List of matching nodes with similarity scores.
        """
        embedding = await self.embedder.encode(query, task_type="search_query")
        
        # Use simple vector similarity search
        # Explicitly select fields to avoid returning 'embedding' (large vector)
        sql = """
        SELECT 
            id, path, node_type, content, metadata, 
            created_at, updated_at, commit_hash,
            title, summary, level, content_hash,
            vector::similarity::cosine(embedding, $embedding) AS score 
        FROM node 
        WHERE embedding != NONE AND embedding != []
        ORDER BY score DESC
        LIMIT $limit;
        """
        
        response = await self.db.query(sql, {"embedding": embedding, "limit": limit})
        
        # Handle SurrealDB response format
        if isinstance(response, list) and len(response) > 0:
            result_obj = response[0]
            if isinstance(result_obj, dict) and result_obj.get('status') == 'OK':
                return self._convert_ids(result_obj.get('result', []))
            return self._convert_ids(response)
            
        return []

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
            
            # Generate embeddings for nodes that don't have them
            for node in batch_nodes:
                if not node.embedding:
                    # Heuristic for text to embed: content first, then title, then ID
                    text_to_embed = node.content or getattr(node, 'title', "") or str(node.id)
                    if text_to_embed:
                        node.embedding = await self.embedder.encode(text_to_embed, task_type="search_document")

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
            
            if isinstance(results, str):
                 raise Exception(f"SurrealDB Transaction Error (Nodes): {results}")
            
            nodes_created += len(batch_nodes)

        # Process Edges in batches
        for i in range(0, len(edges), batch_size):
            batch_edges = edges[i:i + batch_size]
            transaction_query = "BEGIN TRANSACTION;\n"
            params = {}

            for idx, edge in enumerate(batch_edges):
                edge.updated_at = datetime.utcnow()
                data = self._prepare_edge_data(edge)
                
                # Extract pre-calculated record IDs (which currently have backticks/prefixes)
                # We will ignore the pre-calculated string and reconstruct using type::thing for safety
                # But _prepare_edge_data removes source/target from data, so we need to get them from 'edge' object
                
                # Cleanup keys we don't need from data payload
                data.pop("_source_rec", None)
                data.pop("_target_rec", None)
                # Remove ID from payload as we will specify it in the RELATE clause
                # Providing it in CONTENT causes referential integrity issues in RELATE
                data.pop("id", None)
                
                param_name = f"edge_{i}_{idx}"
                params[param_name] = data
                
                # Get tables
                edge_def = self.schema_mapper.schema_map.edge_types.get(edge.edge_type)
                if not edge_def:
                    source_table = "node"
                    target_table = "node"
                else:
                    source_table = self.schema_mapper.get_node_table(edge_def.source_type)
                    target_table = self.schema_mapper.get_node_table(edge_def.target_type)

                # Add params for the IDs to avoid injection and formatting issues
                src_id_param = f"src_id_{i}_{idx}"
                tgt_id_param = f"tgt_id_{i}_{idx}"
                params[src_id_param] = edge.source
                params[tgt_id_param] = edge.target
                
                table = self.schema_mapper.get_edge_table(edge.edge_type)
                
                # Construct IDs manually with backticks to ensure safety and bypass type::thing issues
                src_rec_str = f"{source_table}:`{edge.source}`"
                tgt_rec_str = f"{target_table}:`{edge.target}`"
                edge_rec_str = f"{table}:`{edge.id}`"
                
                # 1. RELATE to ensure existence and links.
                # Use manual string interpolation for IDs.
                # Do NOT use CONTENT here to avoid wiping existing in/out pointers on update.
                # We MUST set mandatory schema fields (like commit_hash) here to avoid validation error on creation.
                set_clause = f"SET updated_at = time::now(), created_at = time::now(), commit_hash = ${param_name}.commit_hash, metadata = ${param_name}.metadata"
                if edge.edge_type == "contains":
                    set_clause += f", order = ${param_name}.order"

                transaction_query += f"RELATE {src_rec_str} -> {edge_rec_str} -> {tgt_rec_str} {set_clause};\n"
                
                # 2. UPDATE MERGE to set/update properties from data payload without losing links.
                transaction_query += f"UPDATE {edge_rec_str} MERGE ${param_name};\n"

            transaction_query += "COMMIT TRANSACTION;"
            results = await self.db.query(transaction_query, params)
            
            if isinstance(results, str):
                 raise Exception(f"SurrealDB Transaction Error (Edges): {results}")
            
            edges_created += len(batch_edges)
        
        return SyncReport(
            success=True,
            message="Nodes and edges ingested successfully.",
            nodes_created=nodes_created,
            edges_created=edges_created
        )

    async def get_dependencies(self, node_id: str, depth: int = 1) -> List[dict]:
        """
        Retrieves direct and indirect dependencies for a given node.

        Args:
            node_id: The ID of the node (e.g., 'file:path/to/file' or 'node:`path`').
            depth: The depth of traversal (default: 1).

        Returns:
            A list of dictionaries containing 'node_id', 'relationship_type', and 'direction'.
        """
        from surrealdb.data.types.record_id import RecordID
        
        # Normalize input node_id to RecordID
        try:
            # Handle various input formats:
            # 1. "file:path/to/file"
            # 2. "file:`path/to/file`"
            # 3. RecordID object (if passed directly)
            
            if isinstance(node_id, RecordID):
                root_rid = node_id
            else:
                # Remove backticks that might be wrapping the ID part
                # e.g. "table:`id`" -> "table:id"
                clean_id = node_id.replace("`", "")
                root_rid = RecordID.parse(clean_id)
        except Exception:
            # Fallback if parsing fails (shouldn't happen with valid IDs)
            return []

        dependencies = []
        # RecordID is not hashable in some versions of the library, use string representation for visited set
        visited = {str(root_rid)}
        queue = [(root_rid, 0)] # (current_rid, current_depth)
        
        while queue:
            current_rid, current_depth = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            # Query for outgoing dependencies and incoming parent (context)
            # Using multiple queries for reliability with v1 client vs SurrealDB 2.0
            
            queries = [
                ("SELECT out as dependency, 'depends_on' as relationship, 'outgoing' as direction FROM type::record($id)->depends_on", "depends_on"),
                ("SELECT out as dependency, 'governed_by' as relationship, 'outgoing' as direction FROM type::record($id)->governed_by", "governed_by"),
                ("SELECT in as dependency, 'parent_of' as relationship, 'incoming' as direction FROM type::record($id)<-parent_of", "parent_of"),
                ("SELECT out as dependency, 'contains' as relationship, 'outgoing' as direction FROM type::record($id)->contains", "contains"),
                ("SELECT out as dependency, 'references' as relationship, 'outgoing' as direction FROM type::record($id)->references", "references"),
            ]
            
            param_id = f"{current_rid.table_name}:`{current_rid.id}`"

            for sql, rel_name in queries:
                try:
                    results = await self.db.query(sql, {"id": param_id})
                    
                    if isinstance(results, list) and len(results) > 0:
                        # Check if results are wrapped in a Status object (common in v1 client)
                        # or if it's already a flat list of records
                        first = results[0]
                        if isinstance(first, dict) and first.get('status') == 'OK' and 'result' in first:
                            items = first.get('result', [])
                        elif isinstance(first, dict) and 'dependency' in first:
                            # It's already a list of records
                            items = results
                        else:
                            # Might be empty or unexpected format
                            items = []
                        
                        if isinstance(items, list):
                            for row in items:
                                dep_rid = row.get('dependency')
                                dep_str = None
                                if isinstance(dep_rid, RecordID):
                                    dep_str = str(dep_rid)
                                elif isinstance(dep_rid, str):
                                    dep_str = dep_rid
                                
                                if dep_str and dep_str not in visited:
                                    visited.add(dep_str)
                                    
                                    deps_item = {
                                        "node_id": dep_str,
                                        "from_node_id": str(current_rid),
                                        "relationship_type": row.get('relationship'),
                                        "direction": row.get('direction')
                                    }
                                    dependencies.append(deps_item)
                                    queue.append((dep_rid if isinstance(dep_rid, RecordID) else RecordID.parse(dep_str.replace("`", "")), current_depth + 1))
                except Exception:
                    continue
                                     
        return self._convert_ids(dependencies)
