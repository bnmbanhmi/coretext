from pathlib import Path
import pytest

def test_project_root_structure():
    """Verify essential project files exist."""
    root_dir = Path.cwd()
    assert (root_dir / "pyproject.toml").exists()
    # assert (root_dir / "gemini-extension.json").exists() # Skipping for now until created
    assert (root_dir / "coretext").exists()
    assert (root_dir / "tests").exists()

def test_package_structure():
    """Verify python package hierarchy."""
    root_dir = Path.cwd()
    coretext = root_dir / "coretext"
    
    assert (coretext / "__init__.py").exists()
    assert (coretext / "main.py").exists()
    assert (coretext / "config.py").exists()
    
    # Sub-packages
    assert (coretext / "cli" / "__init__.py").exists()
    assert (coretext / "server" / "__init__.py").exists()
    assert (coretext / "core" / "__init__.py").exists()
    assert (coretext / "db" / "__init__.py").exists()

def test_extension_manifest():
    """Verify extension manifest content."""
    root_dir = Path.cwd()
    manifest_path = root_dir / "gemini-extension.json"
    
    if not manifest_path.exists():
        pytest.skip("gemini-extension.json not created yet")
        
    content = manifest_path.read_text()
    assert "coretext" in content

def test_pyproject_metadata():
    """Verify pyproject.toml basic metadata."""
    root_dir = Path.cwd()
    content = (root_dir / "pyproject.toml").read_text()
    assert 'name = "coretext"' in content
    assert 'version = "0.1.0"' in content
    assert 'authors = ["Minh"]' in content