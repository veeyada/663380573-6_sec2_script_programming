# Project Plan: Enhanced Task Manager CLI (Final Version)

## 1. Introduction

This document started as the Week 11 plan and now records the final state of the
Enhanced Task Manager CLI: what was built, the problems along the way, and what
comes next.

**Problem statement:** students juggle assignments, exams and personal tasks
with different deadlines and urgency. A plain to-do list cannot answer questions
like "what is due before Friday?" or "what is urgent and still pending?". This
app can.

## 2. Requirements (Status)

### 2.1 Functional

| Requirement | Status |
|---|---|
| Create / list / complete / delete tasks | Done |
| `DueDateTask` and `PriorityTask` types | Done |
| Tags on every task (`add_tag`, `remove_tag`) | Done (+ menu option 10) |
| Search description and tags, case-insensitive, partial | Done |
| Filter: status, due before/after, priority, ALL tags, combined | Done |
| Sort: id, description, completed, due_date, priority, asc/desc | Done |
| Save to / load from `data/tasks.json` | Done |

### 2.2 Non-functional

* **Usability:** numbered menu, `[Success]` / `[Error]` / `[Info]` prefixes,
  re-prompting on invalid input, confirmation before delete.
* **Reliability:** bad input never crashes the app. Corrupted JSON or a single
  broken record does not lose the other tasks. Saving is atomic (temp file +
  `os.replace`).
* **Maintainability:** 4 modules with clear responsibilities, docstrings, PEP 8.
* **Testability:** 26 unit tests using temporary files (the real data is never touched).

## 3. Architecture

```
main.py ──> CLIInterface ──> TaskManager ──> DataPersistence ──> tasks.json
                                  │                │
                                  └──── Task / DueDateTask / PriorityTask
```

* **`task.py`**: data models. Subclasses override `to_dict()` and the
  `_extra_info()` hook used by `__str__`.
* **`data_persistence.py`**: JSON I/O. The `TASK_TYPES` dictionary maps the
  `_type` field to the right class.
* **`task_manager.py`**: all business logic. Returns `(success, message)` tuples
  so it never prints.
* **`cli_interface.py`**: input and output only. Menu choices map to methods
  through a dictionary instead of a long `if/elif` chain.
* **`main.py`**: sets up logging and starts the app.

## 4. Technical Challenges & Solutions

### 4.1 Relative imports broke when running `main.py`
The original template added `src/` to `sys.path` and imported `task_manager`
as a top-level module, but `task_manager.py` uses `from .task import ...`. That
raises *"attempted relative import with no known parent package"*.
**Fix:** put the project root on the path and import `from src.task_manager import TaskManager`,
so `src` is a real package. The tests import the same way.

### 4.2 Polymorphic sorting with missing attributes
Only `DueDateTask` has `due_date` and only `PriorityTask` has `priority`. The
template's trick (`datetime.date.max` / `99` as the key) moves those tasks to the
**top** when `reverse=True`.
**Fix:** split the list into tasks with and without the attribute, sort only the
first group, and always put the second group at the end, sorted by ID. Priorities
use `PRIORITY_MAP = {"High": 1, "Medium": 2, "Low": 3}`, and `id` is the tie-breaker.

### 4.3 Duplicate `__str__` logic
The template rebuilt the string in each subclass by splitting on `" | Tags:"`.
That breaks if a description contains that text.
**Fix:** the base class builds the line once and calls an `_extra_info()` hook that
subclasses override (Template Method pattern).

### 4.4 Tag consistency
Tags typed as `" Study"` and `"study"` were treated as different tags.
**Fix:** `normalize_tag()` (strip + lower) is used everywhere: in the constructor,
`add_tag`, `remove_tag` and filtering. Filtering by tags uses `set.issubset`.

### 4.5 Data safety
One invalid record (for example a priority `"Huge"`) used to make the whole load
fail and return an empty list, and the next save would erase everything.
**Fix:** records are validated one at a time and bad ones are skipped with a
warning. Saving goes through a temp file.

### 4.6 Date filtering
Date filters must ignore tasks that are not `DueDateTask`. `isinstance()` checks
guard the comparison, and the CLI warns if "after" is later than "before".

## 5. Testing

`python -m unittest discover tests` runs 26 tests covering:
* models: tag normalization, date/priority validation, `__str__`, overdue
* persistence: round trip of all 3 types, missing / corrupted files, old records
  without tags, invalid and unknown records
* manager: ID generation, complete/delete edge cases, search, each filter alone
  and combined, every sort criterion in both directions, empty task list

## 6. Lessons Learned

* Building **one feature at a time** and testing it before moving on made bugs
  easy to locate.
* Keeping the CLI separate from the logic made the logic easy to unit test
  without simulating keyboard input.
* Edge cases (an empty list, reverse sort, missing attributes) are where most
  bugs hide, so each one deserves a test.
* `logging` is better than scattered `print()` calls for debugging. It can be
  switched on with `--debug` and stays silent otherwise.

## 7. Future Work

* GUI (Tkinter) or web interface (Flask)
* SQLite storage (only `data_persistence.py` would change)
* Reminders on startup for tasks due within N days
* Recurring tasks, editing existing tasks, CSV export
* For very large lists: keep indexes (for example tag → tasks) instead of
  scanning every task on each search
