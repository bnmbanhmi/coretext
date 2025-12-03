# coretext - Epic Breakdown

**Author:** Minh
**Date:** 2025-12-03
**Project Level:** Intermediate
**Target Scale:** MVP

---

## Overview

This document provides the complete epic and story breakdown for coretext (Simple ToDo App), decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

**Living Document Notice:** This is the initial version. It incorporates interactions from UX Design and technical details from Architecture documents.

### Context Validation
✅ **PRD.md**: Loaded (5 FRs)
✅ **Architecture.md**: Loaded (Components, Data Model, Flow)
✅ **UX Design.md**: Loaded (Command Reference, Principles)

---

## Functional Requirements Inventory

| ID | Requirement | Description |
|:---|:---|:---|
| **FR1** | Add Task | User can add a new task with a description. |
| **FR2** | List Tasks | User can view a list of all current tasks with their status (pending/completed). |
| **FR3** | Complete Task | User can mark a specific task as completed. |
| **FR4** | Delete Task | User can remove a task from the list. |
| **FR5** | Persistence | Tasks are saved to a local file (JSON) automatically. |

---

## FR Coverage Map

_This section will be populated as epics are defined._

---

## Epic Structure Plan

To deliver user value incrementally while respecting the architectural layers, we will break the project into two main epics:

### **Epic 1: Core Infrastructure & Task Management Foundation**
**User Value:** Users can start using the tool to persist, add, and view tasks immediately.
**Technical Context:** Sets up the `Task` model, `Storage` service for JSON persistence, and the base `Manager` logic. Implements the CLI skeleton.
**UX Integration:** Implements `add` and `list` commands with defined output formats.
**Dependencies:** None.

### **Epic 2: Task Lifecycle Management**
**User Value:** Users can manage the lifecycle of tasks by marking them complete or removing them.
**Technical Context:** Extends `Manager` and `CLI` to handle updates and deletions, updating the JSON store.
**UX Integration:** Implements `complete` and `delete` commands.
**Dependencies:** Epic 1.

---

## Technical Context Summary

**Architecture Alignment:**
- **Language**: Python 3.10+
- **Storage**: `tasks.json` managed by `storage.py`
- **Logic**: `manager.py` handles business rules
- **Interface**: `cli.py` uses `argparse`

**Data Model Implementation:**
- Fields: `id`, `description`, `status`, `created_at`
- ID Strategy: Auto-increment or index-based (Architecture 4.0)

---

## Epic 1: Core Infrastructure & Task Management Foundation

**Goal:** Establish the project structure, storage mechanism, and basic "Add/List" functionality so users can begin tracking tasks.

### Story 1.1: Project Setup & Storage Service

As a developer/user,
I want a reliable storage system that initializes the data file,
So that my tasks are saved to disk and persist between sessions.

**Acceptance Criteria:**
**Given** the application is run for the first time
**When** the `Storage` service is initialized
**Then** it should check if `tasks.json` exists
**And** if not, create an empty valid JSON file (e.g., `[]`)

**Given** existing data in `tasks.json`
**When** `load_tasks()` is called
**Then** it returns a list of Task dictionaries

**Given** a list of tasks
**When** `save_tasks(tasks)` is called
**Then** the list is written to `tasks.json` as valid JSON

**Technical Notes:**
- Create `storage.py` module.
- Implement `save_tasks(data)` and `load_tasks()`.
- Ensure file permissions are handled gracefully.
- **Architecture:** Section 3.3 (Storage Service).

---

### Story 1.2: Task Manager & Add Command

As a user,
I want to add a new task via the CLI,
So that I can record things I need to do.

**Acceptance Criteria:**
**Given** the CLI is ready
**When** I run `python todo.py add "Buy coffee"`
**Then** a new task object is created with:
  - `id`: unique integer (incrementing)
  - `description`: "Buy coffee"
  - `status`: "pending"
  - `created_at`: current ISO timestamp
