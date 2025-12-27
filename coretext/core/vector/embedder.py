import asyncio
import os
from pathlib import Path
from typing import Any
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorEmbedder:
    """
    Handles generation of vector embeddings for text using Nomic Embed.
    """
    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1.5", cache_dir: str | None = None):
        """
        Initialize the vector embedder.

        Args:
            model_name: The HuggingFace model ID to load.
            cache_dir: Directory to cache the model. Defaults to ~/.coretext/cache.
        """
        if cache_dir is None:
             cache_dir = str(Path.home() / ".coretext" / "cache")
        
        # Ensure cache directory exists
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        self.model = SentenceTransformer(model_name, trust_remote_code=True, cache_folder=cache_dir)

    async def encode(self, text: str, task_type: str = "search_document", dimension: int = 768) -> list[float]:
        """
        Generate an embedding for the given text.

        Args:
            text: The text to encode.
            task_type: The task type prefix (e.g., 'search_query', 'search_document').
            dimension: The desired dimensionality of the embedding (Matryoshka slicing).

        Returns:
            A list of floats representing the embedding.
        """
        # Nomic specific prefixes
        prefix = f"{task_type}: "
        input_text = prefix + text
        
        # Run in thread pool to avoid blocking event loop
        embedding = await asyncio.to_thread(
            self.model.encode, 
            input_text, 
            convert_to_numpy=True
        )
        
        # Matryoshka slicing
        if dimension < len(embedding):
             embedding = embedding[:dimension]
             # Matryoshka embeddings usually perform better if normalized after slicing
             # but strictly following the AC "slicing" for now. 
             # Ideally we should re-normalize: 
             # norm = np.linalg.norm(embedding)
             # if norm > 0: embedding = embedding / norm

        return embedding.tolist()
