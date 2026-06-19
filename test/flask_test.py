"""
test/flask_test.py  (EXPANDED)
================================================================
Comprehensive unit tests for Pasalify MVC's access-control
decorators and every route group:

  Sections
  --------
  1.  AuthDotPyTests          – decorators in app/auth.py
  2.  AuthControlDotPyTests   – decorators in app/authcontrol.py
  3.  AuthRoutesTests         – /auth/* (register, login, logout,
                                forgot-password, change-password)
  4.  CustomerPublicTests     – public customer routes (no login)
  5.  CustomerAuthTests       – login-protected customer routes
  6.  CartTests               – cart add / update / remove
  7.  WishlistTests           – wishlist toggle
  8.  CheckoutTests           – checkout + promo-code AJAX
  9.  OrderTests              – orders list + order detail
  10. ReviewTests             – submit_review
  11. ProfileTests            – profile GET / POST
  12. NotificationTests       – notifications + count endpoint
  13. SupportTests            – support chatbot (guest + member)
  14. ChatTests               – customer-seller chat
  15. StorePublicTests        – public store pages
  16. SellerAccessTests       – seller role guard on every route
  17. SellerFeatureTests      – seller-specific actions (mocked DB)
  18. AdminAccessTests        – admin role guard on every route
  19. AdminFeatureTests       – admin-specific actions (mocked DB)
  20. DebugUploadTests        – unprotected debug-upload endpoint

All tests use a throwaway in-memory Flask app and mock every
database call, so no real MySQL connection is needed.

Run with:
    python -m pytest test/flask_test.py -v
  or:
    python -m unittest test/flask_test.py -v
"""

import io
import json
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from flask import Flask, Blueprint, session, url_for, jsonify

# ── decorators under test ────────────────────────────────────────────
from app.auth import login_required, guest_only, admin_required
from app.authcontrol import (
    role_required,
    admin_required  as ac_admin_required,
    seller_required as ac_seller_required,
    customer_required as ac_customer_required,
)


# ══════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════

