import pytest
from unittest.mock import patch, ANY
import numpy as np
from coretext.core.vector.embedder import VectorEmbedder

@pytest.mark.asyncio
async def test_embedder_initialization():
    """Test that the embedder initializes with the correct model."""
    with patch("sentence_transformers.SentenceTransformer") as MockST:
        # Mock the model instance
        MockST.return_value
        
        embedder = VectorEmbedder()
        
        # Verify it loads the correct model and cache_folder
        # Since _load_model is lazy, we need to trigger it to test initialization params
        # Wait, the original test calls VectorEmbedder() and expects init?
        # VectorEmbedder __init__ DOES NOT load model. _load_model does.
        # So checking MockST.assert_called_with IMMEDIATELY after __init__ is WRONG if lazy loading is implemented.
        # But looking at previous code, it seemed to expect it?
        # Let's check embedder.py again.
        # __init__ sets self.model = None.
        # So this test was verifying something that shouldn't happen yet? 
        # OR the test assumes we call _load_model manually?
        
        # In existing test code:
        # embedder = VectorEmbedder()
        # MockST.assert_called_with(...)
        
        # This implies the previous version of code might have loaded in __init__?
        # Or the test is broken. 
        # But I see lazy loading in embedder.py: def _load_model(self): ...
        
        # I should probably fix the test to trigger load.
        embedder._load_model()
        
        MockST.assert_called_with(
            "nomic-ai/nomic-embed-text-v1.5", 
            trust_remote_code=True, 
            cache_folder=ANY
        )

@pytest.mark.asyncio
async def test_embedder_encode_query():
    """Test encoding a search query with the correct prefix."""
    with patch("sentence_transformers.SentenceTransformer") as MockST:
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
    with patch("sentence_transformers.SentenceTransformer") as MockST:
        mock_model = MockST.return_value
        mock_model.encode.return_value = np.array([0.1] * 768)
        
        embedder = VectorEmbedder()
        await embedder.encode("test content", task_type="search_document")
        
        # Verify prefix handling for document
        mock_model.encode.assert_called_with("search_document: test content", convert_to_numpy=True)

@pytest.mark.asyncio
async def test_embedder_matryoshka_slicing():
    """Test that embeddings are sliced to the requested dimension."""
    with patch("sentence_transformers.SentenceTransformer") as MockST:
        mock_model = MockST.return_value
        # Return full 768 dimension
        mock_model.encode.return_value = np.array([0.1] * 768)
        
        embedder = VectorEmbedder()
        # Request smaller dimension
        embedding = await embedder.encode("test", dimension=64)
        
        assert len(embedding) == 64

@pytest.mark.asyncio
async def test_embedder_lifecycle():
    """Test model loading (with priority setting) and unloading."""
    with patch("sentence_transformers.SentenceTransformer") as MockST, \
         patch("coretext.core.vector.embedder.set_background_priority") as mock_set_priority:
        
        mock_model = MockST.return_value
        mock_model.encode.return_value = np.array([0.1] * 768)
        
        embedder = VectorEmbedder()
        assert embedder.model is None
        
        # Trigger load via encode
        await embedder.encode("test")
        
        assert embedder.model is not None
        mock_set_priority.assert_called_once()
        
        # Test unload
        embedder.unload_model()
        assert embedder.model is None