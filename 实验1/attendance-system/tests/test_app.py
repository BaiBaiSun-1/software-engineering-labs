import tempfile
import unittest
from pathlib import Path

from app import create_app


class AttendanceWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": Path(self.tempdir.name) / "attendance.sqlite3",
                "SECRET_KEY": "test-key",
            }
        )
        self.client = self.app.test_client()
        self.client.post("/events", data={"title": "实验一测试活动"})

    def tearDown(self):
        self.tempdir.cleanup()

    def test_create_checkin_duplicate_search_and_export(self):
        first = self.client.post(
            "/events/1/checkin",
            data={"student_id": "s001", "name": "测试学生"},
            follow_redirects=True,
        )
        self.assertIn("签到成功", first.get_data(as_text=True))
        self.assertIn("S001", first.get_data(as_text=True))

        duplicate = self.client.post(
            "/events/1/checkin",
            data={"student_id": "S001", "name": "另一姓名"},
            follow_redirects=True,
        )
        self.assertIn("已经签到", duplicate.get_data(as_text=True))
        self.assertIn("1</strong>", duplicate.get_data(as_text=True))

        search = self.client.get("/events/1?q=测试")
        self.assertIn("找到 1 条记录", search.get_data(as_text=True))
        self.assertNotIn("另一姓名", search.get_data(as_text=True))

        exported = self.client.get("/events/1/export.csv")
        self.assertEqual(exported.status_code, 200)
        self.assertIn("attachment;", exported.headers["Content-Disposition"])
        self.assertTrue(exported.data.startswith(b"\xef\xbb\xbf"))
        self.assertIn("S001", exported.data.decode("utf-8-sig"))

    def test_invalid_input_and_missing_event(self):
        invalid = self.client.post(
            "/events/1/checkin",
            data={"student_id": "!", "name": "测试"},
            follow_redirects=True,
        )
        self.assertIn("学号须为", invalid.get_data(as_text=True))
        self.assertEqual(self.client.get("/events/999").status_code, 404)
        self.assertEqual(self.client.get("/events/999/export.csv").status_code, 404)


if __name__ == "__main__":
    unittest.main()
