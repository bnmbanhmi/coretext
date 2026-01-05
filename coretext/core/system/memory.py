import asyncio
import gc
import psutil
import logging
import os
from typing import Callable, Awaitable, List

logger = logging.getLogger(__name__)

class MemoryWatchdog:
    def __init__(self, soft_limit_mb: int = 50, check_interval: int = 60):
        self.soft_limit_mb = soft_limit_mb
        self.check_interval = check_interval
        self.running = False
        self._task: asyncio.Task | None = None
        self._dynamic_offset_mb = 0
        self._cleanup_tasks: List[Callable[[], Awaitable[None]]] = []
        
        # Cache process handle
        self.process = psutil.Process(os.getpid())

    async def start(self):
        """Start the memory monitoring loop."""
        if self.running:
            return
        
        self.running = True
        logger.info(f"Starting MemoryWatchdog (limit={self.soft_limit_mb}MB, interval={self.check_interval}s)")
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        """Stop the memory monitoring loop."""
        if not self.running:
            return
            
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Stopped MemoryWatchdog")
        
    def adjust_threshold(self, mb_offset: int):
        """
        Temporarily adjust the memory limit (e.g., when a heavy model is loaded).
        
        Args:
            mb_offset: MB to add to the limit (can be negative).
        """
        self._dynamic_offset_mb += mb_offset
        logger.debug(f"Memory threshold adjusted by {mb_offset}MB. New offset: {self._dynamic_offset_mb}MB")

    def register_cleanup_task(self, callback: Callable[[], Awaitable[None]]):
        """
        Register an async callback to run periodically (e.g., to check for idle components).
        """
        self._cleanup_tasks.append(callback)

    async def _monitor_loop(self):
        """Async loop to check memory usage and run cleanup tasks."""
        while self.running:
            try:
                # Run registered cleanup tasks first (e.g., might unload a model)
                for task in self._cleanup_tasks:
                    try:
                        await task()
                    except Exception as e:
                        logger.error(f"Error in cleanup task: {e}")

                self.check_memory()
            except Exception as e:
                logger.error(f"Error in MemoryWatchdog loop: {e}")
            
            # Wait for next interval
            try:
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break

    def check_memory(self):
        """
        Checks current RSS memory usage against dynamic limit.
        Triggers GC if usage exceeds limit.
        """
        try:
            rss_bytes = self.process.memory_info().rss
            rss_mb = rss_bytes / (1024 * 1024)
            
            current_limit = self.soft_limit_mb + self._dynamic_offset_mb
            
            if rss_mb > current_limit:
                logger.debug(f"Memory usage ({rss_mb:.2f}MB) exceeds limit ({current_limit}MB). Triggering GC.")
                gc.collect()
                
                # Re-check after GC
                rss_bytes = self.process.memory_info().rss
                rss_mb = rss_bytes / (1024 * 1024)
                
                if rss_mb > current_limit:
                    logger.warning(f"High memory usage: {rss_mb:.2f}MB (Limit: {current_limit}MB) after GC.")
                else:
                    logger.info(f"Memory usage reduced to {rss_mb:.2f}MB after GC.")
        except Exception as e:
            logger.error(f"Error checking memory: {e}")
