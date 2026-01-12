from typing import Type, List, Any
from surrealdb import Surreal
from surrealdb.data.types.record_id import RecordID
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
        created_record = self._convert_ids(created_record)
        return BaseNode.model_validate(created_record)

    async def get_node(self, node_id: str, node_model: Type[BaseNode] = BaseNode) -> BaseNode | None:
        # SurrealDB select returns a list of records
        fetched_records = await self.db.select(node_id)
        if fetched_records:
            # If it's a list, take the first item
            record = fetched_records[0] if isinstance(fetched_records, list) else fetched_records
            
            # Check for invalid record types (e.g. nan, float, None) which indicate not found or error
            if isinstance(record, float) or record is None:
                return None
                
            record = self._convert_ids(record)
            return node_model.model_validate(record)
        return None

    async def update_node(self, node: BaseNode) -> BaseNode:
        node.updated_at = datetime.utcnow()
        data = node.model_dump(mode='json')
        
        table = self.schema_mapper.get_node_table(node.node_type)
        updated_record = await self.db.update(f"{table}:`{node.id}`", data)
        updated_record = self._convert_ids(updated_record)
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
        created_record = self._convert_ids(created_record)
        
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
        updated_record = self._convert_ids(updated_record)
        
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

    def _get_all_node_tables(self) -> str:
        """Returns a comma-separated string of all unique node tables from the schema."""
        if not self.schema_mapper._schema_map:
             # Ensure schema is loaded
             try:
                 self.schema_mapper.load_schema()
             except Exception:
                 # Fallback if load fails (e.g. file missing), though it should be loaded by app startup
                 return "node"
        
        tables = set(nt.db_table for nt in self.schema_mapper.schema_map.node_types.values())
        return ", ".join(tables) if tables else "node"

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
        
        if not embedding:
            # Should not happen with current embedder, but safety check for "Argument 2 ... NONE" error
            return []
        
        target_tables = self._get_all_node_tables()

        # Use simple vector similarity search
        # Explicitly select fields to avoid returning 'embedding' (large vector)
        sql = f"""
        SELECT 
            id, path, node_type, content, metadata, 
            created_at, updated_at, commit_hash,
            title, summary, level, content_hash,
            vector::similarity::cosine(embedding, $embedding) AS score 
        FROM {target_tables} 
        WHERE embedding != NONE AND embedding != []
        ORDER BY score DESC
        LIMIT $limit;
        """
        
        response = await self.db.query(sql, {"embedding": embedding, "limit": limit})
        
        # Handle SurrealDB response format robustly
        results = []
        if isinstance(response, list) and len(response) > 0:
            result_obj = response[0]
            if isinstance(result_obj, dict) and result_obj.get('status') == 'OK':
                results = result_obj.get('result', [])
            elif isinstance(result_obj, dict) and 'score' in result_obj:
                 # Flattened list of dicts (some driver versions)
                 results = response
            else:
                 # Fallback/Direct list
                 results = response

        return self._convert_ids(results)

    async def search_hybrid(
        self, 
        query: str, 
        top_k: int = 5, 
        depth: int = 1, 
        regex: str | None = None, 
        keywords: str | None = None
    ) -> dict:
        """
        Performs a universal search combining Vector Search, Regex, and Keywords,
        followed by a graph traversal to gather context.

        Args:
            query: The natural language query for vector search.
            top_k: Number of anchor nodes to retrieve.
            depth: Traversal depth from anchors.
            regex: Optional regex pattern to filter nodes (matches id, path, or content).
            keywords: Optional keyword string to require in content.

        Returns:
            A dictionary containing 'nodes' and 'edges' lists (deduplicated).
        """
        # 1. Embed query
        embedding = await self.embedder.encode(query, task_type="search_query")
        if not embedding:
            return {"nodes": [], "edges": []}

        target_tables = self._get_all_node_tables()

        # 2. Find Anchors
        sql = f"""
        SELECT 
            *,
            vector::similarity::cosine(embedding, $embedding) AS score 
        FROM {target_tables} 
        WHERE embedding != NONE AND embedding != []
        """
        params = {"embedding": embedding, "limit": top_k}

        if regex:
            # Check id, path, or content.
            # Using string::matches function to support parameterized regex
            sql += " AND (string::matches(type::string(id), $regex) OR string::matches(path, $regex) OR string::matches(content, $regex))"
            params["regex"] = regex
        
        if keywords:
            sql += " AND content CONTAINS $keyword"
            params["keyword"] = keywords

        sql += " ORDER BY score DESC LIMIT $limit;"

        response = await self.db.query(sql, params)
        
        anchors = []
        if isinstance(response, list) and len(response) > 0:
            result_obj = response[0]
            if isinstance(result_obj, dict) and result_obj.get('status') == 'OK':
                anchors = result_obj.get('result', [])
            elif isinstance(result_obj, dict) and 'score' in result_obj:
                 anchors = response
            elif isinstance(result_obj, list):
                 anchors = result_obj
            else:
                 anchors = response

        anchors = self._convert_ids(anchors)
        
        # 3. Traversal
        all_nodes = {n['id']: n for n in anchors}
        all_edges = {} # id -> edge dict

        current_level_ids = list(all_nodes.keys())
        visited_ids = set(current_level_ids)
        
        # Dynamic edge loading from schema
        # We assume all defined edge types are relevant for traversal unless filtered
        outgoing_tables = []
        incoming_tables = [] # We might need a way to know which edges are 'parent' types (incoming context)
        
        # Heuristic: 'parent_of' is incoming, others are outgoing
        # Or better: traverse all edges?
        # For 'search_hybrid' context, we want to know what this node depends on (outgoing)
        # AND what owns this node (incoming parent).
        
        if self.schema_mapper._schema_map:
             for edge_name, edge_def in self.schema_mapper.schema_map.edge_types.items():
                 table = edge_def.db_table
                 # Hardcoded heuristic for direction based on meaningful relationships
                 # This could be improved with 'traversal_direction' in schema later
                 if "parent" in table or "owned_by" in table: 
                     # Wait, parent_of: source(parent) -> target(child). 
                     # If we are child, we want INCOMING parent_of.
                     incoming_tables.append(table)
                 else:
                     outgoing_tables.append(table)
        else:
             # Fallback if schema not loaded
             outgoing_tables = ["depends_on", "governed_by", "contains", "references"]
             incoming_tables = ["parent_of"]

        # Ensure unique tables and deterministic order
        outgoing_tables = sorted(list(set(outgoing_tables)))
        incoming_tables = sorted(list(set(incoming_tables)))

        for _ in range(depth):
            if not current_level_ids:
                break
            
            queries = []
            
            # Outgoing edges: WHERE in IN $ids
            for table in outgoing_tables:
                queries.append(f"SELECT * FROM {table} WHERE in IN $ids;")
            
            # Incoming edges: WHERE out IN $ids
            for table in incoming_tables:
                queries.append(f"SELECT * FROM {table} WHERE out IN $ids;")
                
            batch_sql = "\n".join(queries)
            
            batch_results = await self.db.query(batch_sql, {"ids": current_level_ids})
            
            next_level_ids = set()
            
            # Helper to process results safely
            def get_result_list(res_item):
                if isinstance(res_item, dict) and res_item.get('status') == 'OK':
                    return res_item.get('result', [])
                elif isinstance(res_item, list):
                    return res_item
                return []

            if not isinstance(batch_results, list):
                batch_results = [batch_results]

            # Process outgoing results
            for i, table in enumerate(outgoing_tables):
                if i < len(batch_results):
                    edges = get_result_list(batch_results[i])
                    edges = self._convert_ids(edges)
                    for edge in edges:
                        all_edges[edge['id']] = edge
                        target_id = edge.get('out')
                        if target_id and target_id not in visited_ids:
                            next_level_ids.add(target_id)

            # Process incoming results
            offset = len(outgoing_tables)
            for i, table in enumerate(incoming_tables):
                idx = offset + i
                if idx < len(batch_results):
                    edges = get_result_list(batch_results[idx])
                    edges = self._convert_ids(edges)
                    for edge in edges:
                        all_edges[edge['id']] = edge
                        source_id = edge.get('in')
                        if source_id and source_id not in visited_ids:
                            next_level_ids.add(source_id)
            
            # Fetch new nodes
            if next_level_ids:
                # OPTIMIZATION: Update visited_ids BEFORE fetch to prevent redundant queries
                # for missing (dangling) nodes in future iterations.
                visited_ids.update(next_level_ids)
                
                node_query = f"SELECT * FROM {target_tables} WHERE id IN $ids;"
                node_res = await self.db.query(node_query, {"ids": list(next_level_ids)})
                
                fetched_nodes = []
                if isinstance(node_res, list) and len(node_res) > 0:
                     fetched_nodes = get_result_list(node_res[0])
                elif isinstance(node_res, dict):
                     fetched_nodes = get_result_list(node_res)
                
                fetched_nodes = self._convert_ids(fetched_nodes)
                
                for node in fetched_nodes:
                    all_nodes[node['id']] = node
                    # visited_ids already updated
                
                current_level_ids = list(next_level_ids)
            else:
                break

        # Convert to models and STRIP EMBEDDINGS
        final_nodes = []
        for n in all_nodes.values():
            try:
                # Strip embedding to save bandwidth/tokens
                if 'embedding' in n:
                    n['embedding'] = None
                
                final_nodes.append(BaseNode.model_validate(n))
            except Exception as e:
                print(f"[ERROR] Failed to validate node {n.get('id', 'unknown')}: {e}")
                continue
                
        final_edges = []
        for e in all_edges.values():
            try:
                e_copy = e.copy()
                e_copy['source'] = e_copy.get('in')
                e_copy['target'] = e_copy.get('out')
                final_edges.append(BaseEdge.model_validate(e_copy))
            except Exception as e:
                print(f"[ERROR] Failed to validate edge {e.get('id', 'unknown')}: {e}")
                continue

        return {"nodes": final_nodes, "edges": final_edges}

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
                id_param = f"id_{i}_{idx}"
                
                params[param_name] = data
                
                table = self.schema_mapper.get_node_table(node.node_type)
                # Use RecordID object for parameter
                params[id_param] = RecordID(table, node.id)
                
                # Using UPSERT with parameter
                transaction_query += f"UPSERT ${id_param} CONTENT ${param_name};\n"
            
            transaction_query += "COMMIT TRANSACTION;"
            # print(f"DEBUG QUERY: {transaction_query}") 
            results = await self.db.query(transaction_query, params)
            
            if isinstance(results, str):
                 raise Exception(f"SurrealDB Transaction Error (Nodes): {results}")
            
            # Robust check for SurrealDB 2.0 error format
            if isinstance(results, list):
                for res in results:
                    if isinstance(res, str) and ("Error" in res or "Found NONE" in res or "expected" in res):
                        raise Exception(f"SurrealDB Transaction Error (Nodes): {res}")
                    if isinstance(res, dict) and res.get('status') == 'ERR':
                        raise Exception(f"SurrealDB Transaction Error (Nodes): {res.get('detail', res)}")
            
            nodes_created += len(batch_nodes)

        # Process Edges in batches
        for i in range(0, len(edges), batch_size):
            batch_edges = edges[i:i + batch_size]
            transaction_query = "BEGIN TRANSACTION;\n"
            params = {}

            for idx, edge in enumerate(batch_edges):
                edge.updated_at = datetime.utcnow()
                data = self._prepare_edge_data(edge)
                
                # Cleanup keys we don't need from data payload
                data.pop("_source_rec", None)
                data.pop("_target_rec", None)
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

                # Add params for the IDs as RecordID objects
                src_id_param = f"src_id_{i}_{idx}"
                tgt_id_param = f"tgt_id_{i}_{idx}"
                edge_id_param = f"edge_id_{i}_{idx}"
                
                params[src_id_param] = RecordID(source_table, edge.source)
                params[tgt_id_param] = RecordID(target_table, edge.target)
                
                table = self.schema_mapper.get_edge_table(edge.edge_type)
                params[edge_id_param] = RecordID(table, edge.id)
                
                # 1. RELATE
                set_clause = f"SET updated_at = time::now(), created_at = time::now(), commit_hash = ${param_name}.commit_hash, metadata = ${param_name}.metadata"
                if edge.edge_type == "contains":
                    set_clause += f", order = ${param_name}.order"

                transaction_query += f"RELATE ${src_id_param} -> ${edge_id_param} -> ${tgt_id_param} {set_clause};\n"
                
                # 2. UPDATE MERGE
                transaction_query += f"UPDATE ${edge_id_param} MERGE ${param_name};\n"

            transaction_query += "COMMIT TRANSACTION;"
            results = await self.db.query(transaction_query, params)
            
            if isinstance(results, str):
                 raise Exception(f"SurrealDB Transaction Error (Edges): {results}")

            # Robust check for SurrealDB 2.0 error format
            if isinstance(results, list):
                for res in results:
                    if isinstance(res, str) and ("Error" in res or "Found NONE" in res or "expected" in res):
                        raise Exception(f"SurrealDB Transaction Error (Edges): {res}")
                    if isinstance(res, dict) and res.get('status') == 'ERR':
                        raise Exception(f"SurrealDB Transaction Error (Edges): {res.get('detail', res)}")
            
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

    async def prune_dangling_edges(self) -> int:
        """
        Removes edges where the 'in' or 'out' node no longer exists.
        Returns the count of deleted edges.
        """
        total_deleted = 0
        edge_tables = set()
        
        # Identify all edge tables from schema
        if self.schema_mapper._schema_map:
             for edge_def in self.schema_mapper.schema_map.edge_types.values():
                 edge_tables.add(edge_def.db_table)
        else:
            # Fallback if schema not loaded or empty? 
            # We should try to load it or default to common ones if possible, 
            # but usually it should be loaded.
            # If empty, maybe just try 'edge' generic if it existed, but we know it's specific tables.
            # Let's assume schema is available.
            pass

        # If no tables found (unlikely), return 0
        if not edge_tables:
            return 0

        # Construct query for each table
        # We check out.updated_at/in.updated_at to detect "ghost edges" (links to non-existent records)
        # SurrealDB returns NONE for 'out.updated_at' if 'out' points to a deleted record.
        queries = []
        print(f"DEBUG: Edge tables to prune: {edge_tables}")
        for table in edge_tables:
            # Use backticks for 'in' as it is a reserved word in SurrealQL
            # We use a subquery to check if the target record actually exists
            queries.append(f"DELETE {table} WHERE (SELECT VALUE id FROM out) = [] OR (SELECT VALUE id FROM `in`) = [];")

        # Execute
        for table in edge_tables:
            # We first SELECT the IDs of dangling edges
            # In SurrealDB 2.0, accessing .id on a RecordID field returns NONE if the record doesn't exist.
            select_query = f"SELECT VALUE id FROM {table} WHERE out.id == NONE OR `in`.id == NONE;"
            
            # results should be a list containing one item (the list of IDs)
            results = await self.db.query(select_query)

            if isinstance(results, list) and len(results) > 0:
                # Handle various formats:
                # 1. [ {status:OK, result:[...]} ]
                # 2. [ [...], [...] ] (list of statement results)
                # 3. [ rid1, rid2, ... ] (flattened single statement result)
                
                from surrealdb.data.types.record_id import RecordID
                
                ids_to_delete = []
                first_item = results[0]
                
                if isinstance(first_item, dict) and 'result' in first_item:
                    ids_to_delete = first_item.get('result', [])
                elif isinstance(first_item, list):
                    ids_to_delete = first_item
                elif isinstance(first_item, (RecordID, str)):
                    # Flat list of records/IDs
                    ids_to_delete = results
                
                if isinstance(ids_to_delete, list):
                    for rid in ids_to_delete:
                        # Convert RecordID to string if needed
                        rid_str = str(rid) if isinstance(rid, RecordID) else rid
                        await self.db.delete(rid_str)
                        total_deleted += 1
        
        return total_deleted

    async def prune_orphan_headers(self) -> int:
        """
        Removes Header nodes that are no longer linked to any File node via 'contains'.
        Returns the count of deleted headers.
        """
        # Header nodes are in 'node' table with node_type='header'
        # Linked via 'contains' edge (incoming to header)
        
        # We need the table name for headers
        header_table = "node" # Default assumption from schema
        if self.schema_mapper._schema_map and 'header' in self.schema_mapper.schema_map.node_types:
             header_table = self.schema_mapper.get_node_table('header')
        
        query = f"DELETE {header_table} WHERE node_type = 'header' AND count(<-contains) = 0;"
        
        results = await self.db.query(query)
        
        total_deleted = 0
        if isinstance(results, list) and len(results) > 0:
            res = results[0]
            if isinstance(res, list):
                total_deleted = len(res)
            elif isinstance(res, dict) and 'result' in res:
                items = res.get('result')
                if isinstance(items, list):
                    total_deleted = len(items)
            # If direct list return (some clients)
            elif isinstance(results, list):
                 # if results itself is the list of records
                 # Wait, query returns list of results (one per statement). 
                 # Since we sent 1 statement, results[0] is our result.
                 pass

        # Handle case where results is just the list of records (v1 client sometimes?)
        # But typical python client returns list of query results.
        
        return total_deleted

