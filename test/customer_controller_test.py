import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages

from app.controllers.customer_controller import CustomerController

<<<<<<< HEAD
=======

# A reusable helper that builds a tiny Flask app for every test.
# define the route names the controller redirects to
# (customer.products, customer.cart, customer.wishlist,
# customer.order_detail, customer.orders, customer.profile,
# customer.product_detail, customer.chats, customer.chat_detail,
# customer.stores, customer.home) so that url_for() inside the
# controller can build URLs successfully.
>>>>>>> origin/aayushma
def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    customer_bp = Blueprint("customer", __name__)
    customer_bp.route("/", endpoint="home")(lambda: "home")
    customer_bp.route("/products", endpoint="products")(lambda: "products")
    customer_bp.route("/product/<int:pid>", endpoint="product_detail")(lambda pid: f"product {pid}")
    customer_bp.route("/cart", endpoint="cart")(lambda: "cart")
    customer_bp.route("/wishlist", endpoint="wishlist")(lambda: "wishlist")
    customer_bp.route("/orders", endpoint="orders")(lambda: "orders")
    customer_bp.route("/order/<int:oid>", endpoint="order_detail")(lambda oid: f"order {oid}")
    customer_bp.route("/profile", endpoint="profile")(lambda: "profile")
    customer_bp.route("/chats", endpoint="chats")(lambda: "chats")
    customer_bp.route("/chat/<int:cid>", endpoint="chat_detail")(lambda cid: f"chat {cid}")
    customer_bp.route("/stores", endpoint="stores")(lambda: "stores")
    app.register_blueprint(customer_bp)

    return app

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
def make_controller():
    """
    Build a CustomerController whose DB-touching helpers (_q/_run/_log/
    _notify) are replaced with mocks, so tests exercise the
    controller's own logic instead of hitting a real database.
    """
    controller = CustomerController()
    controller._q = MagicMock(return_value=[])
    controller._run = MagicMock(return_value=1)
    controller._log = MagicMock()
    controller._notify = MagicMock()
    return controller

<<<<<<< HEAD
=======

# =====================================================================
#  HOME / DISCOVERY
# =====================================================================
>>>>>>> origin/aayushma
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
    def test_products_delegates_search_to_product_model(
        self, mock_product_model, mock_category_model, mock_render
    ):
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
    def test_product_detail_renders_for_guest(
        self, mock_product_model, mock_review_model, mock_render
    ):
        mock_product_model.get_with_images.return_value = {"id": 1, "category_id": 2}
        mock_review_model.find_by_product.return_value = []
<<<<<<< HEAD

=======
        # _q called for: images, related (no wishlist check for guests)
>>>>>>> origin/aayushma
        self.controller._q.side_effect = [[], []]
        mock_render.return_value = "product_page"
        with self.app.test_request_context():
            result = self.controller.product_detail(1)
            self.assertEqual(result, "product_page")
            _, kwargs = mock_render.call_args
            self.assertFalse(kwargs["in_wish"])

<<<<<<< HEAD
=======

# =====================================================================
#  CART
# =====================================================================
>>>>>>> origin/aayushma
class TestCart(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.customer_controller.ProductModel")
    def test_cart_add_fails_when_not_enough_stock(self, mock_product_model):
        mock_product_model.find_by_id.return_value = {"id": 1, "stock_qty": 1}
        with self.app.test_request_context(method="POST", data={"quantity": "5"}):
            session["user_id"] = 1
            response = self.controller.cart_add(1)
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Not enough stock."), flashes)
            self.controller._run.assert_not_called()

    @patch("app.controllers.customer_controller.ProductModel")
    def test_cart_add_inserts_new_row_when_not_already_in_cart(self, mock_product_model):
        mock_product_model.find_by_id.return_value = {"id": 1, "stock_qty": 10}
<<<<<<< HEAD
        self.controller._q.return_value = None  
=======
        self.controller._q.return_value = None  # no existing cart row
>>>>>>> origin/aayushma
        with self.app.test_request_context(method="POST", data={"quantity": "2"}):
            session["user_id"] = 1
            response = self.controller.cart_add(1)
            self.controller._run.assert_called_once_with(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s,%s,%s)",
                (1, 1, 2)
            )
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Added to cart!"), flashes)

    @patch("app.controllers.customer_controller.ProductModel")
    def test_cart_add_bumps_quantity_when_already_in_cart(self, mock_product_model):
        mock_product_model.find_by_id.return_value = {"id": 1, "stock_qty": 10}
        self.controller._q.return_value = {"id": 9, "quantity": 1}
        with self.app.test_request_context(method="POST", data={"quantity": "2"}):
            session["user_id"] = 1
            self.controller.cart_add(1)
            self.controller._run.assert_called_once_with(
                "UPDATE cart_items SET quantity = quantity + %s WHERE id = %s", (2, 9)
            )

    def test_cart_update_deletes_when_quantity_below_one(self):
        with self.app.test_request_context(method="POST", data={"quantity": "0"}):
            session["user_id"] = 1
            response = self.controller.cart_update(5)
            self.controller._run.assert_called_once_with(
                "DELETE FROM cart_items WHERE id = %s AND user_id = %s", (5, 1)
            )
            self.assertEqual(response.status_code, 302)

    def test_cart_update_sets_exact_quantity(self):
        with self.app.test_request_context(method="POST", data={"quantity": "4"}):
            session["user_id"] = 1
            self.controller.cart_update(5)
            self.controller._run.assert_called_once_with(
                "UPDATE cart_items SET quantity = %s WHERE id = %s AND user_id = %s",
                (4, 5, 1)
            )

    def test_cart_remove_deletes_item(self):
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.cart_remove(5)
            self.controller._run.assert_called_once_with(
                "DELETE FROM cart_items WHERE id = %s AND user_id = %s", (5, 1)
            )
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("info", "Item removed."), flashes)

