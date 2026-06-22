import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages
from app.controllers.auth_controller import AuthController

<<<<<<< HEAD
=======

# A reusable helper that builds a tiny Flask app for every test.
# define the route names the controller redirects to
# (auth.login, auth.register, customer.home, customer.profile,
# admin.dashboard, seller.setup, seller.dashboard) so that
# url_for() inside the controller can build URLs successfully.
>>>>>>> origin/aayushma
def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    auth_bp = Blueprint("auth", __name__)
    auth_bp.route("/login", endpoint="login")(lambda: "login")
    auth_bp.route("/register", endpoint="register")(lambda: "register")
    app.register_blueprint(auth_bp)

    customer_bp = Blueprint("customer", __name__)
    customer_bp.route("/", endpoint="home")(lambda: "home")
    customer_bp.route("/profile", endpoint="profile")(lambda: "profile")
    app.register_blueprint(customer_bp)

    admin_bp = Blueprint("admin", __name__)
    admin_bp.route("/dashboard", endpoint="dashboard")(lambda: "admin dashboard")
    app.register_blueprint(admin_bp)

    seller_bp = Blueprint("seller", __name__)
    seller_bp.route("/setup", endpoint="setup")(lambda: "seller setup")
    seller_bp.route("/dashboard", endpoint="dashboard")(lambda: "seller dashboard")
    app.register_blueprint(seller_bp)

    return app

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
def make_controller():
    """
    Build an AuthController whose DB-touching helpers (_log/_notify)
    are replaced with mocks, since those call the real database via
    app/utils/auth.py and we only want to exercise the controller's
    own logic in these unit tests.
    """
    controller = AuthController()
    controller._log = MagicMock()
    controller._notify = MagicMock()
    return controller

<<<<<<< HEAD
=======

# =====================================================================
#  REGISTER
# =====================================================================
>>>>>>> origin/aayushma
class TestRegister(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.auth_controller.render_template")
    def test_register_get_shows_form(self, mock_render):
        """Visiting register with GET should show the (empty) register form."""
        mock_render.return_value = "register_page"
        with self.app.test_request_context(method="GET"):
            result = self.controller.register()
            self.assertEqual(result, "register_page")
            mock_render.assert_called_once_with("auth/register.html")

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_register_missing_fields_is_rejected(self, mock_render, mock_user_model):
        """Empty name/email/password fields are refused with messages."""
        mock_render.return_value = "register_page"
        mock_user_model.find_by_email_or_phone.return_value = None
        with self.app.test_request_context(
            method="POST",
            data={"name": "", "email": "", "phone": "", "password": "", "confirm_password": ""},
        ):
            self.controller.register()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Name is required."), flashes)
            self.assertIn(("danger", "Invalid email address."), flashes)
            self.assertIn(("danger", "Password must be at least 8 characters."), flashes)

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_register_short_password_is_rejected(self, mock_render, mock_user_model):
        """Passwords shorter than 8 characters are not allowed."""
        mock_render.return_value = "register_page"
        mock_user_model.find_by_email_or_phone.return_value = None
        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Bob", "email": "bob@example.com", "phone": "9800000000",
                "password": "short", "confirm_password": "short",
            },
        ):
            self.controller.register()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(
                ("danger", "Password must be at least 8 characters."), flashes
            )

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_register_mismatched_passwords_is_rejected(self, mock_render, mock_user_model):
        """Password and confirm_password must match."""
        mock_render.return_value = "register_page"
        mock_user_model.find_by_email_or_phone.return_value = None
        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Bob", "email": "bob@example.com", "phone": "9800000000",
                "password": "secret123", "confirm_password": "different1",
            },
        ):
            self.controller.register()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Passwords do not match."), flashes)

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_register_duplicate_email_is_rejected(self, mock_render, mock_user_model):
        """If the email or phone is already registered, registration is refused."""
        mock_render.return_value = "register_page"
        mock_user_model.find_by_email_or_phone.return_value = {"id": 1}

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Bob", "email": "taken@example.com", "phone": "9800000000",
                "password": "secret123", "confirm_password": "secret123",
            },
        ):
            result = self.controller.register()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Email or phone already registered."), flashes)
