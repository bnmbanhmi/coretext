import os
import json
import tomllib

def test_root_files_exist():
    required_files = [
        "package.json",
        "pnpm-workspace.yaml",
        "turbo.json",
        "pyproject.toml",
        ".gitignore"
    ]
    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)
    
    assert not missing, f"Missing root files: {missing}"

def test_package_json_valid():
    if not os.path.exists("package.json"):
        return
    with open("package.json") as f:
        data = json.load(f)
    assert data.get("name") == "trore"
    assert data.get("private") is True

def test_turbo_json_valid():
    if not os.path.exists("turbo.json"):
        return
    with open("turbo.json") as f:
        data = json.load(f)
    assert "$schema" in data

if __name__ == "__main__":
    # minimal runner
    try:
        test_root_files_exist()
        test_package_json_valid()
        test_turbo_json_valid()
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