<<<<<<< HEAD
=======

# =====================================================================
#  WISHLIST
# =====================================================================
>>>>>>> origin/aayushma
class TestWishlist(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_wishlist_toggle_adds_when_not_present(self):
        self.controller._q.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.wishlist_toggle(7)
            self.controller._run.assert_called_once_with(
                "INSERT IGNORE INTO wishlists (user_id, product_id) VALUES (%s,%s)", (1, 7)
            )
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Added to wishlist!"), flashes)
            self.assertEqual(response.status_code, 302)

    def test_wishlist_toggle_removes_when_present(self):
        self.controller._q.return_value = {"id": 22}
        with self.app.test_request_context():
            session["user_id"] = 1
            self.controller.wishlist_toggle(7)
            self.controller._run.assert_called_once_with(
                "DELETE FROM wishlists WHERE id = %s", (22,)
            )
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("info", "Removed from wishlist."), flashes)

<<<<<<< HEAD
=======

# =====================================================================
#  CHECKOUT
# =====================================================================
>>>>>>> origin/aayushma
class TestCheckout(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_checkout_with_empty_cart_redirects(self):
        self.controller._q.return_value = []
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.checkout()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/cart"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("warning", "Your cart is empty."), flashes)

    @patch("app.controllers.customer_controller.ProductModel")
    @patch("app.controllers.customer_controller.UserModel")
    def test_checkout_post_creates_order_and_clears_cart(self, mock_user_model, mock_product_model):
        mock_user_model.find_by_id.return_value = {"id": 1, "name": "Bob"}
        cart_items = [{
            "product_id": 10, "store_id": 3, "name": "Widget",
            "price": 100.0, "quantity": 2,
        }]
<<<<<<< HEAD

=======
        # _q call order inside checkout():
        #   1) cart items (via _cart_items -> self._q)
        #   2) store lookup for commission
        #   3) order_item id lookup for commission insert
>>>>>>> origin/aayushma
        self.controller._q.side_effect = [
            cart_items,
            {"id": 3, "commission_rate": 10},
            {"id": 55},
        ]
<<<<<<< HEAD
        self.controller._run.return_value = 999  
=======
        self.controller._run.return_value = 999  # order id
>>>>>>> origin/aayushma

        with self.app.test_request_context(
            method="POST",
            data={
                "full_name": "Bob", "phone": "98000000", "address": "Addr",
                "city": "KTM", "payment_method": "cod",
            },
        ):
            session["user_id"] = 1
            response = self.controller.checkout()
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/order/999"))
            self.controller._notify.assert_called_once()
            flashes = get_flashed_messages(with_categories=True)
            self.assertTrue(any(cat == "success" for cat, _ in flashes))

    def test_validate_promo_returns_json(self):
<<<<<<< HEAD
        self.controller._q.return_value = None  
=======
        self.controller._q.return_value = None  # invalid/missing promo code
>>>>>>> origin/aayushma
        with self.app.test_request_context(
            method="POST", data={"code": "SAVE10", "subtotal": "500"}
        ):
            session["user_id"] = 1
            response = self.controller.validate_promo()
            data = response.get_json()
            self.assertIn("valid", data)
            self.assertIn("discount", data)
            self.assertIn("message", data)
            self.assertFalse(data["valid"])

<<<<<<< HEAD
=======

# =====================================================================
#  ORDERS
# =====================================================================
>>>>>>> origin/aayushma
class TestOrders(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.customer_controller.render_template")
    def test_orders_lists_this_users_orders(self, mock_render):
        mock_render.return_value = "orders_page"
        self.controller._q.return_value = [{"id": 1}]
        with self.app.test_request_context():
            session["user_id"] = 1
            result = self.controller.orders()
            self.assertEqual(result, "orders_page")
            mock_render.assert_called_once_with("customer/orders.html", orders=[{"id": 1}])

    def test_order_detail_not_found_redirects(self):
        self.controller._q.return_value = None
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.order_detail(99)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/orders"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Order not found."), flashes)

    @patch("app.controllers.customer_controller.render_template")
    def test_order_detail_renders_for_owner(self, mock_render):
        order = {"id": 5, "user_id": 1}
        items = [{"id": 1, "product_id": 10}]
        self.controller._q.side_effect = [order, items]
        mock_render.return_value = "order_detail_page"
        with self.app.test_request_context():
            session["user_id"] = 1
            result = self.controller.order_detail(5)
            self.assertEqual(result, "order_detail_page")

