"""
customer_controller_test.py — Yubraj's features:
  Sprint 2: view product (home, products, product_detail)
  Sprint 3: edit customer profile, customer chat
  Sprint 5: store URL (stores, store_page)
"""
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages

from app.controllers.customer_controller import CustomerController


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    customer_bp = Blueprint("customer", __name__)
    customer_bp.route("/", endpoint="home")(lambda: "home")
    customer_bp.route("/products", endpoint="products")(lambda: "products")
    customer_bp.route("/product/<int:pid>", endpoint="product_detail")(lambda pid: f"product {pid}")
    customer_bp.route("/profile", endpoint="profile")(lambda: "profile")
    customer_bp.route("/chats", endpoint="chats")(lambda: "chats")
    customer_bp.route("/chat/<int:cid>", endpoint="chat_detail")(lambda cid: f"chat {cid}")
    customer_bp.route("/stores", endpoint="stores")(lambda: "stores")
    app.register_blueprint(customer_bp)

    return app


def make_controller():
    controller = CustomerController()
    controller._q = MagicMock(return_value=[])
    controller._run = MagicMock(return_value=1)
    controller._log = MagicMock()
    controller._notify = MagicMock()
    return controller


# =====================================================================
#  SPRINT 2: VIEW PRODUCT
# =====================================================================
class TestHomeAndDiscovery(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.customer_controller.render_template")
    @patch("app.controllers.customer_controller.CategoryModel")
    def test_home_renders_categories_and_featured_products(self, mock_category_model, mock_render):
        mock_category_model.find_all.return_value = [{"id": 1, "name": "Gadgets"}]
        self.controller._q.return_value = [{"id": 1, "name": "Widget"}]
        mock_render.return_value = "home_page"
        with self.app.test_request_context():
            result = self.controller.home()
            self.assertEqual(result, "home_page")
            mock_render.assert_called_once_with(
                "customer/home.html",
                cats=[{"id": 1, "name": "Gadgets"}],
                featured=[{"id": 1, "name": "Widget"}],
            )

    @patch("app.controllers.customer_controller.render_template")
    @patch("app.controllers.customer_controller.CategoryModel")
    @patch("app.controllers.customer_controller.ProductModel")
    def test_products_delegates_search_to_product_model(self, mock_product_model, mock_category_model, mock_render):
        mock_product_model.search.return_value = [{"id": 1}]
        mock_category_model.find_all.return_value = []
        mock_render.return_value = "products_page"
        with self.app.test_request_context("/customer/products?q=phone&sort=price_asc"):
            result = self.controller.products()
            self.assertEqual(result, "products_page")
            mock_product_model.search.assert_called_once_with(
                query="phone", cat_slug="", min_price="", max_price="",
                sort="price_asc", min_rating="",
            )

    @patch("app.controllers.customer_controller.ProductModel")
    def test_product_detail_not_found_redirects(self, mock_product_model):
        mock_product_model.get_with_images.return_value = None
        with self.app.test_request_context():
            response = self.controller.product_detail(99)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/products"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Product not found."), flashes)

    @patch("app.controllers.customer_controller.render_template")
    @patch("app.controllers.customer_controller.ReviewModel")
    @patch("app.controllers.customer_controller.ProductModel")
    def test_product_detail_renders_for_guest(self, mock_product_model, mock_review_model, mock_render):
        mock_product_model.get_with_images.return_value = {"id": 1, "category_id": 2}
        mock_review_model.find_by_product.return_value = []
        self.controller._q.side_effect = [[], []]
        mock_render.return_value = "product_page"
        with self.app.test_request_context():
            result = self.controller.product_detail(1)
            self.assertEqual(result, "product_page")
            _, kwargs = mock_render.call_args
            self.assertFalse(kwargs["in_wish"])


# =====================================================================
#  SPRINT 3: EDIT CUSTOMER PROFILE
# =====================================================================
class TestProfile(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.customer_controller.UserModel")
    def test_profile_post_updates_and_syncs_session_name(self, mock_user_model):
        mock_user_model.find_by_id.return_value = {"id": 1, "name": "Old Name"}
        with self.app.test_request_context(
            method="POST",
            data={"name": "New Name", "phone": "98", "address": "Addr", "city": "KTM"},
        ):
            session["user_id"] = 1
            response = self.controller.profile()
            mock_user_model.update.assert_called_once_with(
                1, {"name": "New Name", "phone": "98", "address": "Addr", "city": "KTM"}
            )
            self.assertEqual(session["name"], "New Name")
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Profile updated!"), flashes)

    @patch("app.controllers.customer_controller.render_template")
    @patch("app.controllers.customer_controller.UserModel")
    def test_profile_get_renders_with_stats(self, mock_user_model, mock_render):
        mock_user_model.find_by_id.return_value = {"id": 1, "name": "Bob"}
        self.controller._q.side_effect = [{"c": 3}, {"c": 5}]
        mock_render.return_value = "profile_page"
        with self.app.test_request_context(method="GET"):
            session["user_id"] = 1
            result = self.controller.profile()
            self.assertEqual(result, "profile_page")
            _, kwargs = mock_render.call_args
            self.assertEqual(kwargs["orders_count"], 3)
            self.assertEqual(kwargs["wish_count"], 5)


# =====================================================================
#  SPRINT 3: CUSTOMER CHAT
# =====================================================================
class TestChat(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_chat_start_creates_new_chat_when_none_exists(self):
        self.controller._q.side_effect = [{"id": 9, "user_id": 5}, None]
        self.controller._run.return_value = 33
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.chat_start(9)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chat/33"))

    def test_chat_start_unknown_store_redirects_home(self):
        self.controller._q.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.chat_start(999)
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Store not found."), flashes)

    def test_chat_detail_not_found_redirects(self):
        self.controller._q.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.chat_detail(5)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chats"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Not found."), flashes)

    def test_chat_detail_post_sends_message(self):
        self.controller._q.return_value = {"id": 5, "customer_id": 1, "seller_id": 2}
        with self.app.test_request_context(method="POST", data={"message": "Hello"}):
            session["user_id"] = 1
            response = self.controller.chat_detail(5)
            self.controller._run.assert_called_once_with(
                "INSERT INTO chat_messages (chat_id, sender_id, message) VALUES (%s,%s,%s)",
                (5, 1, "Hello")
            )
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chat/5"))


# =====================================================================
#  SPRINT 5: STORE URL
# =====================================================================
class TestStores(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.customer_controller.render_template")
    def test_stores_without_query_lists_all_approved(self, mock_render):
        mock_render.return_value = "stores_page"
        self.controller._q.return_value = [{"id": 1, "name": "Cool Shop"}]
        with self.app.test_request_context():
            result = self.controller.stores()
            self.assertEqual(result, "stores_page")
            self.controller._q.assert_called_once_with(
                "SELECT * FROM stores WHERE is_approved = 1"
            )

    @patch("app.controllers.customer_controller.render_template")
    def test_store_page_not_found_redirects(self, mock_render):
        self.controller._q.return_value = None
        with self.app.test_request_context():
            response = self.controller.store_page("missing-shop")
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/stores"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Store not found."), flashes)


if __name__ == "__main__":
    unittest.main()
