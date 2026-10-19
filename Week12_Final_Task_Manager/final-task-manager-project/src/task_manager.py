# final-task-manager-project/src/task_manager.py
"""Business logic: add, list, complete, delete, search, filter, sort."""
import logging

from .task import Task, DueDateTask, PriorityTask, normalize_tag
from .data_persistence import DataPersistence

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages the collection of various Task objects.
    Focuses on business logic: add, list, complete, delete, search, filter, sort.
    """

    PRIORITY_MAP = {"High": 1, "Medium": 2, "Low": 3}
    SORT_CRITERIA = ("id", "description", "completed", "due_date", "priority")

    def __init__(self, data_file='data/tasks.json'):
        self.persistence = DataPersistence(data_file)
        self.tasks = self.persistence.load_tasks()
        self.next_id = self._get_next_task_id()

    def _get_next_task_id(self):
        """Generates the next unique ID for a new task."""
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def _save_changes(self):
        """Internal helper to save tasks via the persistence layer."""
        self.persistence.save_tasks(self.tasks)

    def _add(self, task):
        """Stores a newly created task, advances the ID counter and saves."""
        self.tasks.append(task)
        self.next_id += 1
        self._save_changes()
        logger.info("Added %r", task)
        return task

    # --- Basic CRUD Operations ---
    def add_normal_task(self, description, tags=None):
        return self._add(Task(self.next_id, description, tags=tags))

    def add_due_date_task(self, description, due_date, tags=None):
        """Returns the new task, or None if the date is invalid."""
        try:
            task = DueDateTask(self.next_id, description, due_date, tags=tags)
        except (ValueError, TypeError):
            logger.error("Invalid due date: %r", due_date)
            return None
        return self._add(task)

    def add_priority_task(self, description, priority, tags=None):
        """Returns the new task, or None if the priority is invalid."""
        try:
            task = PriorityTask(self.next_id, description, priority, tags=tags)
        except ValueError:
            logger.error("Invalid priority: %r", priority)
            return None
        return self._add(task)

    def get_task_by_id(self, task_id):
        """Helper to find a task by ID."""
        return next((task for task in self.tasks if task.id == task_id), None)

    def complete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"Task ID {task_id} not found."
        if task.completed:
            return False, f"Task ID {task_id} is already completed."
        task.mark_complete()
        self._save_changes()
        return True, f"Task ID {task_id} marked as completed."

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"Task ID {task_id} not found."
        self.tasks.remove(task)
        self._save_changes()
        return True, f"Task ID {task_id} deleted successfully."

    def add_tag_to_task(self, task_id, tag):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"Task ID {task_id} not found."
        if not normalize_tag(tag):
            return False, "Tag cannot be empty."
        task.add_tag(tag)
        self._save_changes()
        return True, f"Tags for task ID {task_id}: {', '.join(task.tags)}"

    def remove_tag_from_task(self, task_id, tag):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"Task ID {task_id} not found."
        if not task.remove_tag(tag):
            return False, f"Task ID {task_id} has no tag '{normalize_tag(tag)}'."
        self._save_changes()
        return True, f"Tag removed from task ID {task_id}."

    # --- Search / Filter / Sort ---
    def get_all_tasks(self):
        """Returns a copy of all tasks. Useful for listing."""
        return list(self.tasks)

    def search_tasks(self, keyword):
        """
        Searches tasks by keyword in description or tags.
        Case-insensitive, partial matches ("pres" matches "presentation").
        """
        keyword = (keyword or "").strip().lower()
        if not keyword:
            return []
        return [
            task for task in self.tasks
            if keyword in task.description.lower()
            or any(keyword in tag.lower() for tag in task.tags)
        ]

    def filter_tasks(self, status=None, due_date_before=None,
                     due_date_after=None, priority_level=None,
                     contains_tags=None):
        """
        Filters tasks by various criteria. All given criteria are combined (AND).

        Args:
            status (bool, optional): True for completed, False for pending.
            due_date_before (datetime.date, optional): due on or before this date.
            due_date_after (datetime.date, optional): due on or after this date.
            priority_level (str, optional): "High", "Medium", "Low".
            contains_tags (list, optional): task must have ALL of these tags.
        """
        result = list(self.tasks)

        if status is not None:
            result = [t for t in result if t.completed == status]

        # Date filters only make sense for DueDateTask
        if due_date_before is not None:
            result = [t for t in result if isinstance(t, DueDateTask)
                      and t.due_date <= due_date_before]
        if due_date_after is not None:
            result = [t for t in result if isinstance(t, DueDateTask)
                      and t.due_date >= due_date_after]

        # Priority filter only makes sense for PriorityTask
        if priority_level:
            priority_level = priority_level.strip().capitalize()
            result = [t for t in result if isinstance(t, PriorityTask)
                      and t.priority == priority_level]

        if contains_tags:
            wanted = {normalize_tag(tag) for tag in contains_tags} - {""}
            result = [t for t in result if wanted.issubset(t.tags)]

        return result

    def sort_tasks(self, criterion="id", reverse=False, tasks=None):
        """
        Returns a sorted copy of the tasks (self.tasks is not modified).

        Args:
            criterion (str): "id", "description", "completed", "due_date",
                "priority". Unknown values fall back to "id".
            reverse (bool): True for descending order.
            tasks (list, optional): tasks to sort; defaults to all tasks.

        For "due_date" / "priority", tasks without that attribute are always
        placed LAST (in both orders), sorted by ID.
        """
        tasks = list(self.tasks if tasks is None else tasks)

        if criterion == "due_date":
            with_key = [t for t in tasks if isinstance(t, DueDateTask)]
            key = lambda t: t.due_date
        elif criterion == "priority":
            with_key = [t for t in tasks if isinstance(t, PriorityTask)]
            key = lambda t: self.PRIORITY_MAP[t.priority]
        else:
            if criterion == "description":
                key = lambda t: t.description.lower()
            elif criterion == "completed":
                key = lambda t: t.completed  # Pending (False) first
            else:
                if criterion != "id":
                    logger.warning("Unknown sort criterion %r, using id",
                                   criterion)
                key = lambda t: t.id
            # Secondary key t.id keeps ties in a stable, predictable order
            return sorted(tasks, key=lambda t: (key(t), t.id), reverse=reverse)

        without_key = sorted((t for t in tasks if t not in with_key),
                             key=lambda t: t.id)
        with_key.sort(key=lambda t: t.id)               # tie-breaker
        with_key.sort(key=key, reverse=reverse)         # stable sort
        return with_key + without_key
