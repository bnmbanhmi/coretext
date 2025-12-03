import json
import os

TASKS_FILE = "tasks.json"

def _get_file_path():
    """Returns the absolute path to the tasks.json file."""
    # Using the current working directory for simplicity as per tech spec
    return os.path.join(os.getcwd(), TASKS_FILE)

def load_tasks() -> list[dict]:
    """Loads tasks from the JSON file. Creates an empty file if it doesn't exist."""
    file_path = _get_file_path()
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {TASKS_FILE} is corrupt. Starting with an empty task list.")
        # Overwrite corrupt file with an empty list to fix it
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
        return []


def save_tasks(tasks: list[dict]) -> None:
    """Saves the given list of tasks to the JSON file."""
    file_path = _get_file_path()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=4)

if __name__ == "__main__":
    # Simple test to check functionality
    print("Running basic storage tests...")
    test_file = _get_file_path()
    if os.path.exists(test_file):
        os.remove(test_file)

    # Test load_tasks on empty/non-existent file
    tasks = load_tasks()
    assert tasks == [], f"Expected [], got {tasks}"
    print("  ✓ load_tasks (empty/new file)")

    # Test save_tasks and then load
    sample_tasks = [{"id": 1, "description": "Test Task", "status": "pending"}]
    save_tasks(sample_tasks)
    loaded_tasks = load_tasks()
    assert loaded_tasks == sample_tasks, f"Expected {sample_tasks}, got {loaded_tasks}"
    print("  ✓ save_tasks and load_tasks (roundtrip)")

    # Test handling of corrupt JSON (simulate)
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("{invalid json")
    corrupt_tasks = load_tasks()
    assert corrupt_tasks == [], f"Expected [], got {corrupt_tasks}"
    print("  ✓ load_tasks (corrupt JSON handling)")

    if os.path.exists(test_file):
        os.remove(test_file)
    print("Basic storage tests complete.")
