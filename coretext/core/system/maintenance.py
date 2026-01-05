from coretext.core.graph.manager import GraphManager
import logging

logger = logging.getLogger(__name__)

class MaintenanceService:
    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager

    async def run_self_healing(self) -> dict:
        """
        Executes all self-healing routines.
        """
        logger.info("Starting graph self-healing routine...")
        
        try:
            dangling_deleted = await self.graph_manager.prune_dangling_edges()
            orphans_deleted = await self.graph_manager.prune_orphan_headers()
            
            if dangling_deleted > 0 or orphans_deleted > 0:
                logger.info(f"Self-healing complete: Pruned {dangling_deleted} dangling edges, {orphans_deleted} orphan headers.")
            else:
                logger.debug("Self-healing complete: No issues found.")

            # Log warning if counts are high (as per AC)
            if dangling_deleted > 1000:
                 logger.warning(f"High number of dangling edges pruned: {dangling_deleted}. Check for bulk deletion issues.")
            
            return {
                "dangling_edges_removed": dangling_deleted,
                "orphan_headers_removed": orphans_deleted
            }
        except Exception as e:
            logger.error(f"Error during self-healing routine: {e}")
            # Do not crash startup, just return empty report or re-raise if critical?
            # AC says "non-blocking background task". If it fails, log it.
            return {
                "dangling_edges_removed": 0,
                "orphan_headers_removed": 0,
                "error": str(e)
            }