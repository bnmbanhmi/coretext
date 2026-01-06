import asyncio
import logging
import numpy as np
from surrealdb import AsyncSurreal
from coretext.core.vector.embedder import VectorEmbedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing VectorEmbedder...")
    embedder = VectorEmbedder()
    
    query_text = "   "
    logger.info(f"Encoding text: '{query_text}'")
    
    try:
        embedding = await embedder.encode(query_text, task_type="search_query")
        logger.info(f"Embedding generated. Type: {type(embedding)}")
        if isinstance(embedding, list):
            logger.info(f"Length: {len(embedding)}")
            logger.info(f"First 5 values: {embedding[:5]}")
        else:
            logger.error("Embedding is not a list!")
            return
            
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return

    logger.info("Connecting to SurrealDB...")
    db = AsyncSurreal("ws://localhost:8010/rpc")
    try:
        await db.connect()
        await db.use("coretext", "coretext")
        
        # Test 1: Check if parameter is received correctly
        logger.info("Test 1: Parameter passing")
        sql_debug = "RETURN $embedding;"
        result = await db.query(sql_debug, {"embedding": embedding})
        # logger.info(f"Debug Query Result: {result}")
        
        if isinstance(result, list) and len(result) > 0 and result[0] is not None:
             logger.info("Test 1 PASSED: Parameter received.")
        else:
             logger.error("Test 1 FAILED: Parameter seems missing or null.")

        # Test 2: Cosine Similarity with explicit vectors
        logger.info("Test 2: Cosine Similarity with explicit vectors")
        dummy_vector = [0.1] * len(embedding)
        sql_cosine = "RETURN vector::similarity::cosine($dummy, $embedding);"
        
        try:
            result_cosine = await db.query(sql_cosine, {"dummy": dummy_vector, "embedding": embedding})
            logger.info(f"Cosine Query Result: {result_cosine}")
        except Exception as e:
             logger.error(f"Test 2 FAILED: {e}")

        # Test 3: The actual table query (simulated)
        # We need to see if there is any data in the 'node' table first
        logger.info("Test 3: Table query simulation")
        
        # Check if we have any nodes with embeddings
        check_nodes = "SELECT count() FROM node WHERE embedding != NONE;"
        count_res = await db.query(check_nodes)
        logger.info(f"Nodes with embeddings: {count_res}")

        # Try the query that is failing
        sql_search = """
        SELECT 
            id,
            vector::similarity::cosine(embedding, $embedding) AS score 
        FROM node 
        WHERE embedding != NONE AND embedding != []
        LIMIT 1;
        """
        try:
            search_res = await db.query(sql_search, {"embedding": embedding})
            logger.info(f"Search Query Result: {search_res}")
        except Exception as e:
            logger.error(f"Test 3 FAILED: {e}")

    except Exception as e:
        logger.error(f"DB Connection/Query failed: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