<<<<<<< HEAD
=======

# =====================================================================
#  REVIEWS
# =====================================================================
>>>>>>> origin/aayushma
class TestReviews(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.customer_controller.ProductModel")
    def test_submit_review_inserts_and_updates_rating(self, mock_product_model):
        with self.app.test_request_context(
            method="POST",
            data={"rating": "4", "title": "Nice", "body": "Good product"},
        ):
            session["user_id"] = 1
            response = self.controller.submit_review(7)
            self.controller._run.assert_called_once()
            mock_product_model.update_rating.assert_called_once_with(7)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/product/7"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Review submitted!"), flashes)

<<<<<<< HEAD
=======

# =====================================================================
#  PROFILE
# =====================================================================
>>>>>>> origin/aayushma
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

<<<<<<< HEAD
=======

# =====================================================================
#  NOTIFICATIONS
# =====================================================================
>>>>>>> origin/aayushma
class TestNotifications(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.customer_controller.render_template")
    def test_notifications_marks_all_as_read(self, mock_render):
        mock_render.return_value = "notif_page"
        self.controller._q.return_value = [{"id": 1}]
        with self.app.test_request_context():
            session["user_id"] = 1
            result = self.controller.notifications()
            self.assertEqual(result, "notif_page")
            self.controller._run.assert_called_once_with(
                "UPDATE notifications SET is_read = 1 WHERE user_id = %s", (1,)
            )

    def test_notif_count_returns_json_count(self):
        self.controller._q.return_value = {"c": 4}
        with self.app.test_request_context():
            session["user_id"] = 1
            response = self.controller.notif_count()
            data = response.get_json()
            self.assertEqual(data["count"], 4)

<<<<<<< HEAD
=======

# =====================================================================
#  SUPPORT CHATBOT
# =====================================================================
>>>>>>> origin/aayushma
class TestSupportChatbot(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.customer_controller.render_template")
    def test_support_page_open_to_guest(self, mock_render):
        mock_render.return_value = "support_page"
        with self.app.test_request_context():
            result = self.controller.support()
            self.assertEqual(result, "support_page")
            mock_render.assert_called_once_with("customer/support.html", history=[])

    def test_support_chat_matches_known_keyword(self):
        with self.app.test_request_context(
            method="POST", data={"message": "What is my order status?"}
        ):
            response = self.controller.support_chat()
            data = response.get_json()
            self.assertIn("track your orders", data["reply"])
            self.assertEqual(self.controller._run.call_count, 2)

    def test_support_chat_falls_back_for_unknown_message(self):
        with self.app.test_request_context(method="POST", data={"message": "asdkjasldkj"}):
            response = self.controller.support_chat()
            data = response.get_json()
            self.assertIn("Sorry, I didn't understand", data["reply"])

<<<<<<< HEAD
=======

# =====================================================================
#  STORES (directory)
# =====================================================================
>>>>>>> origin/aayushma
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

<<<<<<< HEAD
=======

# =====================================================================
#  CHAT (customer side)
# =====================================================================
>>>>>>> origin/aayushma
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

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
if __name__ == "__main__":
    unittest.main()
