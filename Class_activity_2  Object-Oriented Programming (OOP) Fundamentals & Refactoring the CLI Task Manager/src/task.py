# my-oop-task-manager/src/task.py
"""Defines the Task class: one task with its data (attributes) and behaviour (methods)."""

VALID_PRIORITIES = ("Low", "Medium", "High")


class Task:
    """
    Represents a single task in the task manager.
    """

    def __init__(self, id, description, completed=False, priority="Medium"):
        """
        Initializes a new Task object.

        Args:
            id (int): A unique identifier for the task.
            description (str): A brief description of the task.
            completed (bool, optional): The completion status of the task. Defaults to False.
            priority (str, optional): 'Low', 'Medium' or 'High'. Defaults to 'Medium'.
        """
        self.id = id
        self.description = description
        self.completed = completed
        self.priority = priority if priority in VALID_PRIORITIES else "Medium"

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True

    def to_dict(self):
        """
        Converts the Task object to a dictionary for JSON serialization.
        """
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Task object from a dictionary loaded from JSON
        (the reverse of to_dict). Missing optional keys get default values.
        """
        return cls(
            id=int(data["id"]),
            description=str(data["description"]),
            completed=bool(data.get("completed", False)),
            priority=data.get("priority", "Medium"),
        )

    def __str__(self):
        """
        Returns a human-readable string representation of the task.
        """
        status = "Completed" if self.completed else "Pending"
        return f"ID: {self.id} | Description: {self.description} | Status: {status}"

    def __repr__(self):
        """
        Returns an official string representation of the task object for debugging.
        """
        return (f"Task(id={self.id}, description='{self.description}', "
                f"completed={self.completed}, priority='{self.priority}')")