**And** the task is saved to storage
**And** the output displays: `[+] Task added: Buy coffee (ID: 1)`

**Technical Notes:**
- Create `manager.py` with `add_task(description)`.
- Create `cli.py` with `argparse` setup for `add` subcommand.
- **UX:** Matches Section 2.1 (Add Task).
- **Architecture:** Sections 3.1 (CLI) & 3.2 (Manager).
- **Prerequisite:** Story 1.1

---

### Story 1.3: List Tasks Command

As a user,
I want to see a list of my tasks,
So that I know what is pending and what is done.

**Acceptance Criteria:**
**Given** I have tasks in the system
**When** I run `python todo.py list`
**Then** the system reads from storage
**And** prints a formatted table with columns: ID, Status, Description
**And** "pending" tasks show as `[ ]`
**And** "completed" tasks show as `[x]`

**Given** no tasks exist
**When** I run `python todo.py list`
**Then** it displays a friendly message (e.g., "No tasks found.")

**Technical Notes:**
- Implement `list_tasks()` in `manager.py`.
- Add `list` subcommand to `cli.py`.
- Format output to match UX specs.
- **UX:** Matches Section 2.2 (List Tasks).
- **Prerequisite:** Story 1.2

<!-- End story repeat -->

---

## Epic 2: Task Lifecycle Management

**Goal:** Enable users to maintain their task list by completing finished items and removing unwanted ones.

### Story 2.1: Complete Task Command

As a user,
I want to mark a task as completed,
So that I can track my progress.

**Acceptance Criteria:**
**Given** a task with ID 1 exists and is "pending"
**When** I run `python todo.py complete 1`
**Then** the task status updates to "completed"
**And** the change is persisted to disk
**And** the output shows: `[x] Task 1 marked as completed.`

**Given** I try to complete a non-existent ID
**When** I run `python todo.py complete 99`
**Then** an error message is displayed: "Error: Task 99 not found."

**Technical Notes:**
- Implement `complete_task(task_id)` in `manager.py`.
- Add `complete` subcommand to `cli.py`.
- Validate ID existence before update.
- **UX:** Matches Section 2.3 (Complete Task).
- **Prerequisite:** Epic 1.

---

### Story 2.2: Delete Task Command

As a user,
I want to remove a task entirely,
So that I can declutter my list.

**Acceptance Criteria:**
**Given** a task with ID 1 exists
**When** I run `python todo.py delete 1`
**Then** the task is removed from the list
**And** the file is updated
**And** the output shows: `[-] Task 1 deleted.`

**Given** I try to delete a non-existent ID
**When** I run `python todo.py delete 99`
**Then** an error message is displayed: "Error: Task 99 not found."

**Technical Notes:**
- Implement `delete_task(task_id)` in `manager.py`.
- Add `delete` subcommand to `cli.py`.
- **UX:** Matches Section 2.4 (Remove Task).
- **Prerequisite:** Story 2.1 (reuses ID validation logic).

---

## FR Coverage Matrix

| Requirement | Covered By | Status |
|:---|:---|:---|
| **FR1 - Add Task** | Epic 1, Story 1.2 | ✅ Planned |
| **FR2 - List Tasks** | Epic 1, Story 1.3 | ✅ Planned |
| **FR3 - Complete Task** | Epic 2, Story 2.1 | ✅ Planned |
| **FR4 - Delete Task** | Epic 2, Story 2.2 | ✅ Planned |
| **FR5 - Persistence** | Epic 1, Story 1.1 | ✅ Planned |

---

## Summary

This breakdown translates the 5 Functional Requirements into 5 actionable stories across 2 Epics.
- **Epic 1** builds the engine and basic IO.
- **Epic 2** adds the state management logic.

All stories are independent enough for a single developer to execute in a short session (Quick Flow), fully aligned with the Architecture and UX specs.

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._