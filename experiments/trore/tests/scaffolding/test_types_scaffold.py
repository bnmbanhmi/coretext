import os

def test_types_structure():
    base = "packages/types"
    required = [
        "package.json",
        "index.d.ts",
        "tsconfig.json"
    ]
    
    missing = []
    for r in required:
        path = os.path.join(base, r)
        if not os.path.exists(path):
            missing.append(path)
            
    assert not missing, f"Missing types files: {missing}"

if __name__ == "__main__":
    try:
        test_types_structure()
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
