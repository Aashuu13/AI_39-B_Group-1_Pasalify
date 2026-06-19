"""
seller_controller_test.py — Yubraj's features:
  Sprint 3: seller chat
  Sprint 4: organize product (products, categories, inventory)
"""
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages

from app.controllers.seller_controller import SellerController


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    seller_bp = Blueprint("seller", __name__)
    seller_bp.route("/setup", endpoint="setup")(lambda: "setup")
    seller_bp.route("/dashboard", endpoint="dashboard")(lambda: "dashboard")
    seller_bp.route("/products", endpoint="products")(lambda: "products")
    seller_bp.route("/inventory", endpoint="inventory")(lambda: "inventory")
    seller_bp.route("/orders", endpoint="orders")(lambda: "orders")
    seller_bp.route("/store/profile", endpoint="store_profile")(lambda: "store_profile")
    seller_bp.route("/store/customize", endpoint="store_customize")(lambda: "store_customize")
    seller_bp.route("/chats", endpoint="chats")(lambda: "chats")
    seller_bp.route("/chats/<int:cid>", endpoint="chat_detail")(lambda cid: f"chat {cid}")
    seller_bp.route("/support", endpoint="support_tickets")(lambda: "support_tickets")
    app.register_blueprint(seller_bp)

    customer_bp = Blueprint("customer", __name__)
    customer_bp.route("/order/<int:oid>", endpoint="order_detail")(lambda oid: f"order {oid}")
    app.register_blueprint(customer_bp)

    return app


def make_controller():
    controller = SellerController()
    controller._q = MagicMock(return_value=[])
    controller._run = MagicMock(return_value=1)
    controller._log = MagicMock()
    controller._notify = MagicMock()
    controller._save_file = MagicMock(return_value=None)
    return controller


# =====================================================================
#  SPRINT 4: ORGANIZE PRODUCT — Products CRUD
# =====================================================================
class TestProducts(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.StoreModel")
    def test_products_requires_store(self, mock_store_model):
        mock_store_model.find_by_user.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.products()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/setup"))

    @patch("app.controllers.seller_controller.CategoryModel")
    @patch("app.controllers.seller_controller.ProductModel")
    @patch("app.controllers.seller_controller.StoreModel")
    def test_product_add_post_creates_product(self, mock_store_model, mock_product_model, mock_category_model):
        mock_store_model.find_by_user.return_value = {"id": 1}
        mock_category_model.find_all.return_value = []
        mock_product_model.create.return_value = 10
        with self.app.test_request_context(
            method="POST",
            data={"name": "Cool Widget", "price": "100", "stock_qty": "5"},
        ):
            session["user_id"] = 1
            response = self.controller.product_add()
            mock_product_model.create.assert_called_once()
            created = mock_product_model.create.call_args[0][0]
            self.assertEqual(created["name"], "Cool Widget")
            self.assertEqual(created["slug"], "cool-widget")
            self.assertEqual(created["store_id"], 1)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/products"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Product added successfully!"), flashes)

    @patch("app.controllers.seller_controller.CategoryModel")
    @patch("app.controllers.seller_controller.ProductModel")
    @patch("app.controllers.seller_controller.StoreModel")
    def test_product_edit_missing_product_redirects(self, mock_store_model, mock_product_model, mock_category_model):
        mock_store_model.find_by_user.return_value = {"id": 1}
        mock_product_model.find_where.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.product_edit(99)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/products"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Product not found."), flashes)

    @patch("app.controllers.seller_controller.CategoryModel")
    @patch("app.controllers.seller_controller.ProductModel")
    @patch("app.controllers.seller_controller.StoreModel")
    def test_product_edit_post_updates_product(self, mock_store_model, mock_product_model, mock_category_model):
        mock_store_model.find_by_user.return_value = {"id": 1}
        mock_product_model.find_where.return_value = {"id": 7, "name": "Old Name"}
        mock_category_model.find_all.return_value = []
        with self.app.test_request_context(
            method="POST",
            data={"name": "New Name", "price": "150", "stock_qty": "3"},
        ):
            session["user_id"] = 1
            response = self.controller.product_edit(7)
            mock_product_model.update.assert_called_once()
            updated = mock_product_model.update.call_args[0][1]
            self.assertEqual(updated["name"], "New Name")
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Product updated!"), flashes)

    @patch("app.controllers.seller_controller.ProductModel")
    @patch("app.controllers.seller_controller.StoreModel")
    def test_product_delete_soft_deletes(self, mock_store_model, mock_product_model):
        mock_store_model.find_by_user.return_value = {"id": 1}
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.product_delete(7)
            mock_product_model.soft_delete.assert_called_once_with(7)
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("info", "Product removed."), flashes)


# =====================================================================
#  SPRINT 4: CATEGORIES (read-only)
# =====================================================================
class TestCategories(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.render_template")
    @patch("app.controllers.seller_controller.CategoryModel")
    def test_categories_renders_all(self, mock_category_model, mock_render):
        mock_category_model.find_all.return_value = [{"id": 1, "name": "Gadgets"}]
        mock_render.return_value = "categories_page"
        with self.app.test_request_context():
            result = self.controller.categories()
            self.assertEqual(result, "categories_page")
            mock_render.assert_called_once_with(
                "seller/categories.html", cats=[{"id": 1, "name": "Gadgets"}]
            )


# =====================================================================
#  SPRINT 4: INVENTORY
# =====================================================================
class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.ProductModel")
    @patch("app.controllers.seller_controller.StoreModel")
    def test_inventory_update_never_goes_negative(self, mock_store_model, mock_product_model):
        mock_store_model.find_by_user.return_value = {"id": 1}
        with self.app.test_request_context(method="POST", data={"stock_qty": "-5"}):
            session["user_id"] = 1
            response = self.controller.inventory_update(3)
            self.controller._run.assert_called_once_with(
                "UPDATE products SET stock_qty = %s WHERE id = %s AND store_id = %s",
                (0, 3, 1)
            )
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Stock updated!"), flashes)


# =====================================================================
#  SPRINT 3: SELLER CHAT
# =====================================================================
class TestChat(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_chat_detail_unknown_chat_redirects(self):
        self.controller._q.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.chat_detail(99)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chats"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Not found."), flashes)

    def test_chat_detail_post_sends_message(self):
        self.controller._q.return_value = {"id": 5, "customer_id": 2, "seller_id": 1}
        with self.app.test_request_context(method="POST", data={"message": "Hi there"}):
            session["user_id"] = 1
            response = self.controller.chat_detail(5)
            self.controller._run.assert_called_once_with(
                "INSERT INTO chat_messages (chat_id, sender_id, message) VALUES (%s,%s,%s)",
                (5, 1, "Hi there")
            )
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chats/5"))


if __name__ == "__main__":
    unittest.main()
