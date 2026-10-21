"""Unit tests for Task and TaskManager. Run: python -m unittest discover tests"""
import json
import os
import tempfile
import unittest

from src.task import Task
from src.task_manager import TaskManager


class TestTask(unittest.TestCase):
    def test_init_defaults(self):
        t = Task(1, "Read book")
        self.assertEqual((t.id, t.description, t.completed, t.priority), (1, "Read book", False, "Medium"))

    def test_mark_complete(self):
        t = Task(1, "Read book")
        t.mark_complete()
        self.assertTrue(t.completed)

    def test_to_dict_from_dict_round_trip(self):
        t = Task(3, "Write report", True, "High")
        self.assertEqual(Task.from_dict(t.to_dict()).to_dict(), t.to_dict())

    def test_str_and_repr(self):
        t = Task(2, "Call mom")
        self.assertIn("Pending", str(t))
        self.assertEqual(repr(t), "Task(id=2, description='Call mom', completed=False, priority='Medium')")


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "tasks.json")
        self.manager = TaskManager(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_assigns_unique_ids_and_saves(self):
        a = self.manager.add_task("A")
        b = self.manager.add_task("B")
        self.assertEqual((a.id, b.id), (1, 2))
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(len(json.load(f)), 2)

    def test_empty_description_rejected(self):
        self.assertIsNone(self.manager.add_task("   "))
        self.assertEqual(self.manager.tasks, [])

    def test_complete_and_delete(self):
        self.manager.add_task("A")
        self.assertTrue(self.manager.complete_task(1))
        self.assertTrue(self.manager.tasks[0].completed)
        self.assertFalse(self.manager.complete_task(99))
        self.assertTrue(self.manager.delete_task(1))
        self.assertFalse(self.manager.delete_task(1))

    def test_reload_restores_task_objects(self):
        self.manager.add_task("Persist me", "High")
        self.manager.complete_task(1)
        reloaded = TaskManager(self.path)
        self.assertIsInstance(reloaded.tasks[0], Task)
        self.assertEqual(reloaded.tasks[0].to_dict(),
                         {"id": 1, "description": "Persist me", "completed": True, "priority": "High"})
        self.assertEqual(reloaded.next_id, 2)

    def test_next_id_keeps_increasing_after_delete(self):
        self.manager.add_task("A")
        self.manager.add_task("B")
        self.manager.delete_task(2)
        self.assertEqual(self.manager.add_task("C").id, 3)

    def test_corrupted_file_starts_empty(self):
        with open(self.path, "w") as f:
            f.write("{not json")
        self.assertEqual(TaskManager(self.path).tasks, [])

    def test_search(self):
        self.manager.add_task("Buy groceries")
        self.manager.add_task("Read book")
        self.assertEqual([t.id for t in self.manager.search_tasks("GROC")], [1])


if __name__ == "__main__":
    unittest.main()
