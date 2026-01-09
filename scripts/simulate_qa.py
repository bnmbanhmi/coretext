import httpx
import json

def query_knowledge(query: str, regex: str = None):
    print(f"\n--- Query: {query} ---")
    payload = {
        "natural_query": query,
        "top_k": 5,
        "depth": 1
    }
    if regex:
        payload["regex_filter"] = regex
        
    try:
        response = httpx.post(
            "http://localhost:8001/mcp/tools/query_knowledge",
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            nodes = data.get("nodes", [])
            print(f"Found {len(nodes)} relevant nodes.")
            for node in nodes[:3]: # Show top 3
                print(f" - [{node.get('node_type')}] {node.get('id')} (Score: {node.get('score', 'N/A')})")
                if node.get('content'):
                    snippet = node.get('content')[:100].replace('\n', ' ')
                    print(f"   Snippet: {snippet}...")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test cases from story
    query_knowledge("Explain the core purpose of CoreText.")
    query_knowledge("What is the architecture for the sync engine?")
    query_knowledge("Find all mentions of SurrealDB in the docs.", regex="SurrealDB")

