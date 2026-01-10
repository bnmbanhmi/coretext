import pytest
import subprocess
from pathlib import Path
from coretext.config import load_config
import shutil

@pytest.fixture
def temp_pollution_file():
    """Creates a temporary markdown file in a code directory."""
    project_root = Path.cwd()
    target_dir = project_root / "coretext" / "templates"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    pollution_file = target_dir / "pollution_test.md"
    pollution_file.write_text("# Pollution Test\nShould be blocked.")
    
    yield pollution_file
    
    if pollution_file.exists():
        pollution_file.unlink()

def test_sync_enforcement_blocks_code_directory(temp_pollution_file):
    """Verify that sync prevents indexing outside _coretext-knowledge."""
    project_root = Path.cwd()
    config = load_config(project_root)
    
    # Ensure config is set to a specific dir (not root)
    if config.docs_dir == ".":
        pytest.skip("Configured docs_dir is root (.), cannot test enforcement.")

    target_dir = temp_pollution_file.parent
    
    result = subprocess.run(
        ["poetry", "run", "coretext", "sync", "--dir", str(target_dir), "--project-root", str(project_root)],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 1, "Sync should fail with exit code 1"
    assert "Security Error" in result.stdout
    assert "restricted to configured docs directory" in result.stdout

def test_sync_allows_knowledge_directory():
    """Verify that sync allows the configured knowledge directory."""
    project_root = Path.cwd()
    config = load_config(project_root)
    docs_root = project_root / config.docs_dir
    
    if not docs_root.exists():
        pytest.skip(f"{docs_root} does not exist")

    result = subprocess.run(
        ["poetry", "run", "coretext", "sync", "--dir", str(docs_root), "--project-root", str(project_root)],
        capture_output=True,
        text=True
    )
    
    # It might fail if daemon is down, but it shouldn't be the Security Error
    if result.returncode != 0:
        # If it failed, check it wasn't the security error
        assert "Security Error" not in result.stdout
    else:
        assert "Successfully synced" in result.stdout or "No files found" in result.stdout
