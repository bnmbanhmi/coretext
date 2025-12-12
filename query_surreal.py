import asyncio
import json
from surrealdb import AsyncSurreal
import sys
from datetime import datetime
from coretext.core.graph.models import FileNode # Import FileNode
from pathlib import Path

# Dynamically get RecordID type if available in the surrealdb client
_RECORD_ID_TYPE = None
try:
    from surrealdb.models import RecordID as _RecID
    _RECORD_ID_TYPE = _RecID
except ImportError:
    try:
        from surrealdb.responses import RecordID as _RecID
        _RECORD_ID_TYPE = _RecID
    except ImportError:
        pass # RecordID type is not directly importable


# Custom JSON encoder to handle RecordID, Path and datetime objects
class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        if _RECORD_ID_TYPE and isinstance(obj, _RECORD_ID_TYPE):
            return str(obj)

        return super().default(obj)


async def test_surreal_db_crud():
    try:
        async with AsyncSurreal('ws://localhost:8000/rpc') as db:
            await db.use('coretext', 'coretext')
            
            # 1. Prepare a test FileNode using Pydantic model
            test_node_id_str = "test_file.md"
            test_node = FileNode(
                id=test_node_id_str,
                node_type="file",
                content="This is test content.",
                metadata={"author": "Gemini"},
                commit_hash="test_commit_hash_123",
                path=Path(test_node_id_str), # Changed from file_path to path
                title="Test Title from Code", 
                summary="Test Summary from Code"
            )
            
            # Use model_dump to get the dictionary payload
            data_payload = test_node.model_dump(mode='json', exclude_unset=False)
            data_payload.pop('id', None) # Remove 'id' from payload

            print(f"Data payload to be sent to SurrealQL CREATE: {json.dumps(data_payload, indent=2, cls=CustomJsonEncoder)}")

            # 2. Execute a raw CREATE statement with params
            create_query = f"CREATE file:⟨{test_node.id}⟩ CONTENT $payload;"
            params = {"payload": data_payload}
            
            print(f"\nExecuting CREATE query: {create_query} with params: {json.dumps(params, indent=2, cls=CustomJsonEncoder)}")
            
            # db.query returns a list of dictionaries, one for each statement
            # The 'result' field of the first item is what we care about for a CREATE.
            query_results = await db.query(create_query, params)
            inserted_record_data = query_results[0]['result'] if query_results and query_results[0]['status'] == 'OK' else None
            
            print(f"Inserted record: {json.dumps(inserted_record_data, indent=2, cls=CustomJsonEncoder)}")

            # 3. Query the file table
            files = await db.select('file')
            print(f"\nFiles after insert: {json.dumps(files, indent=2, cls=CustomJsonEncoder)}")

            # 4. Query the specific test record
            retrieved_record = await db.select(f"file:⟨{test_node.id}⟩") # Use escaped ID
            print(f"\nRetrieved test record: {json.dumps(retrieved_record, indent=2, cls=CustomJsonEncoder)}")

            # 5. Delete the test record
            await db.delete(f"file:⟨{test_node.id}⟩") # Use escaped ID
            print(f"\nDeleted record: file:⟨{test_node.id}⟩")

            # 6. Query again to confirm deletion
            files_after_delete = await db.select('file')
            print(f"\nFiles after delete: {json.dumps(files_after_delete, indent=2, cls=CustomJsonEncoder)}")
            
            return 0 # Success
    except Exception as e:
        print(f"Error connecting to or querying SurrealDB: {e}", file=sys.stderr)
        return 1 # Failure

if __name__ == "__main__":
    sys.exit(asyncio.run(test_surreal_db_crud()))