# My OOP Task Manager CLI (Week 8)

A command-line interface (CLI) application for managing your daily tasks, built with Object-Oriented Programming (OOP) principles.
This version refactors the Week 7 procedural version (`my-task-manager/`, dictionaries + functions) into
a more organized and scalable structure using `Task` and `TaskManager` classes.

## Features

* **Add Tasks**: Add new tasks with a description (and an optional priority).
* **List Tasks**: View all tasks with ID, description and status.
* **Complete Tasks**: Mark tasks as completed by their ID.
* **Delete Tasks**: Remove tasks by their ID.
* **Extra methods** (used by the tests, ready for a future menu): `search_tasks(keyword)`, `list_tasks(status='pending')`, optional `priority`.
* **Persistence**: Tasks are saved to `data/tasks.json` after every change and loaded automatically on startup.
* **Error handling**: Non-numeric IDs, unknown IDs, empty descriptions, invalid menu choices and a corrupted JSON file never crash the program.

## OOP Design

```text
┌───────────────────────────┐        ┌────────────────────────────────────┐
│ Task                      │        │ TaskManager                        │
├───────────────────────────┤  0..*  ├────────────────────────────────────┤
│ id: int                   │◄───────│ tasks: list[Task]                  │
│ description: str          │        │ next_id: int                       │
│ completed: bool           │        │ data_file: str                     │
│ priority: str             │        ├────────────────────────────────────┤
├───────────────────────────┤        │ add_task(description, priority)    │
│ mark_complete()           │        │ list_tasks(status=None)            │
│ to_dict() / from_dict()   │        │ complete_task(task_id)             │
│ __str__() / __repr__()    │        │ delete_task(task_id)               │
└───────────────────────────┘        │ search_tasks(keyword)              │
                                     │ _load_tasks() / _save_tasks()      │
                                     └────────────────────────────────────┘
```

* **`Task`** bundles one task's data (attributes) with its behaviour (`mark_complete`, `to_dict`), which is *encapsulation*.
* **`TaskManager`** owns the list of `Task` objects and is the only place that reads/writes the JSON file.
* **JSON ↔ objects:** `_save_tasks()` turns each object into a dict with `task.to_dict()`; `_load_tasks()` turns each dict back into an object with `Task.from_dict()`.
* **`__str__` vs `__repr__`:** `print(task)` shows `ID: 1 | Description: ... | Status: Pending`; `repr(task)` shows `Task(id=1, description='...', completed=False, priority='High')` for debugging.

### Procedural (Week 7) vs OOP (Week 8)

| Week 7 | Week 8 |
| :-- | :-- |
| `{"id": 1, "description": "...", "completed": False}` | `Task(1, "...")` |
| `task["completed"] = True` | `task.mark_complete()` |
| `task_logic.add_task(tasks, desc)` + `task_data.save_tasks(tasks)` | `manager.add_task(desc)` (saves automatically) |
| data passed between functions | data lives inside the `TaskManager` object (`self.tasks`) |

The JSON format is the same as Week 7, so the Week 7 `tasks.json` loads directly into `Task` objects.

## How to Run

```bash
cd my-oop-task-manager
python main.py
```
Menu: `1` Add Task · `2` List Tasks · `3` Complete Task · `4` Delete Task · `5` Exit

Run the unit tests:
```bash
python -m unittest discover tests
```
Expected: `Ran 11 tests ... OK`

## Project Structure

```text
my-oop-task-manager/
├── src/
│   ├── __init__.py        # Makes 'src' a Python package
│   ├── task.py            # Defines the Task class
│   └── task_manager.py    # Defines the TaskManager class (core logic and data)
├── data/
│   └── tasks.json         # Stores your tasks (created automatically)
├── tests/
│   └── test_task_manager.py
├── main.py                # CLI entry point
├── .gitignore
└── README.md
```

## Student Information
* **ชื่อ-นามสกุล**: ศุภกร กงชา
* **รหัสนักศึกษา**: 633021103-2
* **กลุ่มเรียน / Section**: Sec. 2
