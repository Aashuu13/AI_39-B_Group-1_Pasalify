"""
test/flask_test.py — Yubraj's features only
Sprint 1: change/reset password
Sprint 2: view product
Sprint 3: edit customer UI (profile), seller chat
Sprint 4: organize product (seller products/categories/inventory)
Sprint 5: store URL

Run with: python -m pytest test/flask_test.py -v
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, url_for, jsonify

from app.auth import login_required, guest_only, admin_required
from app.authcontrol import (
    role_required,
    admin_required  as ac_admin_required,
    seller_required as ac_seller_required,
)


def _make_minimal_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.config["TESTING"] = True

    # ── auth blueprint ───────────────────────────────────────────────
    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/login")
    def login(): return "login page"

    @auth_bp.route("/register")
    def register(): return "register page"

    @auth_bp.route("/logout")
    def logout():
        session.clear()
        return "logged out"

    @auth_bp.route("/forgot-password")
    def forgot_password(): return "forgot password page"

    @auth_bp.route("/change-password")
    def change_password(): return "change password page"

    # ── customer blueprint ───────────────────────────────────────────
    customer_bp = Blueprint("customer", __name__)

    @customer_bp.route("/")
    def home(): return "customer home"

    @customer_bp.route("/products")
    def products(): return "products list"

    @customer_bp.route("/product/<int:pid>")
    def product_detail(pid): return f"product {pid}"

    @customer_bp.route("/stores")
    def stores(): return "stores list"

    @customer_bp.route("/store/<slug>")
    def store_page(slug): return f"store {slug}"

    @customer_bp.route("/support")
    def support(): return "support page"

    @customer_bp.route("/support/chat", methods=["POST"])
    def support_chat(): return jsonify({"reply": "bot response"})

    @customer_bp.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile(): return "profile page"

    @customer_bp.route("/notifications")
    @login_required
    def notifications(): return "notifications"

    @customer_bp.route("/notifications/count")
    @login_required
    def notif_count(): return jsonify({"count": 0})

    @customer_bp.route("/chats")
    @login_required
    def chats(): return "chats list"

    @customer_bp.route("/chat/<int:cid>", methods=["GET", "POST"])
    @login_required
    def chat_detail(cid): return f"chat {cid}"

    @customer_bp.route("/chat/start/<int:store_id>")
    @login_required
    def chat_start(store_id): return f"chat started with store {store_id}"

    # stubs
    @customer_bp.route("/cart")
    @login_required
    def cart(): return "cart"

    @customer_bp.route("/orders")
    @login_required
    def orders(): return "orders"

    @customer_bp.route("/order/<int:oid>")
    @login_required
    def order_detail(oid): return f"order {oid}"

    @customer_bp.route("/wishlist")
    @login_required
    def wishlist(): return "wishlist"

    
    seller_bp = Blueprint("seller", __name__)

    @seller_bp.route("/setup", methods=["GET", "POST"])
    @ac_seller_required
    def setup(): return "setup page"

    @seller_bp.route("/dashboard")
    @ac_seller_required
    def dashboard(): return "seller dashboard"

    @seller_bp.route("/store/profile", methods=["GET", "POST"])
    @ac_seller_required
    def store_profile(): return "store profile"

    @seller_bp.route("/store/customize", methods=["GET", "POST"])
    @ac_seller_required
    def store_customize(): return "store customize"

    @seller_bp.route("/products")
    @ac_seller_required
    def products(): return "seller products"

    @seller_bp.route("/products/add", methods=["GET", "POST"])
    @ac_seller_required
    def product_add(): return "add product"

    @seller_bp.route("/products/edit/<int:pid>", methods=["GET", "POST"])
    @ac_seller_required
    def product_edit(pid): return f"edit product {pid}"

    @seller_bp.route("/products/delete/<int:pid>")
    @ac_seller_required
    def product_delete(pid): return f"delete product {pid}"

    @seller_bp.route("/categories")
    @ac_seller_required
    def categories(): return "seller categories"

    @seller_bp.route("/inventory")
    @ac_seller_required
    def inventory(): return "inventory"

    @seller_bp.route("/inventory/update/<int:pid>", methods=["POST"])
    @ac_seller_required
    def inventory_update(pid): return f"inventory updated {pid}"

    @seller_bp.route("/orders")
    @ac_seller_required
    def orders(): return "seller orders"

    @seller_bp.route("/orders/<int:oid>/update", methods=["POST"])
    @ac_seller_required
    def order_update(oid): return f"order updated {oid}"

    @seller_bp.route("/reviews")
    @ac_seller_required
    def reviews(): return "seller reviews"

    @seller_bp.route("/chats")
    @ac_seller_required
    def chats(): return "seller chats"

    @seller_bp.route("/chats/<int:cid>", methods=["GET", "POST"])
    @ac_seller_required
    def chat_detail(cid): return f"seller chat {cid}"

    @seller_bp.route("/support")
    @ac_seller_required
    def support_tickets(): return "seller support tickets"

    @seller_bp.route("/support/reply", methods=["POST"])
    @ac_seller_required
    def support_reply(): return "replied"

    @seller_bp.route("/debug-upload", methods=["GET", "POST"])
    def debug_upload(): return "debug upload"

    # ── admin blueprint ──────────────────────────────────────────────
    admin_bp = Blueprint("admin", __name__)

    @admin_bp.route("/dashboard")
    @ac_admin_required
    def dashboard(): return "admin dashboard"

    # ── store blueprint ──────────────────────────────────────────────
    store_bp = Blueprint("store", __name__)

    @store_bp.route("/<slug>")
    def public_store(slug): return f"public store {slug}"

    @store_bp.route("/<slug>/product/<int:pid>")
    def store_product(slug, pid): return f"store product {slug}/{pid}"

    @store_bp.route("/chat/start/<int:seller_id>", methods=["POST"])
    def start_chat(seller_id): return f"chat started with seller {seller_id}"

    @store_bp.route("/chat/<int:cid>", methods=["GET", "POST"])
    def chat_view(cid): return f"chat view {cid}"

    app.register_blueprint(auth_bp,     url_prefix="/auth")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(seller_bp,   url_prefix="/seller")
    app.register_blueprint(admin_bp,    url_prefix="/admin")
    app.register_blueprint(store_bp,    url_prefix="/store")

    return app


def _login(client, role, user_id=1):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["role"] = role
        sess["name"] = f"Test {role.capitalize()}"


# ══════════════════════════════════════════════════════════════════════
# SPRINT 1: CHANGE / RESET PASSWORD
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
        self.assertEqual(r.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertNotIn("user_id", sess)


# ══════════════════════════════════════════════════════════════════════
# SPRINT 1: AUTH DECORATORS
# ══════════════════════════════════════════════════════════════════════

class AuthDecoratorTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_blocked_from_profile(self):
        r = self.client.get("/customer/profile")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.location)

    def test_logged_in_customer_can_access_profile(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/profile")
        self.assertEqual(r.status_code, 200)

    def test_guest_blocked_from_admin(self):
        r = self.client.get("/admin/dashboard")
        self.assertEqual(r.status_code, 302)

    def test_admin_can_access_admin(self):
        _login(self.client, "admin")
        r = self.client.get("/admin/dashboard")
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# SPRINT 2: VIEW PRODUCT — public routes
# ══════════════════════════════════════════════════════════════════════

class ViewProductTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_home_is_public(self):
        r = self.client.get("/customer/")
        self.assertEqual(r.status_code, 200)

    def test_products_list_is_public(self):
        r = self.client.get("/customer/products")
        self.assertEqual(r.status_code, 200)

    def test_product_detail_is_public(self):
        r = self.client.get("/customer/product/5")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"5", r.data)


# ══════════════════════════════════════════════════════════════════════
# SPRINT 3: EDIT CUSTOMER UI — profile
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

    def test_customer_can_post_profile(self):
        _login(self.client, "customer")
        r = self.client.post("/customer/profile", data={"name": "New Name"})
        self.assertEqual(r.status_code, 200)

    def test_guest_cannot_post_profile(self):
        r = self.client.post("/customer/profile", data={"name": "New Name"})
        self.assertEqual(r.status_code, 302)


# ══════════════════════════════════════════════════════════════════════
# SPRINT 3: SELLER CHAT
# ══════════════════════════════════════════════════════════════════════

class SellerChatTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_cannot_see_customer_chats(self):
        r = self.client.get("/customer/chats")
        self.assertEqual(r.status_code, 302)

    def test_customer_can_see_chats_list(self):
        _login(self.client, "customer")
        r = self.client.get("/customer/chats")
        self.assertEqual(r.status_code, 200)

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

    def test_guest_cannot_access_seller_chats(self):
        r = self.client.get("/seller/chats")
        self.assertEqual(r.status_code, 302)

    def test_seller_can_access_chats(self):
        _login(self.client, "seller")
        r = self.client.get("/seller/chats")
        self.assertEqual(r.status_code, 200)

    def test_seller_can_view_chat_detail(self):
        _login(self.client, "seller")
        r = self.client.get("/seller/chats/1")
        self.assertEqual(r.status_code, 200)

    def test_seller_can_post_message(self):
        _login(self.client, "seller")
        r = self.client.post("/seller/chats/1", data={"message": "Hello customer!"})
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# SPRINT 4: ORGANIZE PRODUCT — seller products/categories/inventory
# ══════════════════════════════════════════════════════════════════════

SELLER_PRODUCT_ROUTES_GET = [
    "/seller/products",
    "/seller/products/add",
    "/seller/products/edit/1",
    "/seller/products/delete/1",
    "/seller/categories",
    "/seller/inventory",
]

SELLER_PRODUCT_ROUTES_POST = [
    ("/seller/products/add",        {"name": "Prod", "price": "100"}),
    ("/seller/inventory/update/1",  {"stock_qty": "20"}),
]


class OrganizeProductAccessTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_guest_blocked_from_seller_product_routes(self):
        for url in SELLER_PRODUCT_ROUTES_GET:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 302)

    def test_customer_blocked_from_seller_product_routes(self):
        _login(self.client, "customer")
        for url in SELLER_PRODUCT_ROUTES_GET:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 302)

    def test_seller_can_access_product_routes(self):
        _login(self.client, "seller")
        for url in SELLER_PRODUCT_ROUTES_GET:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200)

    def test_seller_can_post_product_routes(self):
        _login(self.client, "seller")
        for url, data in SELLER_PRODUCT_ROUTES_POST:
            with self.subTest(url=url):
                r = self.client.post(url, data=data)
                self.assertEqual(r.status_code, 200)


class OrganizeProductFeatureTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()
        _login(self.client, "seller")

    def test_products_page_loads(self):
        r = self.client.get("/seller/products")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"products", r.data)

    def test_add_product_get(self):
        r = self.client.get("/seller/products/add")
        self.assertEqual(r.status_code, 200)

    def test_add_product_post(self):
        r = self.client.post("/seller/products/add",
                             data={"name": "Widget", "price": "199", "stock_qty": "10"})
        self.assertEqual(r.status_code, 200)

    def test_edit_product_get(self):
        r = self.client.get("/seller/products/edit/1")
        self.assertEqual(r.status_code, 200)

    def test_delete_product(self):
        r = self.client.get("/seller/products/delete/1")
        self.assertEqual(r.status_code, 200)

    def test_categories_page_loads(self):
        r = self.client.get("/seller/categories")
        self.assertEqual(r.status_code, 200)

    def test_inventory_page_loads(self):
        r = self.client.get("/seller/inventory")
        self.assertEqual(r.status_code, 200)

    def test_inventory_update_post(self):
        r = self.client.post("/seller/inventory/update/1", data={"stock_qty": "50"})
        self.assertEqual(r.status_code, 200)


# ══════════════════════════════════════════════════════════════════════
# SPRINT 5: STORE URL — public store pages
# ══════════════════════════════════════════════════════════════════════

class StoreUrlTests(unittest.TestCase):
    def setUp(self):
        self.app = _make_minimal_app()
        self.client = self.app.test_client()

    def test_stores_listing_is_public(self):
        r = self.client.get("/customer/stores")
        self.assertEqual(r.status_code, 200)

    def test_store_page_is_public(self):
        r = self.client.get("/customer/store/my-shop")
        self.assertEqual(r.status_code, 200)

    def test_public_store_page_via_store_blueprint(self):
        r = self.client.get("/store/cool-shop")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"cool-shop", r.data)

    def test_store_product_page_accessible_to_guest(self):
        r = self.client.get("/store/cool-shop/product/99")
        self.assertEqual(r.status_code, 200)

    def test_start_chat_from_store_post(self):
        r = self.client.post("/store/chat/start/5")
        self.assertEqual(r.status_code, 200)

    def test_chat_view_from_store(self):
        r = self.client.get("/store/chat/3")
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