<<<<<<< HEAD

            self.assertEqual(result, "register_page")

=======
            # The form is re-rendered rather than redirected.
            self.assertEqual(result, "register_page")
            # And the user should NOT be created.
>>>>>>> origin/aayushma
            mock_user_model.register.assert_not_called()

    @patch("app.controllers.auth_controller.UserModel")
    def test_register_success_saves_user_and_redirects(self, mock_user_model):
        """A valid new customer registration is saved and sent to the login page."""
        mock_user_model.find_by_email_or_phone.return_value = None
        mock_user_model.register.return_value = 42

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Alice", "email": "alice@example.com", "phone": "9811111111",
                "password": "secret123", "confirm_password": "secret123",
                "role": "customer",
            },
        ):
            response = self.controller.register()
            mock_user_model.register.assert_called_once_with(
                "Alice", "alice@example.com", "9811111111", "secret123", "customer"
            )
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Account created! Please log in."), flashes)

    @patch("app.controllers.auth_controller.UserModel")
    def test_register_seller_marks_pending_store_setup(self, mock_user_model):
        """Registering as a seller remembers the new user id so they can be
        nudged into the store-setup wizard right after their first login."""
        mock_user_model.find_by_email_or_phone.return_value = None
        mock_user_model.register.return_value = 7

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Sam", "email": "sam@example.com", "phone": "9822222222",
                "password": "secret123", "confirm_password": "secret123",
                "role": "seller",
            },
        ):
            self.controller.register()
            self.assertEqual(session["pending_store_setup"], 7)

<<<<<<< HEAD
=======

