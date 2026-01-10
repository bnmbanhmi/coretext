import os
import subprocess
import sys

def verify_cleanup():
    errors = []
    
    # Check if extension.yaml exists
    if os.path.exists("extension.yaml"):
        errors.append("❌ extension.yaml still exists in project root")
    
    # Check for references in code/scripts (ignoring this script and history/artifacts if acceptable, 
    # but for now let's be strict on active code)
    
    # files to check specifically
    files_to_check = [
        "scripts/verify_extension_integration.py",
        "tests/test_extension_integration.py",
        "tests/test_scaffolding.py",
        "tests/integration/test_dogfooding_setup.py",
        "README.md",
        "pyproject.toml",
        "_bmad-output/planning-artifacts/project_context.md"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "extension.yaml" in content:
                        errors.append(f"❌ Reference to 'extension.yaml' found in {file_path}")
            except Exception as e:
                errors.append(f"⚠️ Could not read {file_path}: {e}")
                
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    else:
        print("✅ Cleanup verified: extension.yaml removed and references updated.")
        sys.exit(0)

if __name__ == "__main__":
    verify_cleanup()
