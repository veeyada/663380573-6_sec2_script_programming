# Final Project: Enhanced Task Manager CLI

**Student:** _(your full name)_ — **Student ID:** _(your ID)_

A command-line application for managing tasks. It brings together the course
topics: Object-Oriented Programming, modular design, JSON data persistence,
`datetime` handling, error handling, and search / filter / sort.

## Implemented Features

* **Task types**: normal `Task`, `DueDateTask` (with a `due_date`), and
  `PriorityTask` (High / Medium / Low).
* **Tags**: add any number of tags to a task. Tags are trimmed, lower-cased and
  never duplicated. Menu option 10 adds or removes a tag on an existing task.
* **CRUD**: add, list, complete and delete tasks (delete asks for confirmation).
* **Search**: case-insensitive partial match on description **and** tags
  (`pres` finds "presentation").
* **Filter**: by completed status, due date on/before, due date on/after,
  priority, and tags (the task must have ALL given tags). All criteria combine
  with AND, and blank fields are skipped.
* **Sort**: by `id`, `description`, `completed`, `due_date`, `priority`,
  ascending or descending. Tasks without a due date / priority always go last.
* **Overdue marker**: pending due-date tasks past their date show `(OVERDUE)`.
* **Persistence**: every change is saved to `data/tasks.json`. Saving writes to a
  temp file first so a crash cannot corrupt the file. On load, a broken record is
  skipped and the rest still load.
* **Input validation**: wrong dates, priorities, IDs or menu choices show an
  error and ask again. The program never crashes on bad input.
* **Logging**: run `python main.py --debug` to see `logging` messages.

## How to Run

```bash
cd final-task-manager-project
python main.py            # start the app
python main.py --debug    # start with log output
python -m unittest discover tests   # run the 26 unit tests
```

Requires Python 3.8+ and no external packages.

## Project Structure

```
final-task-manager-project/
├── src/
│   ├── __init__.py          # Makes 'src' a Python package
│   ├── task.py              # Models: Task, DueDateTask, PriorityTask (with tags)
│   ├── data_persistence.py  # JSON load/save
│   ├── task_manager.py      # Business logic: CRUD, search, filter, sort
│   └── cli_interface.py     # Menu, input validation, output
├── data/
│   └── tasks.json           # Sample tasks for the demo
├── tests/
│   └── test_task_manager.py # Unit tests
├── main.py                  # Entry point
├── .gitignore
├── README.md
└── PLAN.md                  # Plan, challenges, lessons learned
```

**Separation of concerns:** `cli_interface` only talks to the user, `task_manager`
only holds the rules, `data_persistence` only reads and writes files, and `task`
only describes the data. For example, swapping JSON for SQLite would only change
`data_persistence.py`.

## Demo Script (about 3 minutes)

1. `4` List all tasks. Point out the three task types, tags and the `(OVERDUE)` task.
2. `3` Add a priority task with tags, then `4` to show it.
3. `7` Search `pres`: matches by tag, partial and case-insensitive.
4. `8` Filter: Completed `no`, tags `presentation`.
5. `9` Sort by `due_date`: tasks without dates stay at the bottom.
6. `9` Sort by `priority`, descending.
7. `5` Complete a task, then type `abc` as an ID to show the validation.
8. `0` Exit, run again, `4`: the data is still there.

Backup plan: if something breaks, run `python -m unittest discover tests` to show
that every feature is tested.

## Future Work

* GUI (Tkinter) or web interface (Flask)
* SQLite database instead of JSON
* Reminders for tasks due soon
* Recurring tasks
* Editing a task's description / date / priority
* Export to CSV
