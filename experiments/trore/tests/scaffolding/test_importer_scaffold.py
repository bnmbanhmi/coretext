import os

def test_importer_structure():
    base = "packages/importer"
    required = [
        "Dockerfile",
        "main.py",
        "src"
    ]
    
    missing = []
    for r in required:
        path = os.path.join(base, r)
        if not os.path.exists(path):
            missing.append(path)
            
    assert not missing, f"Missing importer files: {missing}"

if __name__ == "__main__":
    try:
        test_importer_structure()
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
