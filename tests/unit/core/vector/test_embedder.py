import pytest
from unittest.mock import patch, MagicMock, ANY
import numpy as np
from coretext.core.vector.embedder import VectorEmbedder

@pytest.mark.asyncio
async def test_embedder_initialization():
    """Test that the embedder initializes with the correct model."""
    with patch("coretext.core.vector.embedder.SentenceTransformer") as MockST:
        # Mock the model instance
        mock_model = MockST.return_value
        
        embedder = VectorEmbedder()
        
        # Verify it loads the correct model and cache_folder
        MockST.assert_called_with(
            "nomic-ai/nomic-embed-text-v1.5", 
            trust_remote_code=True, 
            cache_folder=ANY
        )

@pytest.mark.asyncio
async def test_embedder_encode_query():
    """Test encoding a search query with the correct prefix."""
    with patch("coretext.core.vector.embedder.SentenceTransformer") as MockST:
        mock_model = MockST.return_value
        # Mock encode to return a dummy embedding as numpy array
        mock_model.encode.return_value = np.array([0.1] * 768)
        
        embedder = VectorEmbedder()
        embedding = await embedder.encode("test query", task_type="search_query")
        
        assert len(embedding) == 768
        # Verify prefix handling for query
        mock_model.encode.assert_called_with("search_query: test query", convert_to_numpy=True)

@pytest.mark.asyncio
async def test_embedder_encode_document():
    """Test encoding a document with the correct prefix."""
    with patch("coretext.core.vector.embedder.SentenceTransformer") as MockST:
        mock_model = MockST.return_value
        mock_model.encode.return_value = np.array([0.1] * 768)
        
        embedder = VectorEmbedder()
        embedding = await embedder.encode("test content", task_type="search_document")
        
        # Verify prefix handling for document
        mock_model.encode.assert_called_with("search_document: test content", convert_to_numpy=True)

@pytest.mark.asyncio
async def test_embedder_matryoshka_slicing():
    """Test that embeddings are sliced to the requested dimension."""
    with patch("coretext.core.vector.embedder.SentenceTransformer") as MockST:
        mock_model = MockST.return_value
        # Return full 768 dimension
        mock_model.encode.return_value = np.array([0.1] * 768)
        
        embedder = VectorEmbedder()
        # Request smaller dimension
        embedding = await embedder.encode("test", dimension=64)
        
        assert len(embedding) == 64
