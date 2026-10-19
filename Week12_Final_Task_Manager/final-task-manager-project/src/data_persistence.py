# final-task-manager-project/src/data_persistence.py
"""JSON load/save for task objects."""
import json
import logging
import os

from .task import Task, DueDateTask, PriorityTask

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Maps the '_type' field in JSON to the class used to rebuild the object
TASK_TYPES = {
    "Task": Task,
    "DueDateTask": DueDateTask,
    "PriorityTask": PriorityTask,
}


class DataPersistence:
    """
    Handles loading and saving of tasks to/from a JSON file.
    Centralizes all file I/O and serialization/deserialization logic.
    """

    def __init__(self, data_file='data/tasks.json'):
        self.data_file = data_file
        # Relative paths are resolved from the project root, so the app works
        # no matter which directory it is started from.
        if os.path.isabs(data_file):
            self._data_file_path = data_file
        else:
            self._data_file_path = os.path.join(PROJECT_ROOT, data_file)

    def load_tasks(self):
        """
        Loads tasks from the JSON file, reconstructing Task objects.
        Handles different task types based on the '_type' field.
        A single broken record is skipped instead of discarding the whole file.
        """
        if not os.path.exists(self._data_file_path):
            return []
        try:
            with open(self._data_file_path, 'r', encoding='utf-8') as f:
                raw_tasks = json.load(f)
        except json.JSONDecodeError:
            print("[Warning] tasks.json is empty or corrupted. "
                  "Starting with an empty task list.")
            return []
        except OSError as e:
            print(f"[Warning] Could not read tasks file: {e}. "
                  "Starting with an empty task list.")
            return []

        if not isinstance(raw_tasks, list):
            print("[Warning] tasks.json has an unexpected format. "
                  "Starting with an empty task list.")
            return []

        loaded_tasks = []
        for t_dict in raw_tasks:
            if not isinstance(t_dict, dict):
                continue
            t_dict = dict(t_dict)
            task_type = t_dict.pop('_type', 'Task')
            # Old files may not have a tags field yet
            t_dict.setdefault('tags', [])
            task_class = TASK_TYPES.get(task_type)
            if task_class is None:
                print(f"[Warning] Unknown task type '{task_type}'. "
                      f"Skipping task ID {t_dict.get('id', 'N/A')}.")
                continue
            try:
                loaded_tasks.append(task_class(**t_dict))
            except (TypeError, ValueError) as e:
                print(f"[Warning] Skipping invalid task ID "
                      f"{t_dict.get('id', 'N/A')}: {e}")
        logger.info("Loaded %d tasks from %s", len(loaded_tasks),
                    self._data_file_path)
        return loaded_tasks

    def save_tasks(self, tasks):
        """
        Saves a list of Task objects to the JSON file.
        Uses the to_dict method of each Task object (polymorphically).
        Writes to a temp file first so a crash cannot corrupt tasks.json.
        """
        tasks_as_dicts = [task.to_dict() for task in tasks]
        os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)
        tmp_path = self._data_file_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(tasks_as_dicts, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, self._data_file_path)
        logger.info("Saved %d tasks", len(tasks_as_dicts))
