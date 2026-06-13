# 📋 Project Tracker CLI

A command-line project management tool for development teams.  
Manage **users**, **projects**, and **tasks** with persistent JSON storage and rich terminal output.

---

## Features

- Create and manage users (with email validation)
- Add projects to users with optional descriptions and due dates
- Add tasks to projects with assignee support
- Mark tasks as complete or update their status
- Search projects by keyword across all users
- Full JSON persistence — data survives between sessions
- Rich colour-coded terminal tables
- 48 unit and integration tests with pytest

---

## Setup

### Requirements

- Python 3.10 or higher
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

All commands follow the pattern:

```bash
python main.py <command> [options]
```

### User Commands

```bash
# Create a user
python main.py add-user --name "Alex" --email alex@dev.io

# List all users
python main.py list-users
```

### Project Commands

```bash
# Add a project to a user
python main.py add-project --user "Alex" --title "CLI Tool" \
    --description "Build the tracker" --due-date 2026-12-31

# List projects for a specific user
python main.py list-projects --user "Alex"

# List projects for all users
python main.py list-projects --all
```

### Task Commands

```bash
# Add a task to a project
python main.py add-task --user "Alex" --project "CLI Tool" \
    --title "Implement add-task" --assigned-to "Alex"

# List tasks in a project
python main.py list-tasks --user "Alex" --project "CLI Tool"

# Mark a task as complete
python main.py complete-task --user "Alex" --project "CLI Tool" \
    --task "Implement add-task"

# Update a task's status  (pending | in-progress | complete)
python main.py update-task --user "Alex" --project "CLI Tool" \
    --task "Write tests" --status in-progress
```

### Search & Delete

```bash
# Search projects by keyword
python main.py search --keyword "API"

# Delete a project from a user
python main.py delete-project --user "Alex" --project "CLI Tool"

# Delete a user (and all their projects/tasks)
python main.py delete-user --user "Jordan"
```

---

## Project Structure

```
project_tracker/
├── main.py                  # CLI entry point (argparse subcommands)
├── requirements.txt         # Dependencies
├── tracker.log              # Debug log (auto-created)
│
├── models/
│   ├── __init__.py
│   ├── person.py            # Base Person class
│   ├── user.py              # User (extends Person) → owns Projects
│   ├── project.py           # Project → owns Tasks
│   └── task.py              # Task with status management
│
├── utils/
│   ├── __init__.py
│   ├── storage.py           # JSON load/save with error handling
│   ├── display.py           # Rich-powered table/panel helpers
│   └── validators.py        # Email, date, non-empty validators
│
├── data/
│   └── tracker_data.json    # Persistent data (auto-created)
│
└── tests/
    ├── __init__.py
    ├── test_models.py            # Unit tests: Person, Task, Project, User
    ├── test_storage_validators.py # Unit tests: storage and validators
    └── test_cli.py               # Integration tests: CLI command handlers
```

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output: **48 passed**.

---

## Object-Oriented Design

| Class | Inherits | Relationship |
|-------|----------|--------------|
| `Person` | — | Base class with name/email |
| `User` | `Person` | One-to-many → `Project` |
| `Project` | — | One-to-many → `Task` |
| `Task` | — | Belongs to one `Project` |

All classes implement:
- `@property` / setter with validation
- `to_dict()` / `from_dict()` for serialisation
- `__repr__` for clean debugging output

---

## Persistence

Data is stored in `data/tracker_data.json` as a JSON array of user objects with nested projects and tasks.  
The file is created automatically on first run. If the file is missing or corrupt, the tool starts with an empty state rather than crashing.

---

## External Packages

| Package | Purpose |
|---------|---------|
| `rich` | Colour-coded terminal tables, panels, and styled messages |
| `pytest` | Unit and integration testing |

---

## Known Issues

- User and project lookup is by name (case-insensitive), so two users cannot share the same name.
- Due dates are stored as plain strings; no overdue warnings are shown yet.
- No interactive/TUI mode — all interaction is via CLI flags.

---