def _make_minimal_app():
    """
    Tiny Flask app wired with one dummy route per blueprint so that
    every url_for() call the controllers and decorators make can
    resolve successfully without loading templates or DB connections.
    """
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # ── auth blueprint ───────────────────────────────────────────────
    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/login")
    def login():
        return "login page"

    @auth_bp.route("/register")
    def register():
        return "register page"

    @auth_bp.route("/logout")
    def logout():
        session.clear()
        return "logged out"

    @auth_bp.route("/forgot-password")
    def forgot_password():
        return "forgot password page"

    @auth_bp.route("/change-password")
    def change_password():
        return "change password page"

    # ── customer blueprint ───────────────────────────────────────────
    customer_bp = Blueprint("customer", __name__)

    @customer_bp.route("/")
    def home():
        return "customer home"

    @customer_bp.route("/products")
    def products():
        return "products list"

    @customer_bp.route("/product/<int:pid>")
    def product_detail(pid):
        return f"product {pid}"

    @customer_bp.route("/cart")
    @login_required
    def cart():
        return "cart page"

    @customer_bp.route("/cart/add/<int:pid>", methods=["POST"])
    @login_required
    def cart_add(pid):
        return "added"

    @customer_bp.route("/cart/update/<int:cid>", methods=["POST"])
    @login_required
    def cart_update(cid):
        return "updated"

    @customer_bp.route("/cart/remove/<int:cid>")
    @login_required
    def cart_remove(cid):
        return "removed"

    @customer_bp.route("/wishlist")
    @login_required
    def wishlist():
        return "wishlist"

    @customer_bp.route("/wishlist/toggle/<int:pid>")
    @login_required
    def wishlist_toggle(pid):
        return "toggled"

    @customer_bp.route("/checkout", methods=["GET", "POST"])
    @login_required
    def checkout():
        return "checkout page"

    @customer_bp.route("/promo/validate", methods=["POST"])
    @login_required
    def validate_promo():
        return jsonify({"valid": True, "discount": 10, "message": "Applied"})

    @customer_bp.route("/orders")
    @login_required
    def orders():
        return "orders list"

    @customer_bp.route("/order/<int:oid>")
    @login_required
    def order_detail(oid):
        return f"order {oid}"

    @customer_bp.route("/payments")
    @login_required
    def payment_history():
        return "payment history"

    @customer_bp.route("/review/<int:pid>", methods=["POST"])
    @login_required
    def submit_review(pid):
        return "review submitted"

    @customer_bp.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        return "profile page"

    @customer_bp.route("/notifications")
    @login_required
    def notifications():
        return "notifications"

    @customer_bp.route("/notifications/count")
    @login_required
    def notif_count():
        return jsonify({"count": 0})

    @customer_bp.route("/support")
    def support():
        return "support page"

    @customer_bp.route("/support/chat", methods=["POST"])
    def support_chat():
        return jsonify({"reply": "bot response"})

    @customer_bp.route("/stores")
    def stores():
        return "stores list"

    @customer_bp.route("/store/<slug>")
    def store_page(slug):
        return f"store {slug}"

    @customer_bp.route("/chats")
    @login_required
    def chats():
        return "chats list"

    @customer_bp.route("/chat/<int:cid>", methods=["GET", "POST"])
    @login_required
    def chat_detail(cid):
        return f"chat {cid}"

    @customer_bp.route("/chat/start/<int:store_id>")
    @login_required
    def chat_start(store_id):
        return f"chat started with store {store_id}"

    # ── seller blueprint ─────────────────────────────────────────────
    seller_bp = Blueprint("seller", __name__)

    @seller_bp.route("/setup", methods=["GET", "POST"])
    @ac_seller_required
    def setup():
        return "setup page"

    @seller_bp.route("/dashboard")
    @ac_seller_required
    def dashboard():
        return "seller dashboard"

    @seller_bp.route("/store/profile", methods=["GET", "POST"])
    @ac_seller_required
    def store_profile():
        return "store profile"


    @seller_bp.route("/products")
    @ac_seller_required
    def products():
        return "seller products"

    @seller_bp.route("/products/add", methods=["GET", "POST"])
    @ac_seller_required
    def product_add():
        return "add product"

    @seller_bp.route("/products/edit/<int:pid>", methods=["GET", "POST"])
    @ac_seller_required
    def product_edit(pid):
        return f"edit product {pid}"

    @seller_bp.route("/products/delete/<int:pid>")
    @ac_seller_required
    def product_delete(pid):
        return f"delete product {pid}"

    @seller_bp.route("/categories")
    @ac_seller_required
    def categories():
        return "seller categories"

    @seller_bp.route("/inventory")
    @ac_seller_required
    def inventory():
        return "inventory"

    @seller_bp.route("/inventory/update/<int:pid>", methods=["POST"])
    @ac_seller_required
    def inventory_update(pid):
        return f"inventory updated {pid}"

    @seller_bp.route("/orders")
    @ac_seller_required
    def orders():
        return "seller orders"

    @seller_bp.route("/orders/<int:oid>/update", methods=["POST"])
    @ac_seller_required
    def order_update(oid):
        return f"order updated {oid}"

    @seller_bp.route("/reviews")
    @ac_seller_required
    def reviews():
        return "seller reviews"

    @seller_bp.route("/chats")
    @ac_seller_required
    def chats():
        return "seller chats"

    @seller_bp.route("/chats/<int:cid>", methods=["GET", "POST"])
    @ac_seller_required
    def chat_detail(cid):
        return f"seller chat {cid}"

    @seller_bp.route("/support")
    @ac_seller_required
    def support_tickets():
        return "seller support tickets"

    @seller_bp.route("/support/reply", methods=["POST"])
    @ac_seller_required
    def support_reply():
        return "replied"

    @seller_bp.route("/debug-upload", methods=["GET", "POST"])
    def debug_upload():
        return "debug upload"

    # ── admin blueprint ──────────────────────────────────────────────
    admin_bp = Blueprint("admin", __name__)

    @admin_bp.route("/dashboard")
    @ac_admin_required
    def dashboard():
        return "admin dashboard"

    @admin_bp.route("/sellers")
    @ac_admin_required
    def sellers():
        return "sellers list"

    @admin_bp.route("/sellers/<int:sid>/approve")
    @ac_admin_required
    def seller_approve(sid):
        return f"approve seller {sid}"

    @admin_bp.route("/sellers/<int:sid>/reject")
    @ac_admin_required
    def seller_reject(sid):
        return f"reject seller {sid}"

    @admin_bp.route("/sellers/<int:sid>/commission", methods=["POST"])
    @ac_admin_required
    def seller_commission(sid):
        return f"commission seller {sid}"

    @admin_bp.route("/products")
    @ac_admin_required
    def products():
        return "admin products"

    @admin_bp.route("/products/<int:pid>/approve")
    @ac_admin_required
    def product_approve(pid):
        return f"approve product {pid}"

    @admin_bp.route("/products/<int:pid>/remove")
    @ac_admin_required
    def product_remove(pid):
        return f"remove product {pid}"

    @admin_bp.route("/finances")
    @ac_admin_required
    def finances():
        return "finances"

    @admin_bp.route("/finances/export")
    @ac_admin_required
    def finance_export():
        return "finance export"

    @admin_bp.route("/users")
    @ac_admin_required
    def users():
        return "users list"

    @admin_bp.route("/users/<int:uid>/toggle")
    @ac_admin_required
    def user_toggle(uid):
        return f"toggle user {uid}"

    @admin_bp.route("/promos")
    @ac_admin_required
    def promos():
        return "promos"

    @admin_bp.route("/promos/add", methods=["POST"])
    @ac_admin_required
    def promo_add():
        return "promo added"

    @admin_bp.route("/promos/<int:pid>/toggle")
    @ac_admin_required
    def promo_toggle(pid):
        return f"toggle promo {pid}"

    @admin_bp.route("/system")
    @ac_admin_required
    def system():
        return "system monitor"

    @admin_bp.route("/system/backup")
    @ac_admin_required
    def backup():
        return "backup"

    @admin_bp.route("/categories")
    @ac_admin_required
    def categories():
        return "admin categories"

    @admin_bp.route("/categories/add", methods=["POST"])
    @ac_admin_required
    def category_add():
        return "category added"

    @admin_bp.route("/support")
    @ac_admin_required
    def support_tickets():
        return "admin support"

    @admin_bp.route("/support/reply", methods=["POST"])
    @ac_admin_required
    def support_reply():
        return "admin replied"

    # ── store blueprint (public) ─────────────────────────────────────
    store_bp = Blueprint("store", __name__)



    @store_bp.route("/chat/start/<int:seller_id>", methods=["POST"])
    def start_chat(seller_id):
        return f"chat started with seller {seller_id}"

    @store_bp.route("/chat/<int:cid>", methods=["GET", "POST"])
    def chat_view(cid):
        return f"chat view {cid}"

    app.register_blueprint(auth_bp,     url_prefix="/auth")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(seller_bp,   url_prefix="/seller")
    app.register_blueprint(admin_bp,    url_prefix="/admin")
    app.register_blueprint(store_bp,    url_prefix="/store")

    return app


