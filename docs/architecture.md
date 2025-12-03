# System Architecture - Simple ToDo App

## 1. Overview
The system is a Python-based CLI application following a modular design pattern to separate concerns between user interaction, logic, and data storage.

## 2. Technology Stack
- **Language:** Python 3.10+
- **Storage:** Local JSON file (`tasks.json`)
- **Libraries:** `argparse` (standard lib) for CLI parsing.

## 3. Architecture Components

### 3.1 CLI Interface (`cli.py`)
- Handles command-line arguments using `argparse`.
- Routes commands (add, list, done, remove) to the Task Manager.
- Displays output to the console.

### 3.2 Task Manager (`manager.py`)
- Implements the core business logic.
- Maintains the runtime state of tasks.
- Validates inputs (e.g., task index exists).

### 3.3 Storage Service (`storage.py`)
- Handles reading and writing to `tasks.json`.
- Ensures data integrity (valid JSON).
- Handles file creation if it doesn't exist.

## 4. Data Model (`Task` object)
```json
{
  "id": "int (auto-increment or index based)",
  "description": "string",
  "status": "string (pending | completed)",
  "created_at": "ISO-8601 timestamp"
}
```

## 5. Data Flow
1. **User** issues command (e.g., `todo add "Buy milk"`)
2. **CLI** parses arguments.
3. **Manager** creates a new Task object.
4. **Manager** calls **Storage** to save the updated list.
5. **Storage** writes to disk.
6. **CLI** confirms success to User.
