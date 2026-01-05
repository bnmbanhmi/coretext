import os
import psutil
import logging

logger = logging.getLogger(__name__)

def set_background_priority() -> None:
    """
    Sets the current process priority to background/idle levels.
    
    POSIX (Linux/macOS): Sets nice value to 19 (lowest priority).
    Windows: Sets priority class to BELOW_NORMAL_PRIORITY_CLASS.
    """
    try:
        # psutil.Process() targets current process by default
        p = psutil.Process()
        
        if os.name == 'nt':
            # Windows
            if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS'):
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                logger.debug("Set process priority to BELOW_NORMAL_PRIORITY_CLASS")
            else:
                # Fallback or strict failure? 
                # Story says: Windows handles priority differently. Use psutil.BELOW_NORMAL_PRIORITY_CLASS.
                logger.warning("psutil.BELOW_NORMAL_PRIORITY_CLASS not found (are we on Windows?)")
        else:
            # POSIX (Linux/macOS)
            # nice values range from -20 (high) to 19 (low)
            p.nice(19)
            logger.debug("Set process nice value to 19")
            
    except Exception as e:
        logger.warning(f"Failed to set background priority: {e}")
