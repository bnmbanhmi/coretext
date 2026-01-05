import pytest
from unittest.mock import patch, MagicMock

# We anticipate the module will be here, even if it doesn't exist yet
try:
    from coretext.core.system import process
except ImportError:
    process = None

@pytest.mark.asyncio
async def test_set_background_priority_posix():
    """Test setting background priority on POSIX systems (Linux/macOS)."""
    if process is None:
        pytest.fail("Module coretext.core.system.process not implemented yet")

    mock_process = MagicMock()
    
    with patch("psutil.Process", return_value=mock_process), \
         patch("os.name", "posix"):
        
        process.set_background_priority()
        
        # Verify nice value set to 19
        mock_process.nice.assert_called_with(19)

@pytest.mark.asyncio
async def test_set_background_priority_windows():
    """Test setting background priority on Windows."""
    if process is None:
        pytest.fail("Module coretext.core.system.process not implemented yet")

    mock_process = MagicMock()
    
    # Need to verify what psutil constant is used. 
    # Since we can't import psutil.BELOW_NORMAL_PRIORITY_CLASS on non-Windows easily without mocking,
    # we'll assume the code uses psutil.BELOW_NORMAL_PRIORITY_CLASS.
    # We will mock the module's usage of psutil.
    
    with patch("psutil.Process", return_value=mock_process), \
         patch("os.name", "nt"), \
         patch("coretext.core.system.process.psutil") as mock_psutil_module:
        
        # Setup the constant on the mock
        mock_psutil_module.BELOW_NORMAL_PRIORITY_CLASS = 16384 # specific value doesn't matter as long as it matches
        mock_psutil_module.Process.return_value = mock_process

        process.set_background_priority()
        
        # Verify nice called with the windows constant
        mock_process.nice.assert_called_with(mock_psutil_module.BELOW_NORMAL_PRIORITY_CLASS)
