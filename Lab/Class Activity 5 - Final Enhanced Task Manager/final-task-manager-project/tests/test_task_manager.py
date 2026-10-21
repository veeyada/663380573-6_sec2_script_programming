"""Unit tests. Run from the project folder: python -m unittest discover tests"""
import datetime
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.task import Task, DueDateTask, PriorityTask
from src.task_manager import TaskManager
from src.data_persistence import DataPersistence

D = datetime.date


class TempFileMixin:
    """Gives each test its own temporary tasks.json."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp_dir, "tasks.json")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


class TestTaskModels(unittest.TestCase):

    def test_tags_are_normalized_and_unique(self):
        task = Task(1, "A", tags=[" Study ", "study", "", "URGENT"])
        self.assertEqual(task.tags, ["study", "urgent"])
        task.add_tag("  Work ")
        task.add_tag("work")
        self.assertEqual(task.tags, ["study", "urgent", "work"])

    def test_remove_tag(self):
        task = Task(1, "A", tags=["study"])
        self.assertTrue(task.remove_tag(" STUDY "))
        self.assertFalse(task.remove_tag("missing"))
        self.assertEqual(task.tags, [])

    def test_tags_list_is_copied(self):
        tags = ["a"]
        task = Task(1, "A", tags=tags)
        task.add_tag("b")
        self.assertEqual(tags, ["a"])

    def test_due_date_parsing(self):
        self.assertEqual(DueDateTask(1, "A", "2026-12-31").due_date, D(2026, 12, 31))
        self.assertEqual(DueDateTask(1, "A", D(2026, 1, 1)).due_date, D(2026, 1, 1))
        with self.assertRaises(ValueError):
            DueDateTask(1, "A", "31/12/2026")
        with self.assertRaises(TypeError):
            DueDateTask(1, "A", 20261231)

    def test_priority_validation(self):
        self.assertEqual(PriorityTask(1, "A", "high").priority, "High")
        with self.assertRaises(ValueError):
            PriorityTask(1, "A", "Urgent")

    def test_str_shows_extra_info_before_tags(self):
        s = str(DueDateTask(2, "Submit", "2099-01-01", tags=["github"]))
        self.assertEqual(s, "ID: 2 | Description: Submit | Status: Pending"
                            " | Due: 2099-01-01 | Tags: github")
        s = str(PriorityTask(3, "Slides", "High"))
        self.assertTrue(s.endswith("| Priority: High"))

    def test_overdue(self):
        task = DueDateTask(1, "A", "2026-01-01")
        self.assertTrue(task.is_overdue(today=D(2026, 1, 2)))
        self.assertFalse(task.is_overdue(today=D(2026, 1, 1)))
        task.mark_complete()
        self.assertFalse(task.is_overdue(today=D(2026, 1, 2)))


class TestPersistence(TempFileMixin, unittest.TestCase):

    def test_round_trip_keeps_types_and_tags(self):
        tasks = [Task(1, "A", tags=["x"]),
                 DueDateTask(2, "B", "2026-05-01", completed=True),
                 PriorityTask(3, "C", "Low", tags=["y", "z"])]
        dp = DataPersistence(self.path)
        dp.save_tasks(tasks)
        loaded = dp.load_tasks()
        self.assertEqual([type(t) for t in loaded], [Task, DueDateTask, PriorityTask])
        self.assertEqual([t.to_dict() for t in loaded], [t.to_dict() for t in tasks])

    def test_missing_file_returns_empty(self):
        self.assertEqual(DataPersistence(self.path).load_tasks(), [])

    def test_corrupted_file_returns_empty(self):
        with open(self.path, "w") as f:
            f.write("{not json")
        self.assertEqual(DataPersistence(self.path).load_tasks(), [])

    def test_old_records_without_tags_and_bad_records(self):
        data = [{"id": 1, "description": "old", "completed": False, "_type": "Task"},
                {"id": 2, "description": "bad", "completed": False,
                 "_type": "PriorityTask", "priority": "Huge"},
                {"id": 3, "description": "?", "completed": False, "_type": "Alien"}]
        with open(self.path, "w") as f:
            json.dump(data, f)
        loaded = DataPersistence(self.path).load_tasks()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].tags, [])


class TestTaskManager(TempFileMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.m = TaskManager(self.path)
        self.m.add_normal_task("Write README", tags=["study", "urgent"])       # 1
        self.m.add_due_date_task("Submit code", "2026-09-30", tags=["study"])  # 2
        self.m.add_priority_task("Make slides", "High", tags=["presentation"]) # 3
        self.m.add_priority_task("Fix style", "Low")                           # 4
        self.m.add_due_date_task("Midterm review", "2026-08-20", tags=["exam"])# 5
        self.m.add_priority_task("Rehearse demo", "Medium", tags=["presentation"])  # 6
        self.m.complete_task(4)
        self.m.complete_task(5)

    def ids(self, tasks):
        return [t.id for t in tasks]

    # CRUD
    def test_ids_and_persistence(self):
        self.assertEqual(self.ids(self.m.get_all_tasks()), [1, 2, 3, 4, 5, 6])
        reloaded = TaskManager(self.path)
        self.assertEqual(len(reloaded.tasks), 6)
        self.assertEqual(reloaded.next_id, 7)

    def test_invalid_inputs_return_none(self):
        self.assertIsNone(self.m.add_due_date_task("x", "2026-13-01"))
        self.assertIsNone(self.m.add_priority_task("x", "Urgent"))
        self.assertEqual(self.m.next_id, 7)

    def test_complete_and_delete(self):
        self.assertTrue(self.m.complete_task(1)[0])
        self.assertFalse(self.m.complete_task(1)[0])   # already completed
        self.assertFalse(self.m.complete_task(99)[0])
        self.assertTrue(self.m.delete_task(1)[0])
        self.assertFalse(self.m.delete_task(1)[0])
        self.assertNotIn(1, self.ids(TaskManager(self.path).tasks))

    def test_id_not_reused_after_delete_of_last(self):
        self.m.delete_task(3)
        self.assertEqual(self.m.add_normal_task("new").id, 7)

    def test_tag_management(self):
        self.assertTrue(self.m.add_tag_to_task(3, "Urgent")[0])
        self.assertIn("urgent", TaskManager(self.path).get_task_by_id(3).tags)
        self.assertFalse(self.m.add_tag_to_task(3, "  ")[0])
        self.assertTrue(self.m.remove_tag_from_task(3, "urgent")[0])
        self.assertFalse(self.m.remove_tag_from_task(3, "urgent")[0])

    # Search
    def test_search_partial_case_insensitive(self):
        self.assertEqual(self.ids(self.m.search_tasks("SLIDE")), [3])
        self.assertEqual(self.ids(self.m.search_tasks("pres")), [3, 6])  # tag
        self.assertEqual(self.ids(self.m.search_tasks("study")), [1, 2])
        self.assertEqual(self.m.search_tasks(""), [])
        self.assertEqual(self.m.search_tasks("zzz"), [])

    # Filter
    def test_filter_status(self):
        self.assertEqual(self.ids(self.m.filter_tasks(status=True)), [4, 5])
        self.assertEqual(self.ids(self.m.filter_tasks(status=False)), [1, 2, 3, 6])

    def test_filter_dates(self):
        self.assertEqual(self.ids(self.m.filter_tasks(due_date_before=D(2026, 9, 1))), [5])
        self.assertEqual(self.ids(self.m.filter_tasks(due_date_after=D(2026, 9, 30))), [2])
        self.assertEqual(self.ids(self.m.filter_tasks(
            due_date_after=D(2026, 8, 1), due_date_before=D(2026, 12, 31))), [2, 5])

    def test_filter_priority_and_tags(self):
        self.assertEqual(self.ids(self.m.filter_tasks(priority_level="high")), [3])
        self.assertEqual(self.ids(self.m.filter_tasks(contains_tags=["STUDY"])), [1, 2])
        self.assertEqual(self.ids(self.m.filter_tasks(contains_tags=["study", "urgent"])), [1])

    def test_filter_combined(self):
        result = self.m.filter_tasks(status=False, contains_tags=["presentation"],
                                     priority_level="Medium")
        self.assertEqual(self.ids(result), [6])
        self.assertEqual(self.ids(self.m.filter_tasks()), [1, 2, 3, 4, 5, 6])

    # Sort
    def test_sort_basic(self):
        self.assertEqual(self.ids(self.m.sort_tasks("id", reverse=True)), [6, 5, 4, 3, 2, 1])
        self.assertEqual(self.ids(self.m.sort_tasks("description")), [4, 3, 5, 6, 2, 1])
        self.assertEqual(self.ids(self.m.sort_tasks("completed")), [1, 2, 3, 6, 4, 5])
        self.assertEqual(self.ids(self.m.sort_tasks("nonsense")), [1, 2, 3, 4, 5, 6])

    def test_sort_due_date_others_always_last(self):
        self.assertEqual(self.ids(self.m.sort_tasks("due_date")), [5, 2, 1, 3, 4, 6])
        self.assertEqual(self.ids(self.m.sort_tasks("due_date", True)), [2, 5, 1, 3, 4, 6])

    def test_sort_priority_others_always_last(self):
        self.assertEqual(self.ids(self.m.sort_tasks("priority")), [3, 6, 4, 1, 2, 5])
        self.assertEqual(self.ids(self.m.sort_tasks("priority", True)), [4, 6, 3, 1, 2, 5])

    def test_sort_does_not_modify_original(self):
        self.m.sort_tasks("id", reverse=True)
        self.assertEqual(self.ids(self.m.tasks), [1, 2, 3, 4, 5, 6])

    def test_empty_manager(self):
        empty = TaskManager(os.path.join(self.tmp_dir, "empty.json"))
        self.assertEqual(empty.search_tasks("a"), [])
        self.assertEqual(empty.filter_tasks(status=True), [])
        self.assertEqual(empty.sort_tasks("priority"), [])


if __name__ == "__main__":
    unittest.main()
