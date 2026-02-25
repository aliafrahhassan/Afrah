"""Tests for afrah.py"""

import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

# Patch TASKS_FILE before importing so tests use a temp file
import tempfile
import os

TMP_DIR = tempfile.mkdtemp()
TMP_TASKS = Path(TMP_DIR) / "tasks.json"

# Import module and redirect storage path
import importlib
import afrah as _afrah_module
_afrah_module.TASKS_FILE = TMP_TASKS
import afrah


def _reset():
    TMP_TASKS.unlink(missing_ok=True)


class TestStorage(unittest.TestCase):
    def setUp(self):
        _reset()

    def test_load_empty(self):
        self.assertEqual(afrah.load_tasks(), [])

    def test_save_and_load(self):
        tasks = [{"id": 1, "title": "hello"}]
        afrah.save_tasks(tasks)
        self.assertEqual(afrah.load_tasks(), tasks)

    def test_next_id_empty(self):
        self.assertEqual(afrah.next_id([]), 1)

    def test_next_id_non_empty(self):
        tasks = [{"id": 3}, {"id": 7}]
        self.assertEqual(afrah.next_id(tasks), 8)


class TestAdd(unittest.TestCase):
    def setUp(self):
        _reset()

    def _add(self, title, priority="medium"):
        parser = afrah.build_parser()
        args = parser.parse_args(["add", title, "--priority", priority])
        args.func(args)

    def test_add_creates_task(self):
        self._add("Write tests")
        tasks = afrah.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Write tests")
        self.assertEqual(tasks[0]["status"], "pending")
        self.assertEqual(tasks[0]["priority"], "medium")

    def test_add_increments_id(self):
        self._add("First")
        self._add("Second")
        tasks = afrah.load_tasks()
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)

    def test_add_priority(self):
        self._add("Urgent", priority="high")
        tasks = afrah.load_tasks()
        self.assertEqual(tasks[0]["priority"], "high")


class TestDone(unittest.TestCase):
    def setUp(self):
        _reset()
        afrah.save_tasks([
            {"id": 1, "title": "Task one", "priority": "low", "status": "pending", "created_at": "2026-01-01T00:00:00"},
        ])

    def _done(self, task_id):
        parser = afrah.build_parser()
        args = parser.parse_args(["done", str(task_id)])
        args.func(args)

    def test_marks_done(self):
        self._done(1)
        tasks = afrah.load_tasks()
        self.assertEqual(tasks[0]["status"], "done")
        self.assertIn("completed_at", tasks[0])

    def test_missing_id_exits(self):
        with self.assertRaises(SystemExit):
            self._done(99)


class TestDelete(unittest.TestCase):
    def setUp(self):
        _reset()
        afrah.save_tasks([
            {"id": 1, "title": "Delete me", "priority": "low", "status": "pending", "created_at": "2026-01-01T00:00:00"},
            {"id": 2, "title": "Keep me", "priority": "low", "status": "pending", "created_at": "2026-01-01T00:00:00"},
        ])

    def _delete(self, task_id):
        parser = afrah.build_parser()
        args = parser.parse_args(["delete", str(task_id)])
        args.func(args)

    def test_delete_removes_task(self):
        self._delete(1)
        tasks = afrah.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], 2)

    def test_missing_id_exits(self):
        with self.assertRaises(SystemExit):
            self._delete(99)


class TestList(unittest.TestCase):
    def setUp(self):
        _reset()
        afrah.save_tasks([
            {"id": 1, "title": "Pending high", "priority": "high", "status": "pending", "created_at": "2026-01-01T00:00:00"},
            {"id": 2, "title": "Done low", "priority": "low", "status": "done", "created_at": "2026-01-01T00:00:00"},
            {"id": 3, "title": "Pending low", "priority": "low", "status": "pending", "created_at": "2026-01-01T00:00:00"},
        ])

    def _list(self, *extra_args):
        parser = afrah.build_parser()
        args = parser.parse_args(["list", *extra_args])
        args.func(args)

    def test_list_all(self):
        self._list()  # should not raise

    def test_filter_pending(self):
        parser = afrah.build_parser()
        args = parser.parse_args(["list", "--filter", "pending"])
        # Capture output
        import io
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            args.func(args)
            output = mock_out.getvalue()
        self.assertIn("Pending high", output)
        self.assertNotIn("Done low", output)

    def test_filter_done(self):
        parser = afrah.build_parser()
        args = parser.parse_args(["list", "--filter", "done"])
        import io
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            args.func(args)
            output = mock_out.getvalue()
        self.assertIn("Done low", output)
        self.assertNotIn("Pending high", output)


if __name__ == "__main__":
    unittest.main()
