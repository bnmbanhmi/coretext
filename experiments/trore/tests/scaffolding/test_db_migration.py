import os
import sys

# Ensure we can import from apps/api
sys.path.append(os.path.abspath("apps/api"))

def test_db_model_exists():
    path = "apps/api/app/models/listings.py"
    if not os.path.exists(path):
        raise AssertionError(f"Missing model file: {path}")

def test_migration_generated():
    versions_dir = "apps/api/migrations/versions"
    if not os.path.exists(versions_dir):
        raise AssertionError("Missing versions dir")
    
    versions = os.listdir(versions_dir)
    py_files = [f for f in versions if f.endswith(".py")]
    
    if not py_files:
        raise AssertionError("No migration script generated")

if __name__ == "__main__":
    try:
        test_db_model_exists()
        test_migration_generated()
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
