import os
import tomllib

def test_api_structure():
    base = "apps/api"
    required_dirs = [
        "app/core",
        "app/db",
        "app/models",
        "app/schemas",
        "app/api"
    ]
    required_files = [
        "pyproject.toml",
        "app/main.py",
        "vercel.json",
        "alembic.ini"
    ]
    
    missing = []
    for d in required_dirs:
        path = os.path.join(base, d)
        if not os.path.exists(path):
            missing.append(path)
            
    for f in required_files:
        path = os.path.join(base, f)
        if not os.path.exists(path):
            missing.append(path)
            
    assert not missing, f"Missing api structure: {missing}"

def test_api_dependencies():
    path = "apps/api/pyproject.toml"
    if not os.path.exists(path):
        return
        
    with open(path, "rb") as f:
        data = tomllib.load(f)
        
    deps = data.get("project", {}).get("dependencies", [])
    required = [
        "fastapi",
        "pydantic",
        "sqlalchemy",
        "alembic",
        "psycopg2-binary", 
        "python-dotenv"
    ]
    
    missing = []
    dep_str = " ".join(deps)
    for r in required:
        if r not in dep_str:
             missing.append(r)
             
    assert not missing, f"Missing dependencies in apps/api/pyproject.toml: {missing}"

if __name__ == "__main__":
    try:
        test_api_structure()
        test_api_dependencies()
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
