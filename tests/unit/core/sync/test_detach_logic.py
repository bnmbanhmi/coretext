import pytest
from coretext.core.sync.engine import SyncEngine

def test_sync_engine_constants():
    """Test that SyncEngine defines the required constants."""
    assert hasattr(SyncEngine, "SYNC_ASYNC_THRESHOLD_FILES")
    assert SyncEngine.SYNC_ASYNC_THRESHOLD_FILES == 5

def test_sync_engine_should_detach():
    """Test the logic for determining when to detach."""
    # Below threshold
    assert SyncEngine.should_detach(1) is False
    assert SyncEngine.should_detach(4) is False
    assert SyncEngine.should_detach(5) is False # Boundary condition - exact threshold is usually "inclusive" or "exclusive". Story says "> 5" or ">= 5"? 
    # Story: " > 10 files" (example in AC). "SYNC_ASYNC_THRESHOLD_FILES = 5" (Task).
    # Usually "threshold" means if >= threshold. Or if > threshold. 
    # timeout_utils.py says: if len(file_paths) > FILE_COUNT_DETACH_THRESHOLD. (Exclusive)
    # I'll stick to > threshold for now to match timeout_utils.py behavior, or >= if typical.
    # Let's assume > threshold as per timeout_utils.
    
    # Above threshold
    assert SyncEngine.should_detach(6) is True
    assert SyncEngine.should_detach(100) is True