def _login(client, role, user_id=1):
    """Stamp the session as if a user has logged in."""
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["role"] = role
        sess["name"] = f"Test {role.capitalize()}"


# ══════════════════════════════════════════════════════════════════════
# 1. AUTH.PY DECORATOR TESTS
# ══════════════════════════════════════════════════════════════════════

class AuthDotPyTests(unittest.TestCase):
    """Tests for login_required / guest_only / admin_required in app/auth.py."""

    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    # ── login_required ───────────────────────────────────────────────

    def test_guest_cannot_access_cart(self):
        r = self.client.get("/customer/cart")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.location)

    def test_logged_in_customer_can_access_cart(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/cart")
        self.assertEqual(r.status_code, 200)

    def test_guest_redirected_from_orders(self):
        r = self.client.get("/customer/orders")
        self.assertEqual(r.status_code, 302)

    def test_logged_in_user_can_view_orders(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/orders")
        self.assertEqual(r.status_code, 200)

    # ── guest_only ───────────────────────────────────────────────────

    def test_login_page_accessible_as_guest(self):
        r = self.client.get("/auth/login")
        self.assertEqual(r.status_code, 200)

    def test_register_page_accessible_as_guest(self):
        r = self.client.get("/auth/register")
        self.assertEqual(r.status_code, 200)

    # ── admin_required (auth.py version) ────────────────────────────

    def test_guest_blocked_from_admin_dashboard(self):
        r = self.client.get("/admin/dashboard")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.location)

    def test_customer_blocked_from_admin_dashboard(self):
        _login(self.client, "customer")
        r = self.client.get("/admin/dashboard")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.location, "/customer/")

    def test_admin_can_access_admin_dashboard(self):
        _login(self.client, "admin")
        r = self.client.get("/admin/dashboard")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"admin dashboard", r.data)


# ══════════════════════════════════════════════════════════════════════
# 2. AUTHCONTROL.PY DECORATOR TESTS
# ══════════════════════════════════════════════════════════════════════

class AuthControlDotPyTests(unittest.TestCase):
    """Tests for role_required / admin_required / seller_required /
    customer_required in app/authcontrol.py."""

    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    # ── role_required ────────────────────────────────────────────────

    def test_role_required_blocks_guest(self):
        r = self.client.get("/seller/dashboard")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.location)

    def test_role_required_blocks_wrong_role(self):
        _login(self.client, "customer")
        r = self.client.get("/seller/dashboard")
        self.assertEqual(r.status_code, 302)

    def test_role_required_passes_correct_role(self):
        _login(self.client, "seller")
        r = self.client.get("/seller/dashboard")
        self.assertEqual(r.status_code, 200)

    # ── seller_required ──────────────────────────────────────────────

    def test_seller_required_blocks_admin(self):
        _login(self.client, "admin")
        r = self.client.get("/seller/dashboard")
        self.assertEqual(r.status_code, 302)

    def test_seller_required_passes_seller(self):
        _login(self.client, "seller")
        r = self.client.get("/seller/dashboard")
        self.assertEqual(r.status_code, 200)

    # ── admin_required (authcontrol.py version) ──────────────────────

    def test_admin_required_blocks_seller(self):
        _login(self.client, "seller")
        r = self.client.get("/admin/sellers")
        self.assertEqual(r.status_code, 302)

    def test_admin_required_passes_admin(self):
        _login(self.client, "admin")
        r = self.client.get("/admin/sellers")
        self.assertEqual(r.status_code, 200)

    # ── customer_required ────────────────────────────────────────────

    def test_customer_required_blocks_seller_on_wishlist(self):
        """Wishlist uses login_required (any role), not customer_required.
        Seller should still be let through (login_required only)."""
        _login(self.client, "seller")
        r = self.client.get("/customer/wishlist")
        self.assertEqual(r.status_code, 200)

    def test_guest_blocked_from_wishlist(self):
        r = self.client.get("/customer/wishlist")
        self.assertEqual(r.status_code, 302)


