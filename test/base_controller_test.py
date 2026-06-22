import io
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session, get_flashed_messages

from app.controllers.base_controller import BaseController

<<<<<<< HEAD
=======

# A reusable helper that builds a tiny Flask app for every test.
# BaseController doesn't redirect to any named routes itself, but its
# session helpers and flash shortcuts need an active Flask request
# context to work.
>>>>>>> origin/aayushma
def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()
    return app

<<<<<<< HEAD
=======

# =====================================================================
#  SESSION HELPERS
# =====================================================================
>>>>>>> origin/aayushma
class TestSessionHelpers(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = BaseController()

    def test_current_user_id_returns_none_when_logged_out(self):
        with self.app.test_request_context():
            self.assertIsNone(self.controller._current_user_id())

    def test_current_user_id_returns_id_when_logged_in(self):
        with self.app.test_request_context():
            session["user_id"] = 7
            self.assertEqual(self.controller._current_user_id(), 7)

    def test_current_role_returns_none_when_logged_out(self):
        with self.app.test_request_context():
            self.assertIsNone(self.controller._current_role())

    def test_current_role_returns_role_when_logged_in(self):
        with self.app.test_request_context():
            session["role"] = "seller"
            self.assertEqual(self.controller._current_role(), "seller")

    def test_is_logged_in_false_when_no_session(self):
        with self.app.test_request_context():
            self.assertFalse(self.controller._is_logged_in())

    def test_is_logged_in_true_when_user_id_present(self):
        with self.app.test_request_context():
            session["user_id"] = 1
            self.assertTrue(self.controller._is_logged_in())

<<<<<<< HEAD
=======

# =====================================================================
#  FLASH MESSAGE SHORTCUTS
# =====================================================================
>>>>>>> origin/aayushma
class TestFlashShortcuts(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = BaseController()

    def test_ok_flashes_success_category(self):
        with self.app.test_request_context():
            self.controller._ok("Saved!")
            self.assertIn(("success", "Saved!"), get_flashed_messages(with_categories=True))

    def test_err_flashes_danger_category(self):
        with self.app.test_request_context():
            self.controller._err("Broken!")
            self.assertIn(("danger", "Broken!"), get_flashed_messages(with_categories=True))

    def test_warn_flashes_warning_category(self):
        with self.app.test_request_context():
            self.controller._warn("Careful!")
            self.assertIn(("warning", "Careful!"), get_flashed_messages(with_categories=True))

    def test_info_flashes_info_category(self):
        with self.app.test_request_context():
            self.controller._info("FYI")
            self.assertIn(("info", "FYI"), get_flashed_messages(with_categories=True))

<<<<<<< HEAD
=======

# =====================================================================
#  DATABASE SHORTHANDS
# =====================================================================
>>>>>>> origin/aayushma
class TestDatabaseShortcuts(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = BaseController()

    @patch("app.controllers.base_controller.db")
    def test_q_delegates_to_db_query(self, mock_db):
        mock_db.query.return_value = [{"id": 1}]
        with self.app.test_request_context():
            result = self.controller._q("SELECT * FROM users", (1,), one=False)
            mock_db.query.assert_called_once_with("SELECT * FROM users", (1,), False)
            self.assertEqual(result, [{"id": 1}])

    @patch("app.controllers.base_controller.db")
    def test_run_delegates_to_db_execute(self, mock_db):
        mock_db.execute.return_value = 99
        with self.app.test_request_context():
            result = self.controller._run("INSERT INTO users (name) VALUES (%s)", ("Bob",))
            mock_db.execute.assert_called_once_with(
                "INSERT INTO users (name) VALUES (%s)", ("Bob",)
            )
            self.assertEqual(result, 99)

<<<<<<< HEAD
=======

# =====================================================================
#  FILE UPLOAD HELPERS
# =====================================================================
>>>>>>> origin/aayushma
class TestFileUploadHelpers(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = BaseController()

    def tearDown(self):
        shutil.rmtree(self.app.config["UPLOAD_FOLDER"], ignore_errors=True)

    def test_allowed_file_accepts_known_extensions(self):
        self.assertTrue(self.controller._allowed_file("photo.png"))
        self.assertTrue(self.controller._allowed_file("photo.JPG"))

    def test_allowed_file_rejects_unknown_extensions(self):
        self.assertFalse(self.controller._allowed_file("virus.exe"))
        self.assertFalse(self.controller._allowed_file("noextension"))

    def test_save_file_returns_none_when_no_file_selected(self):
        with self.app.test_request_context():
            self.assertIsNone(self.controller._save_file(None))

    def test_save_file_returns_none_for_disallowed_extension(self):
        fake_file = MagicMock()
        fake_file.filename = "malware.exe"
        with self.app.test_request_context():
            self.assertIsNone(self.controller._save_file(fake_file))

    def test_save_file_saves_and_returns_relative_path(self):
        fake_file = MagicMock()
        fake_file.filename = "logo.png"
        with self.app.test_request_context():
            path = self.controller._save_file(fake_file, "logos")
            self.assertTrue(path.startswith("uploads/logos/"))
            self.assertTrue(path.endswith(".png"))
            fake_file.save.assert_called_once()

<<<<<<< HEAD
=======

# =====================================================================
#  AUDIT HELPERS
# =====================================================================
>>>>>>> origin/aayushma
class TestAuditHelpers(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = BaseController()

    @patch("app.controllers.base_controller.log_action")
    def test_log_passes_current_user_and_action(self, mock_log_action):
        with self.app.test_request_context():
            session["user_id"] = 5
            self.controller._log("did_a_thing", "product", 10)
            mock_log_action.assert_called_once_with(5, "did_a_thing", "product", 10)

    @patch("app.controllers.base_controller._notify")
    def test_notify_passes_through_to_notify_util(self, mock_notify_util):
        with self.app.test_request_context():
            self.controller._notify(3, "Title", "Message", "order", "/orders/1")
            mock_notify_util.assert_called_once_with(
                3, "Title", "Message", "order", "/orders/1"
            )

<<<<<<< HEAD
=======

# =====================================================================
#  ABSTRACT HOOK / MISC
# =====================================================================
>>>>>>> origin/aayushma
class TestMisc(unittest.TestCase):
    def setUp(self):
        self.controller = BaseController()

    def test_handle_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.controller.handle()

    def test_repr_shows_class_name(self):
        self.assertEqual(repr(self.controller), "<BaseController>")

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
if __name__ == "__main__":
    unittest.main()
