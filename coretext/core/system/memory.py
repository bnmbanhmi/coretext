import asyncio
import gc
import psutil
import logging
import os

logger = logging.getLogger(__name__)

class MemoryWatchdog:
    def __init__(self, soft_limit_mb: int = 50, check_interval: int = 60):
        self.soft_limit_mb = soft_limit_mb
        self.check_interval = check_interval
        self.running = False
        self._task: asyncio.Task | None = None

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

    async def _monitor_loop(self):
        """Async loop to check memory usage."""
        while self.running:
            try:
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
        Checks current RSS memory usage.
        Triggers GC if usage exceeds limit.
        Logs warning if usage remains high.
        """
        try:
            process = psutil.Process(os.getpid())
            rss_bytes = process.memory_info().rss
            rss_mb = rss_bytes / (1024 * 1024)
            
            if rss_mb > self.soft_limit_mb:
                logger.debug(f"Memory usage ({rss_mb:.2f}MB) exceeds limit ({self.soft_limit_mb}MB). Triggering GC.")
                gc.collect()
                
                # Re-check after GC
                rss_bytes = process.memory_info().rss
                rss_mb = rss_bytes / (1024 * 1024)
                
                if rss_mb > self.soft_limit_mb:
                    logger.warning(f"High memory usage: {rss_mb:.2f}MB (Limit: {self.soft_limit_mb}MB) after GC.")
                else:
                    logger.info(f"Memory usage reduced to {rss_mb:.2f}MB after GC.")
        except Exception as e:
            logger.error(f"Error checking memory: {e}")