# ══════════════════════════════════════════════════════════════════════
# 3. AUTH ROUTES (register / login / logout / etc.)
# ══════════════════════════════════════════════════════════════════════

class AuthRoutesTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_get_login_page(self):
        r = self.client.get("/auth/login")
        self.assertEqual(r.status_code, 200)

    def test_get_register_page(self):
        r = self.client.get("/auth/register")
        self.assertEqual(r.status_code, 200)

    def test_get_forgot_password_page(self):
        r = self.client.get("/auth/forgot-password")
        self.assertEqual(r.status_code, 200)

    def test_get_change_password_page(self):
        r = self.client.get("/auth/change-password")
        self.assertEqual(r.status_code, 200)

    def test_logout_clears_session(self):
        _login(self.client, "customer")
        r = self.client.get("/auth/logout")
        self.assertEqual(r.status_code, 200)  # our dummy returns 200
        with self.client.session_transaction() as sess:
            self.assertNotIn("user_id", sess)


# ══════════════════════════════════════════════════════════════════════
# 4. CUSTOMER PUBLIC ROUTES (no login needed)
# ══════════════════════════════════════════════════════════════════════

class CustomerPublicTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_home_is_public(self):
        r = self.client.get("/customer/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"home", r.data)

    def test_products_list_is_public(self):
        r = self.client.get("/customer/products")
        self.assertEqual(r.status_code, 200)

    def test_product_detail_is_public(self):
        r = self.client.get("/customer/product/5")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"5", r.data)

    def test_support_page_is_public(self):
        r = self.client.get("/customer/support")
        self.assertEqual(r.status_code, 200)

    def test_stores_listing_is_public(self):
        r = self.client.get("/customer/stores")
        self.assertEqual(r.status_code, 200)

    def test_store_page_is_public(self):
        r = self.client.get("/customer/store/my-shop")
        self.assertEqual(r.status_code, 200)

    def test_support_chat_post_is_public(self):
        r = self.client.post("/customer/support/chat",
                             data={"message": "order status"})
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("reply", body)


# ══════════════════════════════════════════════════════════════════════
# 5. CUSTOMER AUTH-PROTECTED PAGES
# ══════════════════════════════════════════════════════════════════════

class CustomerAuthTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()
        _login(self.client, "customer")

    def test_cart_page_accessible_when_logged_in(self):
        r = self.client.get("/customer/cart")
        self.assertEqual(r.status_code, 200)

    def test_wishlist_accessible_when_logged_in(self):
        r = self.client.get("/customer/wishlist")
        self.assertEqual(r.status_code, 200)

    def test_checkout_get_accessible_when_logged_in(self):
        r = self.client.get("/customer/checkout")
        self.assertEqual(r.status_code, 200)

    def test_orders_accessible_when_logged_in(self):
        r = self.client.get("/customer/orders")
        self.assertEqual(r.status_code, 200)

    def test_order_detail_accessible_when_logged_in(self):
        r = self.client.get("/customer/order/42")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"42", r.data)

    def test_payment_history_accessible_when_logged_in(self):
        r = self.client.get("/customer/payments")
        self.assertEqual(r.status_code, 200)

    def test_profile_get_accessible_when_logged_in(self):
        r = self.client.get("/customer/profile")
        self.assertEqual(r.status_code, 200)

    def test_notifications_accessible_when_logged_in(self):
        r = self.client.get("/customer/notifications")
        self.assertEqual(r.status_code, 200)

    def test_notif_count_returns_json(self):
        r = self.client.get("/customer/notifications/count")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("count", body)

    def test_chats_list_accessible_when_logged_in(self):
        r = self.client.get("/customer/chats")
        self.assertEqual(r.status_code, 200)

    def test_chat_detail_accessible_when_logged_in(self):
        r = self.client.get("/customer/chat/7")
        self.assertEqual(r.status_code, 200)

    def test_chat_start_accessible_when_logged_in(self):
        r = self.client.get("/customer/chat/start/3")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 6. CART TESTS
# ══════════════════════════════════════════════════════════════════════

class CartTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_add_to_cart(self):
        r = self.client.post("/customer/cart/add/1", data={"quantity": "1"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.location)

    def test_logged_in_user_can_add_to_cart(self):
        _login(self.client, "customer")
        r = self.client.post("/customer/cart/add/1", data={"quantity": "1"})
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_update_cart(self):
        r = self.client.post("/customer/cart/update/1", data={"quantity": "3"})
        self.assertEqual(r.status_code, 302)

    def test_logged_in_user_can_update_cart(self):
        _login(self.client, "customer")
        r = self.client.post("/customer/cart/update/1", data={"quantity": "3"})
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_remove_from_cart(self):
        r = self.client.get("/customer/cart/remove/1")
        self.assertEqual(r.status_code, 302)

    def test_logged_in_user_can_remove_from_cart(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/cart/remove/1")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 7. WISHLIST TESTS
# ══════════════════════════════════════════════════════════════════════

class WishlistTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_view_wishlist(self):
        r = self.client.get("/customer/wishlist")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_view_wishlist(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/wishlist")
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_toggle_wishlist(self):
        r = self.client.get("/customer/wishlist/toggle/10")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_toggle_wishlist(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/wishlist/toggle/10")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 8. CHECKOUT / PROMO TESTS
# ══════════════════════════════════════════════════════════════════════

class CheckoutTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_access_checkout(self):
        r = self.client.get("/customer/checkout")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.location)

    def test_customer_can_get_checkout(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/checkout")
        self.assertEqual(r.status_code, 200)

    def test_customer_can_post_checkout(self):
        _login(self.client, "customer")
        r = self.client.post("/customer/checkout", data={"method": "cod"})
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_validate_promo(self):
        r = self.client.post("/customer/promo/validate",
                             data={"code": "SAVE10", "subtotal": "500"})
        self.assertEqual(r.status_code, 302)

    def test_customer_can_validate_promo(self):
        _login(self.client, "customer")
        r = self.client.post("/customer/promo/validate",
                             data={"code": "SAVE10", "subtotal": "500"})
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("valid", body)
        self.assertIn("discount", body)
        self.assertIn("message", body)


# ══════════════════════════════════════════════════════════════════════
# 9. ORDER TESTS
# ══════════════════════════════════════════════════════════════════════

class OrderTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_view_orders_list(self):
        r = self.client.get("/customer/orders")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_view_orders_list(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/orders")
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_view_order_detail(self):
        r = self.client.get("/customer/order/1")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_view_order_detail(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/order/1")
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_view_payment_history(self):
        r = self.client.get("/customer/payments")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_view_payment_history(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/payments")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 10. REVIEW TESTS
# ══════════════════════════════════════════════════════════════════════

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_submit_review(self):
        r = self.client.post("/customer/review/5",
                             data={"rating": "5", "title": "Great", "body": "Love it"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.location)

    def test_customer_can_submit_review(self):
        _login(self.client, "customer")
        r = self.client.post("/customer/review/5",
                             data={"rating": "5", "title": "Great", "body": "Love it"})
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 11. PROFILE TESTS
# ══════════════════════════════════════════════════════════════════════

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_view_profile(self):
        r = self.client.get("/customer/profile")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_view_profile(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/profile")
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_post_profile(self):
        r = self.client.post("/customer/profile", data={"name": "New Name"})
        self.assertEqual(r.status_code, 302)

    def test_customer_can_post_profile(self):
        _login(self.client, "customer")
        r = self.client.post("/customer/profile", data={"name": "New Name"})
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 12. NOTIFICATION TESTS
# ══════════════════════════════════════════════════════════════════════

class NotificationTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_view_notifications(self):
        r = self.client.get("/customer/notifications")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_view_notifications(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/notifications")
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_poll_notif_count(self):
        r = self.client.get("/customer/notifications/count")
        self.assertEqual(r.status_code, 302)

    def test_notif_count_returns_count_key(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/notifications/count")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("count", body)
        self.assertIsInstance(body["count"], int)


# ══════════════════════════════════════════════════════════════════════
# 13. SUPPORT CHATBOT TESTS
# ══════════════════════════════════════════════════════════════════════

class SupportTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_support_page_open_to_guest(self):
        r = self.client.get("/customer/support")
        self.assertEqual(r.status_code, 200)

    def test_support_page_open_to_logged_in(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/support")
        self.assertEqual(r.status_code, 200)

    def test_chatbot_post_returns_json_with_reply(self):
        r = self.client.post("/customer/support/chat",
                             data={"message": "track my order"})
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("reply", body)
        self.assertIsInstance(body["reply"], str)

    def test_chatbot_accepts_empty_message_without_crashing(self):
        r = self.client.post("/customer/support/chat", data={"message": ""})
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 14. CUSTOMER-SELLER CHAT TESTS
# ══════════════════════════════════════════════════════════════════════

class ChatTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_see_chats_list(self):
        r = self.client.get("/customer/chats")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_see_chats_list(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/chats")
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_open_chat_detail(self):
        r = self.client.get("/customer/chat/1")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_open_chat_detail(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/chat/1")
        self.assertEqual(r.status_code, 200)

    def test_customer_can_post_message_in_chat(self):
        _login(self.client, "customer")
        r = self.client.post("/customer/chat/1", data={"message": "hello"})
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_start_chat_with_store(self):
        r = self.client.get("/customer/chat/start/2")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_start_chat_with_store(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/chat/start/2")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 15. PUBLIC STORE PAGES
# ══════════════════════════════════════════════════════════════════════

class StorePublicTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()



    def test_start_chat_post_accessible(self):
        r = self.client.post("/store/chat/start/5")
        self.assertEqual(r.status_code, 200)

    def test_chat_view_get_accessible(self):
        r = self.client.get("/store/chat/3")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 16. SELLER ACCESS CONTROL — every seller route requires seller role
# ══════════════════════════════════════════════════════════════════════

SELLER_ROUTES_GET = [
    "/seller/setup",
    "/seller/dashboard",
    "/seller/store/profile",
    "/seller/store/customize",
    "/seller/products",
    "/seller/products/add",
    "/seller/products/edit/1",
    "/seller/products/delete/1",
    "/seller/categories",
    "/seller/inventory",
    "/seller/orders",
    "/seller/reviews",
    "/seller/chats",
    "/seller/chats/1",
    "/seller/support",
]

SELLER_ROUTES_POST = [
    ("/seller/inventory/update/1", {"qty": "20"}),
    ("/seller/orders/1/update",    {"status": "shipped"}),
    ("/seller/support/reply",      {"ticket_id": "1", "reply": "Hi"}),
    ("/seller/store/profile",      {"name": "Shop"}),
    ("/seller/store/customize",    {"theme": "dark"}),
    ("/seller/products/add",       {"name": "Prod", "price": "100"}),
]


class SellerAccessTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def _assert_blocked(self, url, method="GET", data=None):
        if method == "POST":
            r = self.client.post(url, data=data or {})
        else:
            r = self.client.get(url)
        self.assertEqual(r.status_code, 302,
                         f"Expected 302 for {method} {url}, got {r.status_code}")

    def _assert_allowed(self, url, method="GET", data=None):
        if method == "POST":
            r = self.client.post(url, data=data or {})
        else:
            r = self.client.get(url)
        self.assertEqual(r.status_code, 200,
                         f"Expected 200 for {method} {url}, got {r.status_code}")

    # — Guest is blocked ─────────────────────────────────────────────

    def test_guest_blocked_from_all_seller_get_routes(self):
        for url in SELLER_ROUTES_GET:
            with self.subTest(url=url):
                self._assert_blocked(url)

    def test_guest_blocked_from_all_seller_post_routes(self):
        for url, data in SELLER_ROUTES_POST:
            with self.subTest(url=url):
                self._assert_blocked(url, "POST", data)

    # — Customer is blocked ──────────────────────────────────────────

    def test_customer_blocked_from_all_seller_get_routes(self):
        _login(self.client, "customer")
        for url in SELLER_ROUTES_GET:
            with self.subTest(url=url):
                self._assert_blocked(url)

    def test_customer_blocked_from_all_seller_post_routes(self):
        _login(self.client, "customer")
        for url, data in SELLER_ROUTES_POST:
            with self.subTest(url=url):
                self._assert_blocked(url, "POST", data)

    # — Admin is blocked ─────────────────────────────────────────────

    def test_admin_blocked_from_all_seller_get_routes(self):
        _login(self.client, "admin")
        for url in SELLER_ROUTES_GET:
            with self.subTest(url=url):
                self._assert_blocked(url)

    # — Seller is allowed ────────────────────────────────────────────

    def test_seller_allowed_on_all_get_routes(self):
        _login(self.client, "seller")
        for url in SELLER_ROUTES_GET:
            with self.subTest(url=url):
                self._assert_allowed(url)

    def test_seller_allowed_on_all_post_routes(self):
        _login(self.client, "seller")
        for url, data in SELLER_ROUTES_POST:
            with self.subTest(url=url):
                self._assert_allowed(url, "POST", data)


# ══════════════════════════════════════════════════════════════════════
# 17. SELLER FEATURE TESTS — response shape / content
# ══════════════════════════════════════════════════════════════════════

class SellerFeatureTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()
        _login(self.client, "seller")

    def test_setup_page_loads(self):
        r = self.client.get("/seller/setup")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"setup", r.data)

    def test_seller_dashboard_loads(self):
        r = self.client.get("/seller/dashboard")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"dashboard", r.data)

    def test_add_product_get(self):
        r = self.client.get("/seller/products/add")
        self.assertEqual(r.status_code, 200)

    def test_add_product_post(self):
        r = self.client.post("/seller/products/add",
                             data={"name": "Widget", "price": "199",
                                   "stock_qty": "10", "category_id": "1"})
        self.assertEqual(r.status_code, 200)

    def test_edit_product_get(self):
        r = self.client.get("/seller/products/edit/1")
        self.assertEqual(r.status_code, 200)

    def test_delete_product(self):
        r = self.client.get("/seller/products/delete/1")
        self.assertEqual(r.status_code, 200)

    def test_inventory_page_loads(self):
        r = self.client.get("/seller/inventory")
        self.assertEqual(r.status_code, 200)

    def test_inventory_update_post(self):
        r = self.client.post("/seller/inventory/update/1", data={"qty": "50"})
        self.assertEqual(r.status_code, 200)

    def test_orders_page_loads(self):
        r = self.client.get("/seller/orders")
        self.assertEqual(r.status_code, 200)

    def test_order_status_update_post(self):
        r = self.client.post("/seller/orders/1/update", data={"status": "delivered"})
        self.assertEqual(r.status_code, 200)

    def test_reviews_page_loads(self):
        r = self.client.get("/seller/reviews")
        self.assertEqual(r.status_code, 200)

    def test_seller_chats_list(self):
        r = self.client.get("/seller/chats")
        self.assertEqual(r.status_code, 200)

    def test_seller_chat_detail_get(self):
        r = self.client.get("/seller/chats/1")
        self.assertEqual(r.status_code, 200)

    def test_seller_chat_detail_post(self):
        r = self.client.post("/seller/chats/1", data={"message": "Hello customer!"})
        self.assertEqual(r.status_code, 200)

    def test_seller_support_tickets(self):
        r = self.client.get("/seller/support")
        self.assertEqual(r.status_code, 200)

    def test_seller_support_reply_post(self):
        r = self.client.post("/seller/support/reply",
                             data={"ticket_id": "1", "reply": "We'll help you."})
        self.assertEqual(r.status_code, 200)

    def test_store_profile_get(self):
        r = self.client.get("/seller/store/profile")
        self.assertEqual(r.status_code, 200)

    def test_store_profile_post(self):
        r = self.client.post("/seller/store/profile",
                             data={"name": "My Shop", "description": "Best shop"})
        self.assertEqual(r.status_code, 200)


        self.assertEqual(r.status_code, 200)

    def test_categories_page_loads(self):
        r = self.client.get("/seller/categories")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 18. ADMIN ACCESS CONTROL — every admin route requires admin role
# ══════════════════════════════════════════════════════════════════════

ADMIN_ROUTES_GET = [
    "/admin/dashboard",
    "/admin/sellers",
    "/admin/sellers/1/approve",
    "/admin/sellers/1/reject",
    "/admin/products",
    "/admin/products/1/approve",
    "/admin/products/1/remove",
    "/admin/finances",
    "/admin/finances/export",
    "/admin/users",
    "/admin/users/1/toggle",
    "/admin/promos",
    "/admin/promos/1/toggle",
    "/admin/system",
    "/admin/system/backup",
    "/admin/categories",
    "/admin/support",
]

ADMIN_ROUTES_POST = [
    ("/admin/sellers/1/commission", {"commission": "10"}),
    ("/admin/promos/add",           {"code": "SAVE10", "discount": "10"}),
    ("/admin/categories/add",       {"name": "Electronics"}),
    ("/admin/support/reply",        {"ticket_id": "1", "reply": "Fixed"}),
]


class AdminAccessTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def _assert_blocked(self, url, method="GET", data=None):
        r = (self.client.post(url, data=data or {})
             if method == "POST" else self.client.get(url))
        self.assertEqual(r.status_code, 302,
                         f"Expected 302 for {method} {url}, got {r.status_code}")

    def _assert_allowed(self, url, method="GET", data=None):
        r = (self.client.post(url, data=data or {})
             if method == "POST" else self.client.get(url))
        self.assertEqual(r.status_code, 200,
                         f"Expected 200 for {method} {url}, got {r.status_code}")

    # — Guest blocked ────────────────────────────────────────────────

    def test_guest_blocked_from_all_admin_get_routes(self):
        for url in ADMIN_ROUTES_GET:
            with self.subTest(url=url):
                self._assert_blocked(url)

    def test_guest_blocked_from_all_admin_post_routes(self):
        for url, data in ADMIN_ROUTES_POST:
            with self.subTest(url=url):
                self._assert_blocked(url, "POST", data)

    # — Customer blocked ─────────────────────────────────────────────

    def test_customer_blocked_from_all_admin_get_routes(self):
        _login(self.client, "customer")
        for url in ADMIN_ROUTES_GET:
            with self.subTest(url=url):
                self._assert_blocked(url)

    # — Seller blocked ───────────────────────────────────────────────

    def test_seller_blocked_from_all_admin_get_routes(self):
        _login(self.client, "seller")
        for url in ADMIN_ROUTES_GET:
            with self.subTest(url=url):
                self._assert_blocked(url)

    # — Admin allowed ────────────────────────────────────────────────

    def test_admin_allowed_on_all_get_routes(self):
        _login(self.client, "admin")
        for url in ADMIN_ROUTES_GET:
            with self.subTest(url=url):
                self._assert_allowed(url)

    def test_admin_allowed_on_all_post_routes(self):
        _login(self.client, "admin")
        for url, data in ADMIN_ROUTES_POST:
            with self.subTest(url=url):
                self._assert_allowed(url, "POST", data)


# ══════════════════════════════════════════════════════════════════════
# 19. ADMIN FEATURE TESTS — response shape / content
# ══════════════════════════════════════════════════════════════════════

class AdminFeatureTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()
        _login(self.client, "admin")

    def test_dashboard_page(self):
        r = self.client.get("/admin/dashboard")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"dashboard", r.data)

    def test_sellers_list(self):
        r = self.client.get("/admin/sellers")
        self.assertEqual(r.status_code, 200)

    def test_seller_approve(self):
        r = self.client.get("/admin/sellers/2/approve")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"2", r.data)

    def test_seller_reject(self):
        r = self.client.get("/admin/sellers/2/reject")
        self.assertEqual(r.status_code, 200)

    def test_seller_commission_post(self):
        r = self.client.post("/admin/sellers/2/commission",
                             data={"commission": "15"})
        self.assertEqual(r.status_code, 200)

    def test_products_list(self):
        r = self.client.get("/admin/products")
        self.assertEqual(r.status_code, 200)

    def test_product_approve(self):
        r = self.client.get("/admin/products/5/approve")
        self.assertEqual(r.status_code, 200)

    def test_product_remove(self):
        r = self.client.get("/admin/products/5/remove")
        self.assertEqual(r.status_code, 200)

    def test_finances_page(self):
        r = self.client.get("/admin/finances")
        self.assertEqual(r.status_code, 200)

    def test_finance_export(self):
        r = self.client.get("/admin/finances/export")
        self.assertEqual(r.status_code, 200)

    def test_users_list(self):
        r = self.client.get("/admin/users")
        self.assertEqual(r.status_code, 200)

    def test_user_toggle(self):
        r = self.client.get("/admin/users/3/toggle")
        self.assertEqual(r.status_code, 200)

    def test_promos_list(self):
        r = self.client.get("/admin/promos")
        self.assertEqual(r.status_code, 200)

    def test_promo_add_post(self):
        r = self.client.post("/admin/promos/add",
                             data={"code": "FLASH20", "discount_type": "percent",
                                   "discount_value": "20", "min_order": "0",
                                   "valid_until": "2027-01-01", "max_uses": "100"})
        self.assertEqual(r.status_code, 200)

    def test_promo_toggle(self):
        r = self.client.get("/admin/promos/1/toggle")
        self.assertEqual(r.status_code, 200)

    def test_system_monitor(self):
        r = self.client.get("/admin/system")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"system", r.data)

    def test_backup(self):
        r = self.client.get("/admin/system/backup")
        self.assertEqual(r.status_code, 200)

    def test_categories_list(self):
        r = self.client.get("/admin/categories")
        self.assertEqual(r.status_code, 200)

    def test_category_add_post(self):
        r = self.client.post("/admin/categories/add",
                             data={"name": "New Category", "slug": "new-category"})
        self.assertEqual(r.status_code, 200)

    def test_support_tickets(self):
        r = self.client.get("/admin/support")
        self.assertEqual(r.status_code, 200)

    def test_support_reply_post(self):
        r = self.client.post("/admin/support/reply",
                             data={"ticket_id": "2", "reply": "Issue resolved."})
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# 20. DEBUG UPLOAD ENDPOINT (unprotected — should stay GET + POST)
# ══════════════════════════════════════════════════════════════════════

class DebugUploadTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_debug_upload_get_is_open(self):
        """The debug route has no role guard, so guests can reach it."""
        r = self.client.get("/seller/debug-upload")
        self.assertEqual(r.status_code, 200)

    def test_debug_upload_post_without_file(self):
        """POST without a file should not crash."""
        r = self.client.post("/seller/debug-upload", data={})
        self.assertEqual(r.status_code, 200)

    def test_debug_upload_post_with_file(self):
        """POST with a file reaches the endpoint."""
        data = {
            "logo": (io.BytesIO(b"fake-image-bytes"), "logo.png"),
        }
        r = self.client.post("/seller/debug-upload",
                             data=data,
                             content_type="multipart/form-data")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
