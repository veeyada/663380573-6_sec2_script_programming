# final-task-manager-project/src/task.py
"""Domain models: Task, DueDateTask and PriorityTask (all support tags)."""
import datetime

DATE_FORMAT = '%Y-%m-%d'
ALLOWED_PRIORITIES = ("High", "Medium", "Low")


def normalize_tag(tag):
    """Return a cleaned, lower-case tag ('' if the tag is blank)."""
    return str(tag).strip().lower()


class Task:
    """
    Base class for all tasks in the task manager.
    Includes a 'tags' attribute (list of strings) for categorization.
    """

    def __init__(self, id, description, completed=False, tags=None):
        self.id = id
        self.description = description
        self.completed = completed
        # Always keep tags as a list of unique, normalized strings
        self.tags = []
        for tag in (tags or []):
            self.add_tag(tag)

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True

    def add_tag(self, tag):
        """Adds a tag to the task, preventing blanks and duplicates."""
        tag = normalize_tag(tag)
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        """Removes a tag from the task. Returns True if it was removed."""
        tag = normalize_tag(tag)
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def _extra_info(self):
        """Hook for subclasses: extra ' | Key: value' text shown before tags."""
        return ""

    def to_dict(self):
        """
        Converts the Task object to a dictionary for JSON serialization.
        Includes a '_type' field and tags.
        """
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "tags": list(self.tags),
            "_type": "Task",
        }

    def __str__(self):
        """Returns a human-readable string representation of the task."""
        status = "Completed" if self.completed else "Pending"
        tags_str = f" | Tags: {', '.join(self.tags)}" if self.tags else ""
        return (f"ID: {self.id} | Description: {self.description} | "
                f"Status: {status}{self._extra_info()}{tags_str}")

    def __repr__(self):
        return (f"Task(id={self.id}, description='{self.description}', "
                f"completed={self.completed}, tags={self.tags})")


class DueDateTask(Task):
    """
    A task with an additional due date, stored as a datetime.date object.
    Inherits from the base Task class.
    """

    def __init__(self, id, description, due_date, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        # due_date can be a string (from JSON / CLI) or a datetime.date object
        if isinstance(due_date, str):
            # Raises ValueError on a bad format
            self.due_date = datetime.datetime.strptime(
                due_date.strip(), DATE_FORMAT).date()
        elif isinstance(due_date, datetime.date):
            self.due_date = due_date
        else:
            raise TypeError("due_date must be a string in YYYY-MM-DD format "
                            "or a datetime.date object")

    def is_overdue(self, today=None):
        """True if the task is pending and its due date has passed."""
        today = today or datetime.date.today()
        return not self.completed and self.due_date < today

    def _extra_info(self):
        overdue = " (OVERDUE)" if self.is_overdue() else ""
        return f" | Due: {self.due_date.strftime(DATE_FORMAT)}{overdue}"

    def to_dict(self):
        """Adds due_date (as a string) and its own type identifier."""
        base_dict = super().to_dict()
        base_dict["due_date"] = self.due_date.strftime(DATE_FORMAT)
        base_dict["_type"] = "DueDateTask"
        return base_dict

    def __repr__(self):
        return (f"DueDateTask(id={self.id}, description='{self.description}', "
                f"due_date='{self.due_date.strftime(DATE_FORMAT)}', "
                f"completed={self.completed}, tags={self.tags})")


class PriorityTask(Task):
    """
    A task with an additional priority level (High, Medium or Low).
    Inherits from the base Task class.
    """

    def __init__(self, id, description, priority, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        priority = str(priority).strip().capitalize()
        if priority not in ALLOWED_PRIORITIES:
            raise ValueError(
                f"Priority must be one of {list(ALLOWED_PRIORITIES)}")
        self.priority = priority

    def _extra_info(self):
        return f" | Priority: {self.priority}"

    def to_dict(self):
        """Adds priority and its own type identifier."""
        base_dict = super().to_dict()
        base_dict["priority"] = self.priority
        base_dict["_type"] = "PriorityTask"
        return base_dict

    def __repr__(self):
        return (f"PriorityTask(id={self.id}, description='{self.description}', "
                f"priority='{self.priority}', completed={self.completed}, "
                f"tags={self.tags})")
