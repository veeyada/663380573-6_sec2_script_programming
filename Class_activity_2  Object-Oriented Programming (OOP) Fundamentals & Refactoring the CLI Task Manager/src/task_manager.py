# my-oop-task-manager/src/task_manager.py
"""Defines the TaskManager class: owns the list of Task objects and their persistence."""
import json
import os

from .task import Task  # Import the Task class from the same package

# Project root = the folder that contains src/ (so paths work from any working directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TaskManager:
    """
    Manages the collection of Task objects, including loading, saving,
    and performing operations like add, list, complete, and delete.
    """

    def __init__(self, data_file='data/tasks.json'):
        """
        Initializes the TaskManager.
        Loads tasks from the specified data file or starts with an empty list.
        """
        self.data_file = data_file if os.path.isabs(data_file) else os.path.join(PROJECT_ROOT, data_file)
        self.tasks = self._load_tasks()
        self.next_id = self._get_next_task_id()

    # ------------------------------------------------------------------ internal helpers
    def _get_next_task_id(self):
        """Generates the next unique ID for a new task."""
        return max((task.id for task in self.tasks), default=0) + 1

    def _find_task(self, task_id):
        """Returns the Task with this ID, or None if it does not exist."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def _load_tasks(self):
        """
        Internal method to load tasks from the JSON file.
        Converts dictionaries from JSON back into Task objects.
        """
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                raw_tasks = json.load(f)
        except json.JSONDecodeError:
            print(f"[Warning] '{self.data_file}' is not valid JSON. Starting with an empty task list.")
            return []
        except OSError as e:
            print(f"[Error] Could not read '{self.data_file}': {e}")
            return []

        if not isinstance(raw_tasks, list):
            print("[Warning] Task file does not contain a list. Starting with an empty task list.")
            return []

        tasks = []
        for item in raw_tasks:
            try:
                tasks.append(Task.from_dict(item))
            except (KeyError, TypeError, ValueError):
                print(f"[Warning] Skipping malformed task record: {item}")
        return tasks

    def _save_tasks(self):
        """
        Internal method to save tasks to the JSON file.
        Converts Task objects to dictionaries before saving.
        """
        tasks_as_dicts = [task.to_dict() for task in self.tasks]
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_as_dicts, f, indent=4, ensure_ascii=False)
            return True
        except OSError as e:
            print(f"[Error] Could not save tasks: {e}")
            return False

    # ------------------------------------------------------------------ public operations
    def add_task(self, description, priority="Medium"):
        """Creates a new Task object, adds it to self.tasks, and saves. Returns the Task (or None)."""
        description = description.strip()
        if not description:
            print("[Error] Task description cannot be empty.")
            return None
        new_task = Task(self.next_id, description, priority=priority.strip().capitalize() or "Medium")
        self.tasks.append(new_task)
        self.next_id += 1
        self._save_tasks()
        print(f"Task '{description}' added with ID {new_task.id}.")
        return new_task

    def list_tasks(self, status=None):
        """
        Prints tasks using Task.__str__.
        status: None = all, 'pending' or 'completed' to filter.
        """
        tasks = self.tasks
        if status == "pending":
            tasks = [t for t in self.tasks if not t.completed]
        elif status == "completed":
            tasks = [t for t in self.tasks if t.completed]

        if not tasks:
            print("No tasks found.")
            return
        print("\n--- Your Tasks ---")
        for task in tasks:
            print(task)  # print() calls Task.__str__
        print("-" * 18)

    def search_tasks(self, keyword):
        """Returns tasks whose description contains the keyword (case-insensitive)."""
        keyword = keyword.strip().lower()
        return [t for t in self.tasks if keyword and keyword in t.description.lower()]

    def complete_task(self, task_id):
        """Finds a task by ID, calls task.mark_complete(), and saves. Returns True if found."""
        task = self._find_task(task_id)
        if task is None:
            print(f"Task with ID {task_id} not found.")
            return False
        if task.completed:
            print(f"[Info] Task {task_id} is already completed.")
            return True
        task.mark_complete()  # Use the Task object's method
        self._save_tasks()
        print(f"Task {task_id} marked as complete.")
        return True

    def delete_task(self, task_id):
        """Finds a task by ID, removes it from self.tasks, and saves. Returns True if found."""
        task = self._find_task(task_id)
        if task is None:
            print(f"Task with ID {task_id} not found.")
            return False
        self.tasks.remove(task)
        self._save_tasks()
        print(f"Task {task_id} deleted.")
        return True
