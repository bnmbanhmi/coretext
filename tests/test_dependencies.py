import pytest
from pathlib import Path

def test_dependencies_present():
    """Verify critical dependencies are defined in pyproject.toml."""
    root_dir = Path.cwd()
    content = (root_dir / "pyproject.toml").read_text()
    
    required_deps = [
        "fastapi", 
        "typer", 
        "pydantic", 
        "surrealdb", 
        "python-multipart", 
        "uvicorn", 
        "gitpython", 
        "sentence-transformers"
    ]
    
    for dep in required_deps:
        assert dep in content, f"Dependency {dep} is missing from pyproject.toml"
