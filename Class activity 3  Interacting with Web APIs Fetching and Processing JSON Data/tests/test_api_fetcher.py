"""
Unit tests (offline) for APIClient and export_to_json_file.
requests.get is mocked, so no internet is needed.
Run: python -m unittest discover tests
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from api_client import APIClient  # noqa: E402
from exporter import export_to_json_file  # noqa: E402

USER_1 = {"id": 1, "name": "Leanne Graham", "username": "Bret", "email": "Sincere@april.biz",
          "phone": "1-770-736-8031 x56442", "address": {"city": "Gwenborough"},
          "company": {"name": "Romaguera-Crona"}}
COMMENTS_1 = [{"postId": 1, "id": i, "name": f"comment {i}", "email": f"u{i}@x.com", "body": "text"} for i in range(1, 6)]


def fake_response(status=200, payload=None):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = payload
    if status >= 400:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError(f"{status} Error")
    return resp


class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api_client.requests.get")
    def test_user_profile_endpoint_and_nested_fields(self, mock_get):
        mock_get.return_value = fake_response(200, USER_1)
        user = self.client.fetch_user_profile(1)
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/1", timeout=10)
        self.assertEqual(user["company"]["name"], "Romaguera-Crona")
        self.assertEqual(user["address"]["city"], "Gwenborough")

    @patch("api_client.requests.get")
    def test_user_profile_not_found_returns_none(self, mock_get):
        mock_get.return_value = fake_response(404, {})
        self.assertIsNone(self.client.fetch_user_profile(999))

    @patch("api_client.requests.get")
    def test_post_comments(self, mock_get):
        mock_get.return_value = fake_response(200, COMMENTS_1)
        comments = self.client.fetch_post_comments(1)
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/posts/1/comments", timeout=10)
        self.assertEqual(len(comments), 5)

    @patch("api_client.requests.get", side_effect=requests.exceptions.ConnectionError("offline"))
    def test_network_error_returns_none(self, _):
        self.assertIsNone(self.client.fetch_single_todo(1))


class TestExport(unittest.TestCase):
    def test_export_utf8_thai_and_indent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.json")
            self.assertTrue(export_to_json_file(path, {"ชื่อ": "ทดสอบ"}))
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("ทดสอบ", text)          # ensure_ascii=False
            self.assertIn('\n    "ชื่อ"', text)    # indent=4
            self.assertEqual(json.loads(text), {"ชื่อ": "ทดสอบ"})

    def test_export_adds_json_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(export_to_json_file(os.path.join(tmp, "data"), [1, 2]))
            self.assertTrue(os.path.exists(os.path.join(tmp, "data.json")))

    def test_export_bad_path_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            blocker = os.path.join(tmp, "file")
            open(blocker, "w").close()  # a file where a folder is expected
            self.assertFalse(export_to_json_file(os.path.join(blocker, "x.json"), {}))

    def test_export_unserializable_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(export_to_json_file(os.path.join(tmp, "x.json"), {"bad": object()}))


if __name__ == "__main__":
    unittest.main()
