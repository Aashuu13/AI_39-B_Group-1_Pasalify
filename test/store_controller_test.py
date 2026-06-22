import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages

from app.controllers.store_controller import StoreController


# A reusable helper that builds a tiny Flask app for every test.
# define the route names the controller redirects to
# (customer.home, customer.product_detail, auth.login, store.chat_view)
# so that url_for() inside the controller can build URLs successfully.
def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    customer_bp = Blueprint("customer", __name__)
    customer_bp.route("/", endpoint="home")(lambda: "home")
    customer_bp.route("/product/<int:pid>", endpoint="product_detail")(lambda pid: f"product {pid}")
    app.register_blueprint(customer_bp)

    auth_bp = Blueprint("auth", __name__)
    auth_bp.route("/login", endpoint="login")(lambda: "login")
    app.register_blueprint(auth_bp)

    store_bp = Blueprint("store", __name__)
    store_bp.route("/chat/<int:cid>", endpoint="chat_view")(lambda cid: f"chat {cid}")
    app.register_blueprint(store_bp)

    return app


def make_controller():
    """
    Build a StoreController whose DB-touching helpers (_q/_run/_log/
    _notify) are replaced with mocks, so tests exercise the
    controller's own logic instead of hitting a real database.
    """
    controller = StoreController()
    controller._q = MagicMock(return_value=None)
    controller._run = MagicMock(return_value=1)
    controller._log = MagicMock()
    controller._notify = MagicMock()
    return controller


# =====================================================================
#  PUBLIC STORE PAGE
# =====================================================================
class TestPublicStore(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_unknown_store_redirects_home_with_warning(self):
        """A slug that doesn't match any approved store bounces the
        visitor back to the customer homepage."""
        self.controller._q.return_value = None
        with self.app.test_request_context("/store/missing-shop"):
            response = self.controller.public_store("missing-shop")
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("warning", "Store not found or not yet approved."), flashes)

    @patch("app.controllers.store_controller.render_template")
    def test_known_store_renders_storefront(self, mock_render):
        """An approved store renders its public storefront with its
        products, categories, owner, and review stats."""
        mock_render.return_value = "store_page"
        store_row = {"id": 1, "slug": "cool-shop", "user_id": 9}
        products = [{"id": 10, "name": "Widget"}]
        categories = [{"id": 1, "name": "Gadgets"}]
        owner = {"name": "Sam"}
        reviews_avg = {"avg": 4.5, "cnt": 3}

        # _q is called in sequence: store lookup, products, categories,
        # owner, reviews_avg.
        self.controller._q.side_effect = [store_row, products, categories, owner, reviews_avg]

        with self.app.test_request_context("/store/cool-shop?q=widget&sort=price_asc"):
            result = self.controller.public_store("cool-shop")
            self.assertEqual(result, "store_page")
            mock_render.assert_called_once()
            _, kwargs = mock_render.call_args
            self.assertEqual(kwargs["store"], store_row)
            self.assertEqual(kwargs["products"], products)
            self.assertEqual(kwargs["cats"], categories)
            self.assertEqual(kwargs["owner"], owner)
            self.assertEqual(kwargs["reviews_avg"], reviews_avg)
            self.assertEqual(kwargs["q"], "widget")
            self.assertEqual(kwargs["sort"], "price_asc")

    def test_store_product_redirects_to_product_detail(self):
        """A store-scoped product URL just forwards to the main
        product detail page."""
        with self.app.test_request_context("/store/cool-shop/product/42"):
            response = self.controller.store_product("cool-shop", 42)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/product/42"))


# =====================================================================
#  CHAT STARTED FROM A STORE PAGE
# =====================================================================
class TestStartChat(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_guest_must_log_in_before_chatting(self):
        """A visitor who isn't logged in is sent to the login page
        instead of starting a chat."""
        with self.app.test_request_context(method="POST"):
            response = self.controller.start_chat(5)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("warning", "Login to chat with seller."), flashes)

    def test_logged_in_user_starts_new_chat(self):
        """A logged-in customer with no existing chat gets a brand new
        one created and is redirected straight into it."""
        self.controller._q.return_value = None  # no existing chat
        self.controller._run.return_value = 77  # new chat id

        with self.app.test_request_context(method="POST", data={"product_id": "3"}):
            session["user_id"] = 1
            response = self.controller.start_chat(5)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chat/77"))
            self.controller._run.assert_called_once_with(
                "INSERT INTO chats (customer_id, seller_id, product_id) VALUES (%s,%s,%s)",
                (1, 5, 3)
            )

    def test_logged_in_user_resumes_existing_chat(self):
        """If a chat between this customer and seller already exists,
        no new row is created — the existing chat id is reused."""
        self.controller._q.return_value = {"id": 55}

        with self.app.test_request_context(method="POST", data={}):
            session["user_id"] = 1
            response = self.controller.start_chat(5)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chat/55"))
            self.controller._run.assert_not_called()


# =====================================================================
#  CHAT VIEW
# =====================================================================
class TestChatView(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_guest_is_redirected_to_login(self):
        with self.app.test_request_context():
            response = self.controller.chat_view(1)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)

    def test_chat_not_belonging_to_user_is_rejected(self):
        """A chat id that doesn't belong to the logged-in customer is
        treated as not found."""
        self.controller._q.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.chat_view(99)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Chat not found."), flashes)

    def test_post_sends_a_message(self):
        chat_row = {"id": 1, "customer_id": 1, "seller_id": 5}
        self.controller._q.return_value = chat_row

        with self.app.test_request_context(method="POST", data={"message": "Hello!"}):
            session["user_id"] = 1
            response = self.controller.chat_view(1)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chat/1"))
            self.controller._run.assert_called_once_with(
                "INSERT INTO chat_messages (chat_id, sender_id, message) VALUES (%s,%s,%s)",
                (1, 1, "Hello!")
            )

    def test_post_with_blank_message_sends_nothing(self):
        chat_row = {"id": 1, "customer_id": 1, "seller_id": 5}
        self.controller._q.return_value = chat_row

        with self.app.test_request_context(method="POST", data={"message": "   "}):
            session["user_id"] = 1
            self.controller.chat_view(1)
            self.controller._run.assert_not_called()

    @patch("app.controllers.store_controller.render_template")
    def test_get_renders_thread_and_marks_messages_read(self, mock_render):
        mock_render.return_value = "chat_page"
        chat_row = {"id": 1, "customer_id": 1, "seller_id": 5}
        msgs = [{"id": 1, "message": "hi"}]
        seller = {"name": "Sam", "store_name": "Cool Shop"}
        # _q called: chat lookup, msgs, seller
        self.controller._q.side_effect = [chat_row, msgs, seller]

        with self.app.test_request_context(method="GET"):
            session["user_id"] = 1
            result = self.controller.chat_view(1)
            self.assertEqual(result, "chat_page")
            mock_render.assert_called_once_with(
                "store/chat.html", chat=chat_row, msgs=msgs, seller=seller
            )
            # The seller's unread messages get marked as read.
            self.controller._run.assert_called_once_with(
                "UPDATE chat_messages SET is_read=1 WHERE chat_id=%s AND sender_id!=%s",
                (1, 1)
            )


if __name__ == "__main__":
    unittest.main()
