# Product Requirements Document (PRD) - Simple ToDo App

## 1. Introduction
**Product Name:** Simple ToDo
**Purpose:** A minimalist command-line interface (CLI) application for managing personal tasks.
**Target Audience:** Developers and power users who prefer terminal-based tools.

## 2. Goals & Objectives
- Provide a fast, keyboard-centric way to manage tasks.
- Ensure data persistence across sessions.
- Maintain a zero-dependency approach where possible (standard libraries preferred).

## 3. Functional Requirements (FRs)
- **FR1 - Add Task:** User can add a new task with a description.
- **FR2 - List Tasks:** User can view a list of all current tasks with their status (pending/completed).
- **FR3 - Complete Task:** User can mark a specific task as completed.
- **FR4 - Delete Task:** User can remove a task from the list.
- **FR5 - Persistence:** Tasks are saved to a local file (JSON) automatically.

## 4. Non-Functional Requirements (NFRs)
- **NFR1 - Performance:** All commands must execute in under 100ms.
- **NFR2 - Compatibility:** Must run on macOS, Linux, and Windows (Python based).
- **NFR3 - Usability:** Help command must provide clear usage instructions.

## 5. Future Scope
- Prioritization (High/Medium/Low)
- Due dates
- Task categories/tags
