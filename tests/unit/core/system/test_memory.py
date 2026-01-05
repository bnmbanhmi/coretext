import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Anticipate module existence
try:
    from coretext.core.system import memory
except ImportError:
    memory = None

@pytest.mark.asyncio
async def test_memory_watchdog_initialization():
    if memory is None:
        pytest.fail("Module coretext.core.system.memory not implemented")
    
    with patch("psutil.Process"): # Mock process in init
        watchdog = memory.MemoryWatchdog(soft_limit_mb=100, check_interval=30)
        assert watchdog.soft_limit_mb == 100
        assert watchdog.check_interval == 30
        assert not watchdog.running
        assert watchdog._dynamic_offset_mb == 0

@pytest.mark.asyncio
async def test_check_memory_under_limit():
    if memory is None:
        pytest.fail("Module coretext.core.system.memory not implemented")

    with patch("psutil.Process") as mock_proc_cls:
        mock_process = MagicMock()
        mock_proc_cls.return_value = mock_process
        
        watchdog = memory.MemoryWatchdog(soft_limit_mb=50)
        
        # 40MB usage (under 50MB)
        mock_process.memory_info.return_value.rss = 40 * 1024 * 1024 
        
        with patch("gc.collect") as mock_gc:
            watchdog.check_memory()
            mock_gc.assert_not_called()

@pytest.mark.asyncio
async def test_check_memory_dynamic_limit():
    """Test that dynamic offset increases the allowed limit."""
    if memory is None:
        pytest.fail("Module coretext.core.system.memory not implemented")

    with patch("psutil.Process") as mock_proc_cls:
        mock_process = MagicMock()
        mock_proc_cls.return_value = mock_process
        
        watchdog = memory.MemoryWatchdog(soft_limit_mb=50)
        
        # Adjust limit by +100MB
        watchdog.adjust_threshold(100)
        
        # 120MB usage (Over 50, but under 150)
        mock_process.memory_info.return_value.rss = 120 * 1024 * 1024 
        
        with patch("gc.collect") as mock_gc:
            watchdog.check_memory()
            mock_gc.assert_not_called()
            
        # Revert limit
        watchdog.adjust_threshold(-100)
         # 120MB usage (Over 50)
        with patch("gc.collect") as mock_gc:
            watchdog.check_memory()
            mock_gc.assert_called()

@pytest.mark.asyncio
async def test_cleanup_tasks_execution():
    """Test that registered cleanup tasks are awaited during loop."""
    if memory is None:
        pytest.fail("Module coretext.core.system.memory not implemented")

    with patch("psutil.Process"):
        watchdog = memory.MemoryWatchdog(check_interval=0.01)
        
        mock_task = AsyncMock()
        watchdog.register_cleanup_task(mock_task)
        
        with patch.object(watchdog, 'check_memory'):
            await watchdog.start()
            await asyncio.sleep(0.05)
            await watchdog.stop()
            
            assert mock_task.call_count >= 1

@pytest.mark.asyncio
async def test_check_memory_over_limit_recovers():
    """Test that GC is triggered when over limit, and if it recovers, no warning."""
    if memory is None:
        pytest.fail("Module coretext.core.system.memory not implemented")

    with patch("psutil.Process") as mock_proc_cls:
        mock_process = MagicMock()
        mock_proc_cls.return_value = mock_process
        
        watchdog = memory.MemoryWatchdog(soft_limit_mb=50)
        
        # First call: 60MB (over), Second call: 45MB (under)
        mock_process.memory_info.side_effect = [
            MagicMock(rss=60 * 1024 * 1024),
            MagicMock(rss=45 * 1024 * 1024)
        ]
        
        with patch("gc.collect") as mock_gc, \
             patch("coretext.core.system.memory.logger") as mock_logger:
            
            watchdog.check_memory()
            
            # Should trigger GC
            mock_gc.assert_called_once()
            # Should NOT log warning about high memory (only maybe debug info)
            mock_logger.warning.assert_not_called()

@pytest.mark.asyncio
async def test_check_memory_over_limit_remains_high():
    """Test that warning is logged if memory remains high after GC."""
    if memory is None:
        pytest.fail("Module coretext.core.system.memory not implemented")

    with patch("psutil.Process") as mock_proc_cls:
        mock_process = MagicMock()
        mock_proc_cls.return_value = mock_process

        watchdog = memory.MemoryWatchdog(soft_limit_mb=50)
        
        # First call: 60MB, Second call: 55MB (still over)
        mock_process.memory_info.side_effect = [
            MagicMock(rss=60 * 1024 * 1024),
            MagicMock(rss=55 * 1024 * 1024)
        ]
        
        with patch("gc.collect") as mock_gc, \
             patch("coretext.core.system.memory.logger") as mock_logger:
            
            watchdog.check_memory()
            
            # Should trigger GC
            mock_gc.assert_called_once()
            # Should log warning
            mock_logger.warning.assert_called_once()

@pytest.mark.asyncio
async def test_watchdog_loop():
    """Test that start creates a task and runs loop."""
    if memory is None:
        pytest.fail("Module coretext.core.system.memory not implemented")

    with patch("psutil.Process"):
        # Use small interval
        watchdog = memory.MemoryWatchdog(check_interval=0.001)
        
        with patch.object(watchdog, 'check_memory') as mock_check:
            
            await watchdog.start()
            # Sleep a bit to allow loop to run
            await asyncio.sleep(0.01)
            
            assert watchdog.running
            assert mock_check.called
            
            await watchdog.stop()
            assert not watchdog.running
