# UX Design - Simple ToDo App

## 1. Interaction Principles
- **Speed:** Minimal keystrokes.
- **Clarity:** Output should be readable and concise.
- **Feedback:** Immediate confirmation of actions.

## 2. Command Reference

### 2.1 Add Task
**Input:** `python todo.py add "Buy coffee"`
**Output:** `[+] Task added: Buy coffee (ID: 1)`

### 2.2 List Tasks
**Input:** `python todo.py list`
**Output:**
```text
ID  Status    Description
-------------------------
1   [ ]       Buy coffee
2   [x]       Walk the dog
```

### 2.3 Complete Task
**Input:** `python todo.py complete 1`
**Output:** `[x] Task 1 marked as completed.`

### 2.4 Remove Task
**Input:** `python todo.py delete 1`
**Output:** `[-] Task 1 deleted.`

### 2.5 Help / Invalid
**Input:** `python todo.py` or `python todo.py --help`
**Output:** Standard argparse help message listing available subcommands.