# =====================================================================
#  LOGIN
# =====================================================================
>>>>>>> origin/aayushma
class TestLogin(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.auth_controller.render_template")
    def test_login_get_shows_form(self, mock_render):
        """Visiting login with GET should show the login form."""
        mock_render.return_value = "login_page"
        with self.app.test_request_context(method="GET"):
            result = self.controller.login()
            self.assertEqual(result, "login_page")
            mock_render.assert_called_once_with("auth/login.html")

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_login_unknown_email_is_rejected(self, mock_render, mock_user_model):
        """An email that isn't registered is refused with a generic message."""
        mock_render.return_value = "login_page"
        mock_user_model.find_by_email.return_value = None
        mock_user_model.authenticate.return_value = None

        with self.app.test_request_context(
            method="POST", data={"email": "nobody@example.com", "password": "whatever1"}
        ):
            self.controller.login()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Invalid email or password."), flashes)
            mock_user_model.record_failed_login.assert_not_called()

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_login_wrong_password_is_rejected(self, mock_render, mock_user_model):
        """A correct email but wrong password is refused, and the failed
        attempt is recorded against the existing user."""
        mock_render.return_value = "login_page"
        mock_user_model.find_by_email.return_value = {
            "id": 1, "name": "Bob", "email": "bob@example.com",
            "role": "customer", "is_active": 1,
        }
        mock_user_model.authenticate.return_value = None

        with self.app.test_request_context(
            method="POST",
            data={"email": "bob@example.com", "password": "wrongpass"},
        ):
            self.controller.login()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Invalid email or password."), flashes)
            mock_user_model.record_failed_login.assert_called_once_with(1)
<<<<<<< HEAD

=======
            # No session was created.
>>>>>>> origin/aayushma
            self.assertNotIn("user_id", session)

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_login_deactivated_account_is_rejected(self, mock_render, mock_user_model):
        """A correct password for a deactivated account is still refused."""
        mock_render.return_value = "login_page"
        mock_user_model.find_by_email.return_value = {
            "id": 1, "name": "Bob", "email": "bob@example.com",
            "role": "customer", "is_active": 0,
        }
        mock_user_model.authenticate.return_value = {"id": 1}

        with self.app.test_request_context(
            method="POST",
            data={"email": "bob@example.com", "password": "secret123"},
        ):
            self.controller.login()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Your account has been deactivated."), flashes)
            self.assertNotIn("user_id", session)

    @patch("app.controllers.auth_controller.UserModel")
    def test_login_success_sets_session_and_redirects_customer(self, mock_user_model):
        """A correct customer login stores the user in the session and
        redirects to the customer homepage."""
        mock_user_model.find_by_email.return_value = {
            "id": 2, "name": "Bob", "email": "bob@example.com",
            "role": "customer", "is_active": 1,
        }
        mock_user_model.authenticate.return_value = {"id": 2}

        with self.app.test_request_context(
            method="POST",
            data={"email": "bob@example.com", "password": "secret123"},
        ):
            response = self.controller.login()
            self.assertEqual(session["user_id"], 2)
            self.assertEqual(session["name"], "Bob")
            self.assertEqual(session["role"], "customer")
            self.assertEqual(response.status_code, 302)
            mock_user_model.update_last_login.assert_called_once_with(2)
            self.controller._log.assert_called_once_with("login")

    @patch("app.controllers.auth_controller.UserModel")
    def test_login_success_redirects_admin_to_dashboard(self, mock_user_model):
        """An admin is redirected straight to the admin dashboard."""
        mock_user_model.find_by_email.return_value = {
            "id": 3, "name": "Admin", "email": "admin@example.com",
            "role": "admin", "is_active": 1,
        }
        mock_user_model.authenticate.return_value = {"id": 3}

        with self.app.test_request_context(
            method="POST",
            data={"email": "admin@example.com", "password": "secret123"},
        ):
            response = self.controller.login()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/dashboard"))

    @patch("app.controllers.auth_controller.StoreModel")
    @patch("app.controllers.auth_controller.UserModel")
    def test_login_success_seller_without_store_goes_to_setup(self, mock_user_model, mock_store_model):
        """A seller without a store yet is sent to the setup wizard."""
        mock_user_model.find_by_email.return_value = {
            "id": 4, "name": "Sam", "email": "sam@example.com",
            "role": "seller", "is_active": 1,
        }
        mock_user_model.authenticate.return_value = {"id": 4}
        mock_store_model.find_by_user.return_value = None

        with self.app.test_request_context(
            method="POST",
            data={"email": "sam@example.com", "password": "secret123"},
        ):
            response = self.controller.login()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/setup"))

    @patch("app.controllers.auth_controller.StoreModel")
    @patch("app.controllers.auth_controller.UserModel")
    def test_login_success_seller_with_store_goes_to_dashboard(self, mock_user_model, mock_store_model):
        """A seller who already has a store is sent to their dashboard."""
        mock_user_model.find_by_email.return_value = {
            "id": 5, "name": "Sam", "email": "sam@example.com",
            "role": "seller", "is_active": 1,
        }
        mock_user_model.authenticate.return_value = {"id": 5}
        mock_store_model.find_by_user.return_value = {"id": 99}

        with self.app.test_request_context(
            method="POST",
            data={"email": "sam@example.com", "password": "secret123"},
        ):
            response = self.controller.login()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/dashboard"))

<<<<<<< HEAD
=======

# =====================================================================
#  LOGOUT
# =====================================================================
>>>>>>> origin/aayushma
class TestLogout(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_logout_clears_session_and_redirects(self):
        """Logging out wipes the session and returns to the login page."""
        with self.app.test_request_context():
<<<<<<< HEAD

=======
            # Pretend someone is logged in.
>>>>>>> origin/aayushma
            session["user_id"] = 99
            session["name"] = "Alice"
            session["role"] = "customer"

            response = self.controller.logout()

<<<<<<< HEAD
            self.assertNotIn("user_id", session)
            self.assertNotIn("name", session)
            self.assertNotIn("role", session)

=======
            # Every session value is gone.
            self.assertNotIn("user_id", session)
            self.assertNotIn("name", session)
            self.assertNotIn("role", session)
            # Redirected (302) back to login with a goodbye message.
>>>>>>> origin/aayushma
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("info", "Logged out successfully."), flashes)
            self.controller._log.assert_called_once_with("logout")

<<<<<<< HEAD
=======

# =====================================================================
#  FORGOT PASSWORD
# =====================================================================
>>>>>>> origin/aayushma
class TestForgotPassword(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.auth_controller.render_template")
    def test_forgot_password_get_shows_form(self, mock_render):
        mock_render.return_value = "forgot_password_page"
        with self.app.test_request_context(method="GET"):
            result = self.controller.forgot_password()
            self.assertEqual(result, "forgot_password_page")
            mock_render.assert_called_once_with("auth/forgot_password.html")

    def test_forgot_password_post_always_shows_generic_message(self):
        """The same message is shown whether or not the email exists, so
        this endpoint can't be used to discover which emails are registered."""
        with self.app.test_request_context(
            method="POST", data={"email": "anyone@example.com"}
        ):
            response = self.controller.forgot_password()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(
                ("info", "If that email exists, a reset link has been sent."), flashes
            )

<<<<<<< HEAD
=======

# =====================================================================
#  CHANGE PASSWORD
# =====================================================================
>>>>>>> origin/aayushma
class TestChangePassword(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_guest_is_redirected_to_login(self):
        """A visitor without an active session can't reach this page."""
        with self.app.test_request_context(method="GET"):
            response = self.controller.change_password()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)

    @patch("app.controllers.auth_controller.render_template")
    def test_logged_in_get_shows_form(self, mock_render):
        mock_render.return_value = "change_password_page"
        with self.app.test_request_context(method="GET"):
            session["user_id"] = 1
            result = self.controller.change_password()
            self.assertEqual(result, "change_password_page")
            mock_render.assert_called_once_with("auth/change_password.html")

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_wrong_current_password_is_rejected(self, mock_render, mock_user_model):
        mock_render.return_value = "change_password_page"
        mock_user_model.find_by_id.return_value = {"id": 1, "email": "bob@example.com"}
        mock_user_model.authenticate.return_value = None

        with self.app.test_request_context(
            method="POST",
            data={"old_password": "wrongold", "new_password": "newsecret1"},
        ):
            session["user_id"] = 1
            self.controller.change_password()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Current password is incorrect."), flashes)
            mock_user_model.change_password.assert_not_called()

    @patch("app.controllers.auth_controller.UserModel")
    @patch("app.controllers.auth_controller.render_template")
    def test_short_new_password_is_rejected(self, mock_render, mock_user_model):
        mock_render.return_value = "change_password_page"
        mock_user_model.find_by_id.return_value = {"id": 1, "email": "bob@example.com"}
        mock_user_model.authenticate.return_value = {"id": 1}

        with self.app.test_request_context(
            method="POST",
            data={"old_password": "oldsecret1", "new_password": "short"},
        ):
            session["user_id"] = 1
            self.controller.change_password()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(
                ("danger", "New password must be at least 8 characters."), flashes
            )
            mock_user_model.change_password.assert_not_called()

    @patch("app.controllers.auth_controller.UserModel")
    def test_successful_change_redirects_to_profile(self, mock_user_model):
        mock_user_model.find_by_id.return_value = {"id": 1, "email": "bob@example.com"}
        mock_user_model.authenticate.return_value = {"id": 1}

        with self.app.test_request_context(
            method="POST",
            data={"old_password": "oldsecret1", "new_password": "newsecret1"},
        ):
            session["user_id"] = 1
            response = self.controller.change_password()
            mock_user_model.change_password.assert_called_once_with(1, "newsecret1")
            self.assertEqual(response.status_code, 302)
            self.assertIn("/profile", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Password updated successfully."), flashes)
            self.controller._log.assert_called_once_with("change_password")

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
if __name__ == "__main__":
    unittest.main()
