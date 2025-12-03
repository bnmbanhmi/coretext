import unittest
import os
import json
from storage import load_tasks, save_tasks, TASKS_FILE # Assuming TASKS_FILE is defined in storage.py

class TestStorage(unittest.TestCase):

    def setUp(self):
        """Set up a clean environment for each test."""
        self.test_file_path = os.path.join(os.getcwd(), TASKS_FILE)
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def tearDown(self):
        """Clean up the environment after each test."""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_ac1_load_tasks_creates_file_if_not_exists(self):
        """AC 1: On first run, tasks.json is created with content []."""
        tasks = load_tasks()
        self.assertEqual(tasks, [])
        self.assertTrue(os.path.exists(self.test_file_path))
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            self.assertEqual(content, [])

    def test_ac2_load_tasks_returns_list_if_data_exists(self):
        """AC 2: load_tasks() returns a list of dicts if data exists."""
        sample_data = [{"id": 1, "description": "Buy milk", "status": "pending"}]
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f)
        
        tasks = load_tasks()
        self.assertEqual(tasks, sample_data)

    def test_ac3_save_tasks_writes_valid_json(self):
        """AC 3: save_tasks() writes valid JSON to disk."""
        sample_data = [{"id": 1, "description": "Learn Python", "status": "completed"}]
        save_tasks(sample_data)
        
        self.assertTrue(os.path.exists(self.test_file_path))
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            content = json.load(f) # This will raise ValueError if not valid JSON
            self.assertEqual(content, sample_data)

    def test_ac4_save_tasks_persists_exact_data(self):
        """AC 4: save_tasks() persists exact data passed to it."""
        sample_data = [
            {"id": 1, "description": "Task A", "status": "pending"},
            {"id": 2, "description": "Task B", "status": "completed"}
        ]
        save_tasks(sample_data)
        loaded_data = load_tasks()
        self.assertEqual(loaded_data, sample_data)

    def test_load_tasks_corrupt_json_handling(self):
        """Test handling of corrupt JSON by load_tasks."""
        # Ensure file does not exist initially
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

        # Create a corrupt JSON file
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write("{invalid json")

        # Call load_tasks - it should handle the corruption and overwrite the file
        tasks = load_tasks()
        self.assertEqual(tasks, []) # Verify it returns an empty list

        # Now, verify that the file content was fixed by load_tasks
        self.assertTrue(os.path.exists(self.test_file_path))
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            content_str = f.read()
            self.assertEqual(content_str.strip(), "[]") # Check for exact string "[]"

        # Optionally, try to load it as JSON again to be super sure
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            content_json = json.load(f)
            self.assertEqual(content_json, [])


if __name__ == '__main__':
    unittest.main()
