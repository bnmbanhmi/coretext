import os
import json
import tomllib

def test_web_files_exist():
    base = "apps/web"
    required = [
        "package.json",
        "vite.config.ts",
        "src/features",
        "src/components",
        "src/lib",
        "tailwind.config.js",
        "postcss.config.js"
    ]
    missing = []
    for r in required:
        path = os.path.join(base, r)
        if not os.path.exists(path):
            missing.append(path)
    
    assert not missing, f"Missing web files: {missing}"

def test_web_dependencies():
    path = "apps/web/package.json"
    if not os.path.exists(path):
        return
    with open(path) as f:
        data = json.load(f)
    
    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}
    
    required = [
        "react",
        "react-dom",
        "zustand",
        "@tanstack/react-query",
        "react-router-dom",
        "tailwindcss",
        "vite",
        "typescript"
    ]
    
    missing = [d for d in required if d not in all_deps]
    assert not missing, f"Missing dependencies in apps/web/package.json: {missing}"

if __name__ == "__main__":
    try:
        test_web_files_exist()
        test_web_dependencies()
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
