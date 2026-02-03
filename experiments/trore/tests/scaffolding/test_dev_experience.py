import json
import os

def test_turbo_dev_config():
    if not os.path.exists("turbo.json"):
        raise AssertionError("turbo.json missing")
        
    with open("turbo.json") as f:
        data = json.load(f)
        
    dev_pipeline = data.get("pipeline", {}).get("dev", {})
    if not dev_pipeline.get("persistent"):
        raise AssertionError("turbo dev pipeline not persistent")
    if dev_pipeline.get("cache") is not False:
         raise AssertionError("turbo dev pipeline should not cache")

def test_root_dev_script():
    with open("package.json") as f:
        data = json.load(f)
        
    scripts = data.get("scripts", {})
    if scripts.get("dev") != "turbo dev":
        raise AssertionError("root dev script should be 'turbo dev'")

if __name__ == "__main__":
    try:
        test_turbo_dev_config()
        test_root_dev_script()
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
