import asyncio
from pathlib import Path
import numpy as np
import logging
import time

from coretext.core.system.process import set_background_priority
# Type hint only to avoid circular import if needed, though dependency injection handles it
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coretext.core.system.memory import MemoryWatchdog

logger = logging.getLogger(__name__)

class VectorEmbedder:
    """
    Handles generation of vector embeddings for text using Nomic Embed.
    """
    def __init__(
        self, 
        model_name: str = "nomic-ai/nomic-embed-text-v1.5", 
        cache_dir: str | None = None,
        memory_watchdog: "MemoryWatchdog | None" = None,
        idle_timeout_seconds: int = 300  # 5 minutes default
    ):
        """
        Initialize the vector embedder.

        Args:
            model_name: The HuggingFace model ID to load.
            cache_dir: Directory to cache the model. Defaults to ~/.coretext/cache.
            memory_watchdog: Optional MemoryWatchdog instance to coordinate memory usage.
            idle_timeout_seconds: Seconds of inactivity before unloading the model.
        """
        self.model_name = model_name
        self.memory_watchdog = memory_watchdog
        self.idle_timeout_seconds = idle_timeout_seconds
        self.last_used_time = 0.0
        
        if cache_dir is None:
             cache_dir = str(Path.home() / ".coretext" / "cache")
        
        # Ensure cache directory exists
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        self.cache_dir = cache_dir
        self.model = None

        # Register cleanup task with watchdog if available
        if self.memory_watchdog:
            self.memory_watchdog.register_cleanup_task(self.check_idle)

    async def check_idle(self):
        """
        Checks if the model has been idle for too long and unloads it.
        This is intended to be called periodically (e.g., by MemoryWatchdog).
        """
        if self.model is not None:
            now = time.time()
            if now - self.last_used_time > self.idle_timeout_seconds:
                logger.info(f"VectorEmbedder idle for {now - self.last_used_time:.0f}s. Unloading model.")
                self.unload_model()

    def _load_model(self):
        """Lazily loads the SentenceTransformer model."""
        if self.model is None:
            # Tell watchdog we are about to load a heavy object (~300MB)
            if self.memory_watchdog:
                self.memory_watchdog.adjust_threshold(300)

            # Set background priority for the process as model loading/usage is resource intensive
            set_background_priority()
            
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name, trust_remote_code=True, cache_folder=self.cache_dir)
                self.last_used_time = time.time()
            except Exception as e:
                # If load fails, revert threshold
                if self.memory_watchdog:
                    self.memory_watchdog.adjust_threshold(-300)
                raise e

    def unload_model(self):
        """Unloads the model to free memory."""
        if self.model is not None:
            logger.info("Unloading embedding model to free memory")
            self.model = None
            
            # Revert watchdog threshold
            if self.memory_watchdog:
                self.memory_watchdog.adjust_threshold(-300)
            
            # Force GC
            import gc
            gc.collect()
            
            # Try to free Torch memory if applicable
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                     torch.mps.empty_cache()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Error clearing torch cache: {e}")

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
        # Update usage time
        self.last_used_time = time.time()
        
        # Nomic specific prefixes
        prefix = f"{task_type}: "
        input_text = prefix + text
        
        # Ensure model is loaded
        if self.model is None:
            await asyncio.to_thread(self._load_model)
        
        # Run in thread pool to avoid blocking event loop
        embedding = await asyncio.to_thread(
            self.model.encode, 
            input_text, 
            convert_to_numpy=True
        )
        
        # Matryoshka slicing
        if dimension < len(embedding):
             embedding = embedding[:dimension]
             # Re-normalize after slicing for optimal performance
             norm = np.linalg.norm(embedding)
             if norm > 0:
                 embedding = embedding / norm

        return embedding.tolist()