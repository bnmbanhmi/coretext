import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from coretext.server.app import app
from coretext.config import Config, SystemConfig

@pytest.fixture
def mock_config():
    config = Config()
    config.system = SystemConfig(memory_limit_mb=100, background_priority=True)
    return config

def test_app_lifespan(mock_config):
    """Test that lifespan events trigger watchdog and priority setting."""
    
    with patch("coretext.server.app.load_config", return_value=mock_config), \
         patch("coretext.server.app.set_background_priority") as mock_set_priority, \
         patch("coretext.server.app.MemoryWatchdog") as MockWatchdog:
        
        mock_watchdog_instance = MockWatchdog.return_value
        mock_watchdog_instance.start = AsyncMock()
        mock_watchdog_instance.stop = AsyncMock()
        
        # TestClient triggers lifespan
        with TestClient(app) as client:
            # Startup checks
            mock_set_priority.assert_called_once()
            MockWatchdog.assert_called_with(soft_limit_mb=100, check_interval=60)
            mock_watchdog_instance.start.assert_awaited_once()
            
            # Make a request to ensure app is running
            _ = client.get("/health")
            # Assuming health endpoint exists, otherwise 404 is fine as long as app runs
            
        # Shutdown checks
        mock_watchdog_instance.stop.assert_awaited_once()

def test_app_lifespan_no_priority(mock_config):
    """Test that set_background_priority is skipped if config is False."""
    mock_config.system.background_priority = False
    
    with patch("coretext.server.app.load_config", return_value=mock_config), \
         patch("coretext.server.app.set_background_priority") as mock_set_priority, \
         patch("coretext.server.app.MemoryWatchdog") as MockWatchdog:
        
        mock_watchdog_instance = MockWatchdog.return_value
        mock_watchdog_instance.start = AsyncMock()
        mock_watchdog_instance.stop = AsyncMock()
        
        with TestClient(app):
            mock_set_priority.assert_not_called()
            mock_watchdog_instance.start.assert_awaited_once()
            
        mock_watchdog_instance.stop.assert_awaited_once()
