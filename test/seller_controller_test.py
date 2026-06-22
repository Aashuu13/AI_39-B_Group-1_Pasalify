import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages

from app.controllers.seller_controller import SellerController

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# A reusable helper that builds a tiny Flask app for every test.
# define the route names the controller redirects to
# (seller.setup, seller.dashboard, seller.products, seller.inventory,
# seller.orders, seller.store_profile, seller.store_customize,
# seller.chats, seller.chat_detail, seller.support_tickets,
# customer.order_detail) so that url_for() inside the controller can
# build URLs successfully.
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
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

<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
=======

>>>>>>> origin/sandesh
def make_controller():
    """
    Build a SellerController whose DB-touching helpers (_q/_run/_log/
    _notify/_save_file) are replaced with mocks, so tests exercise the
    controller's own logic instead of hitting a real database or disk.
    """
    controller = SellerController()
    controller._q = MagicMock(return_value=[])
    controller._run = MagicMock(return_value=1)
    controller._log = MagicMock()
    controller._notify = MagicMock()
    controller._save_file = MagicMock(return_value=None)
    return controller

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  STORE SETUP
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
class TestSetup(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.StoreModel")
    def test_existing_store_redirects_straight_to_dashboard(self, mock_store_model):
        mock_store_model.find_by_user.return_value = {"id": 1}
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.setup()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/dashboard"))

    @patch("app.controllers.seller_controller.render_template")
    @patch("app.controllers.seller_controller.StoreModel")
    def test_get_shows_setup_form_when_no_store_yet(self, mock_store_model, mock_render):
        mock_store_model.find_by_user.return_value = None
        mock_render.return_value = "setup_page"
        with self.app.test_request_context(method="GET"):
            session["user_id"] = 1
            result = self.controller.setup()
            self.assertEqual(result, "setup_page")

    @patch("app.controllers.seller_controller.StoreModel")
    def test_post_creates_store_and_redirects_to_dashboard(self, mock_store_model):
        mock_store_model.find_by_user.return_value = None
        mock_store_model.make_unique_slug.return_value = "cool-shop"
        mock_store_model.create.return_value = 5

        with self.app.test_request_context(
            method="POST", data={"name": "Cool Shop", "description": "Best shop"}
        ):
            session["user_id"] = 1
            response = self.controller.setup()
            mock_store_model.create.assert_called_once()
            created = mock_store_model.create.call_args[0][0]
            self.assertEqual(created["name"], "Cool Shop")
            self.assertEqual(created["slug"], "cool-shop")
            self.assertEqual(created["user_id"], 1)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/dashboard"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Store created successfully!"), flashes)

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  DASHBOARD
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.StoreModel")
    def test_redirects_to_setup_when_no_store(self, mock_store_model):
        mock_store_model.find_by_user.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.dashboard()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/setup"))

    @patch("app.controllers.seller_controller.render_template")
    @patch("app.controllers.seller_controller.OrderModel")
    @patch("app.controllers.seller_controller.ProductModel")
    @patch("app.controllers.seller_controller.StoreModel")
    def test_renders_dashboard_with_stats(
        self, mock_store_model, mock_product_model, mock_order_model, mock_render
    ):
        store = {"id": 1, "name": "Cool Shop"}
        mock_store_model.find_by_user.return_value = store
        mock_store_model.stats.return_value = {
            "total_sales": 1000, "total_orders": 5, "total_products": 3
        }
        mock_product_model.low_stock.return_value = []
        mock_order_model.find_by_store.return_value = []
        mock_order_model.monthly_revenue.return_value = []
        self.controller._q.return_value = []
        mock_render.return_value = "dashboard_page"

        with self.app.test_request_context():
            session["user_id"] = 1
            result = self.controller.dashboard()
            self.assertEqual(result, "dashboard_page")
            _, kwargs = mock_render.call_args
            self.assertEqual(kwargs["total_sales"], 1000)
            self.assertEqual(kwargs["total_orders"], 5)
            self.assertEqual(kwargs["total_products"], 3)

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  STORE PROFILE / CUSTOMIZE
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
class TestStoreProfile(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.StoreModel")
    def test_post_updates_profile_and_keeps_old_logo_if_none_uploaded(self, mock_store_model):
        store = {"id": 1, "logo": "uploads/logos/old.png", "banner": "uploads/banners/old.png"}
        mock_store_model.find_by_user.return_value = store
<<<<<<< HEAD
<<<<<<< HEAD
        self.controller._save_file.return_value = None  
=======
        self.controller._save_file.return_value = None  # no new file uploaded
>>>>>>> origin/aayushma
=======
        self.controller._save_file.return_value = None  # no new file uploaded
>>>>>>> origin/sandesh

        with self.app.test_request_context(
            method="POST", data={"name": "New Name", "description": "New desc"}
        ):
            session["user_id"] = 1
            response = self.controller.store_profile()
            mock_store_model.update.assert_called_once()
            updated = mock_store_model.update.call_args[0][1]
            self.assertEqual(updated["logo"], "uploads/logos/old.png")
            self.assertEqual(updated["banner"], "uploads/banners/old.png")
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Store profile updated!"), flashes)

<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
=======

>>>>>>> origin/sandesh
class TestStoreCustomize(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.StoreModel")
    def test_post_saves_theme_settings(self, mock_store_model):
        mock_store_model.find_by_user.return_value = {"id": 1}
        with self.app.test_request_context(
            method="POST", data={"theme_color": "#000000", "theme_layout": "list"}
        ):
            session["user_id"] = 1
            response = self.controller.store_customize()
            mock_store_model.update.assert_called_once_with(
                1, {"theme_color": "#000000", "theme_layout": "list"}
            )
            self.assertEqual(response.status_code, 302)

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  PRODUCTS
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
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
    def test_product_add_post_creates_product_and_images(
        self, mock_store_model, mock_product_model, mock_category_model
    ):
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
    def test_product_edit_missing_product_redirects(
        self, mock_store_model, mock_product_model, mock_category_model
    ):
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
    def test_product_edit_post_updates_product(
        self, mock_store_model, mock_product_model, mock_category_model
    ):
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  CATEGORIES (read-only for sellers)
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  INVENTORY
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  ORDERS
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
class TestOrders(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.OrderModel")
    def test_order_update_with_valid_status_notifies_buyer(self, mock_order_model):
        mock_order_model.find_by_id.return_value = {
            "id": 1, "user_id": 2, "order_number": "ORD-1"
        }
        with self.app.test_request_context(method="POST", data={"status": "shipped"}):
            response = self.controller.order_update(1)
            mock_order_model.update.assert_called_once_with(1, {"status": "shipped"})
            self.controller._notify.assert_called_once()
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Order status updated."), flashes)

    @patch("app.controllers.seller_controller.OrderModel")
    def test_order_update_with_invalid_status_does_nothing(self, mock_order_model):
        with self.app.test_request_context(method="POST", data={"status": "bogus"}):
            response = self.controller.order_update(1)
            mock_order_model.update.assert_not_called()
            self.assertEqual(response.status_code, 302)

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  CHAT
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/sandesh

# =====================================================================
#  SUPPORT TICKETS (seller-scoped)
# =====================================================================
<<<<<<< HEAD
>>>>>>> origin/aayushma
=======
>>>>>>> origin/sandesh
class TestSupportTickets(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.seller_controller.StoreModel")
    def test_support_reply_rejects_empty_message(self, mock_store_model):
        mock_store_model.find_by_user.return_value = {"id": 1, "name": "Cool Shop"}
        with self.app.test_request_context(
            method="POST", data={"customer_id": "1", "message": ""}
        ):
            session["user_id"] = 1
            response = self.controller.support_reply()
            self.controller._run.assert_not_called()
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Reply cannot be empty."), flashes)

    @patch("app.controllers.seller_controller.StoreModel")
    def test_support_reply_creates_chat_and_sends_message(self, mock_store_model):
        mock_store_model.find_by_user.return_value = {"id": 1, "name": "Cool Shop"}
<<<<<<< HEAD
<<<<<<< HEAD
        self.controller._q.return_value = None  
        self.controller._run.return_value = 88  
=======
        self.controller._q.return_value = None  # no existing chat
        self.controller._run.return_value = 88  # new chat id
>>>>>>> origin/aayushma
=======
        self.controller._q.return_value = None  # no existing chat
        self.controller._run.return_value = 88  # new chat id
>>>>>>> origin/sandesh

        with self.app.test_request_context(
            method="POST", data={"customer_id": "2", "message": "We'll help!"}
        ):
            session["user_id"] = 1
            response = self.controller.support_reply()
            self.controller._notify.assert_called_once()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/chats/88"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Message sent to customer."), flashes)

<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
=======

>>>>>>> origin/sandesh
if __name__ == "__main__":
    unittest.main()
