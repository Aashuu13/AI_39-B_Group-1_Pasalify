import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint, session, get_flashed_messages

from app.controllers.admin_controller import AdminController

<<<<<<< HEAD
=======

# A reusable helper that builds a tiny Flask app for every test.
# define the route names the controller redirects to
# (admin.sellers, admin.products, admin.users, admin.promos,
# admin.system, admin.categories, admin.support_tickets) so that
# url_for() inside the controller can build URLs successfully.
>>>>>>> origin/aayushma
def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    admin_bp = Blueprint("admin", __name__)
    admin_bp.route("/sellers", endpoint="sellers")(lambda: "sellers")
    admin_bp.route("/products", endpoint="products")(lambda: "products")
    admin_bp.route("/users", endpoint="users")(lambda: "users")
    admin_bp.route("/promos", endpoint="promos")(lambda: "promos")
    admin_bp.route("/system", endpoint="system")(lambda: "system")
    admin_bp.route("/categories", endpoint="categories")(lambda: "categories")
    admin_bp.route("/support", endpoint="support_tickets")(lambda: "support")
    app.register_blueprint(admin_bp)

    return app

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
def make_controller():
    """
    Build an AdminController whose DB-touching helpers (_q/_run/_log/
    _notify) are replaced with mocks, so tests exercise the
    controller's own logic instead of hitting a real database.
    """
    controller = AdminController()
    controller._q = MagicMock(return_value=[])
    controller._run = MagicMock(return_value=1)
    controller._log = MagicMock()
    controller._notify = MagicMock()
    return controller

<<<<<<< HEAD
=======

# =====================================================================
#  DASHBOARD
# =====================================================================
>>>>>>> origin/aayushma
class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.admin_controller.render_template")
    @patch("app.controllers.admin_controller.StoreModel")
    @patch("app.controllers.admin_controller.ProductModel")
    @patch("app.controllers.admin_controller.UserModel")
    def test_dashboard_gathers_stats_and_renders(
        self, mock_user_model, mock_product_model, mock_store_model, mock_render
    ):
        mock_render.return_value = "dashboard_page"
<<<<<<< HEAD
        mock_user_model.count.side_effect = [10, 3]   
        mock_store_model.count.return_value = 2
        mock_product_model.count.return_value = 4

=======
        mock_user_model.count.side_effect = [10, 3]   # customers, sellers
        mock_store_model.count.return_value = 2
        mock_product_model.count.return_value = 4
        # _q called for: total_orders, total_revenue, recent_orders, monthly, logs
>>>>>>> origin/aayushma
        self.controller._q.side_effect = [
            {"c": 50}, {"t": 1234.5}, [{"id": 1}], [{"month": "2026-05"}], [{"id": 1}]
        ]

        with self.app.test_request_context():
            result = self.controller.dashboard()
            self.assertEqual(result, "dashboard_page")
            mock_render.assert_called_once()
            _, kwargs = mock_render.call_args
            self.assertEqual(kwargs["total_users"], 10)
            self.assertEqual(kwargs["total_sellers"], 3)
            self.assertEqual(kwargs["total_orders"], 50)
            self.assertEqual(kwargs["total_revenue"], 1234.5)
            self.assertEqual(kwargs["pending_stores"], 2)
            self.assertEqual(kwargs["pending_prods"], 4)
            self.assertEqual(kwargs["recent_orders"], [{"id": 1}])
            self.assertEqual(kwargs["monthly"], [{"month": "2026-05"}])
            self.assertEqual(kwargs["logs"], [{"id": 1}])

<<<<<<< HEAD
=======

# =====================================================================
#  SELLER MODERATION
# =====================================================================
>>>>>>> origin/aayushma
class TestSellerModeration(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.admin_controller.render_template")
    @patch("app.controllers.admin_controller.StoreModel")
    def test_sellers_lists_stores_with_owner(self, mock_store_model, mock_render):
        mock_render.return_value = "sellers_page"
        mock_store_model.all_with_owner.return_value = [{"id": 1, "owner_name": "Sam"}]
        with self.app.test_request_context():
            result = self.controller.sellers()
            self.assertEqual(result, "sellers_page")
            mock_render.assert_called_once_with(
                "admin/sellers.html", sellers=[{"id": 1, "owner_name": "Sam"}]
            )

    @patch("app.controllers.admin_controller.StoreModel")
    def test_seller_approve_notifies_owner_and_redirects(self, mock_store_model):
        mock_store_model.find_by_id.return_value = {"id": 1, "user_id": 9, "name": "Cool Shop"}
        with self.app.test_request_context():
            response = self.controller.seller_approve(1)
            mock_store_model.approve.assert_called_once_with(1)
            self.controller._notify.assert_called_once()
            self.assertEqual(self.controller._notify.call_args[0][0], 9)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/sellers"))
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Seller approved."), flashes)

    @patch("app.controllers.admin_controller.StoreModel")
    def test_seller_reject_warns_and_redirects(self, mock_store_model):
        with self.app.test_request_context():
            response = self.controller.seller_reject(1)
            mock_store_model.reject.assert_called_once_with(1)
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("warning", "Seller rejected."), flashes)

    @patch("app.controllers.admin_controller.StoreModel")
    def test_seller_commission_updates_rate(self, mock_store_model):
        with self.app.test_request_context(method="POST", data={"commission_rate": "12.5"}):
            response = self.controller.seller_commission(1)
            mock_store_model.set_commission.assert_called_once_with(1, 12.5)
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Commission rate updated."), flashes)

    @patch("app.controllers.admin_controller.StoreModel")
    def test_seller_commission_rejects_invalid_value(self, mock_store_model):
        with self.app.test_request_context(method="POST", data={"commission_rate": "abc"}):
            response = self.controller.seller_commission(1)
            mock_store_model.set_commission.assert_not_called()
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Invalid commission rate."), flashes)

<<<<<<< HEAD
=======

# =====================================================================
#  PRODUCT MODERATION
# =====================================================================
>>>>>>> origin/aayushma
class TestProductModeration(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.admin_controller.ProductModel")
    def test_product_approve_redirects_with_success(self, mock_product_model):
        with self.app.test_request_context():
            response = self.controller.product_approve(5)
            mock_product_model.approve.assert_called_once_with(5)
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Product approved."), flashes)

    @patch("app.controllers.admin_controller.ProductModel")
    def test_product_remove_soft_deletes(self, mock_product_model):
        with self.app.test_request_context():
            response = self.controller.product_remove(5)
            mock_product_model.soft_delete.assert_called_once_with(5)
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("warning", "Product removed."), flashes)

<<<<<<< HEAD
=======

# =====================================================================
#  FINANCES
# =====================================================================
>>>>>>> origin/aayushma
class TestFinances(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.admin_controller.render_template")
    def test_finances_renders_transactions_and_commissions(self, mock_render):
        mock_render.return_value = "finances_page"
        self.controller._q.side_effect = [
<<<<<<< HEAD
            [{"id": 1}],           
            [{"id": 1}],           
            {"t": 555.0},          
=======
            [{"id": 1}],           # transactions
            [{"id": 1}],           # commissions
            {"t": 555.0},          # total_rev
>>>>>>> origin/aayushma
        ]
        with self.app.test_request_context():
            result = self.controller.finances()
            self.assertEqual(result, "finances_page")
            _, kwargs = mock_render.call_args
            self.assertEqual(kwargs["total_rev"], 555.0)

    def test_finance_export_returns_csv_response(self):
        self.controller._q.return_value = [
            {"id": 1, "order_number": "ORD-1", "name": "Bob", "amount": 100,
             "method": "cod", "status": "success", "created_at": "2026-01-01"}
        ]
        with self.app.test_request_context():
            response = self.controller.finance_export()
            self.assertEqual(response.headers["Content-Type"], "text/csv")
            self.assertIn("pasalify_transactions.csv", response.headers["Content-Disposition"])
            body = response.get_data(as_text=True)
            self.assertIn("ID,Order,Name,Amount,Method,Status,Created_at", body)

<<<<<<< HEAD
=======

# =====================================================================
#  USER MANAGEMENT
# =====================================================================
>>>>>>> origin/aayushma
class TestUserManagement(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.admin_controller.render_template")
    @patch("app.controllers.admin_controller.UserModel")
    def test_users_lists_everyone(self, mock_user_model, mock_render):
        mock_render.return_value = "users_page"
        mock_user_model.find_all.return_value = [{"id": 1}]
        with self.app.test_request_context():
            result = self.controller.users()
            self.assertEqual(result, "users_page")
            mock_render.assert_called_once_with("admin/users.html", users=[{"id": 1}])

    @patch("app.controllers.admin_controller.UserModel")
    def test_user_toggle_deactivates_active_user(self, mock_user_model):
        mock_user_model.find_by_id.return_value = {"id": 1, "is_active": 1}
        with self.app.test_request_context():
            response = self.controller.user_toggle(1)
            mock_user_model.update.assert_called_once_with(1, {"is_active": 0})
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("info", "User deactivated."), flashes)

    @patch("app.controllers.admin_controller.UserModel")
    def test_user_toggle_activates_inactive_user(self, mock_user_model):
        mock_user_model.find_by_id.return_value = {"id": 1, "is_active": 0}
        with self.app.test_request_context():
            response = self.controller.user_toggle(1)
            mock_user_model.update.assert_called_once_with(1, {"is_active": 1})
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("info", "User activated."), flashes)

    @patch("app.controllers.admin_controller.UserModel")
    def test_user_toggle_missing_user_does_nothing(self, mock_user_model):
        mock_user_model.find_by_id.return_value = None
        with self.app.test_request_context():
            response = self.controller.user_toggle(999)
            mock_user_model.update.assert_not_called()
            self.assertEqual(response.status_code, 302)

<<<<<<< HEAD
=======

# =====================================================================
#  PROMO CODES
# =====================================================================
>>>>>>> origin/aayushma
class TestPromoCodes(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    def test_promo_add_inserts_and_redirects(self):
        with self.app.test_request_context(
            method="POST",
            data={
                "code": "save10", "discount_type": "percent", "discount_value": "10",
                "min_order": "100", "max_uses": "50",
                "valid_from": "2026-01-01", "valid_until": "2026-12-31",
            },
        ):
            response = self.controller.promo_add()
            self.controller._run.assert_called_once()
            args = self.controller._run.call_args[0][1]
<<<<<<< HEAD
            self.assertEqual(args[0], "SAVE10")  
=======
            self.assertEqual(args[0], "SAVE10")  # uppercased
>>>>>>> origin/aayushma
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Promo code created!"), flashes)

    def test_promo_toggle_flips_active_flag(self):
        self.controller._q.return_value = {"is_active": 1}
        with self.app.test_request_context():
            response = self.controller.promo_toggle(1)
            self.controller._run.assert_called_once_with(
                "UPDATE promo_codes SET is_active = %s WHERE id = %s", (0, 1)
            )
            self.assertEqual(response.status_code, 302)

    def test_promo_toggle_missing_code_does_nothing(self):
        self.controller._q.return_value = None
        with self.app.test_request_context():
            self.controller.promo_toggle(999)
            self.controller._run.assert_not_called()

<<<<<<< HEAD
=======

# =====================================================================
#  SYSTEM MONITORING
# =====================================================================
>>>>>>> origin/aayushma
class TestSystemMonitoring(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.admin_controller.render_template")
    def test_system_renders_diagnostics(self, mock_render):
        mock_render.return_value = "system_page"
        self.controller._q.side_effect = [
<<<<<<< HEAD
            [{"id": 1}],          
            {"size": 12.3},       
            [{"table_name": "users", "table_rows": 5}],  
=======
            [{"id": 1}],          # logs
            {"size": 12.3},       # db_size
            [{"table_name": "users", "table_rows": 5}],  # table_counts
>>>>>>> origin/aayushma
        ]
        with self.app.test_request_context():
            result = self.controller.system()
            self.assertEqual(result, "system_page")

    def test_backup_logs_and_redirects(self):
        with self.app.test_request_context():
            response = self.controller.backup()
            self.controller._log.assert_called_once_with("manual_backup_triggered")
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(
                ("info", "Backup initiated. In production, connect mysqldump here."), flashes
            )

<<<<<<< HEAD
=======

# =====================================================================
#  CATEGORIES
# =====================================================================
>>>>>>> origin/aayushma
class TestCategories(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.admin_controller.render_template")
    def test_categories_lists_all(self, mock_render):
        mock_render.return_value = "categories_page"
        self.controller._q.return_value = [{"id": 1, "name": "Gadgets"}]
        with self.app.test_request_context():
            result = self.controller.categories()
            self.assertEqual(result, "categories_page")

    @patch("app.controllers.admin_controller.CategoryModel")
    def test_category_add_creates_and_redirects(self, mock_category_model):
        with self.app.test_request_context(
            method="POST", data={"name": "Home Decor", "icon": "home"}
        ):
            response = self.controller.category_add()
            mock_category_model.create.assert_called_once_with(
                {"name": "Home Decor", "slug": "home-decor", "icon": "home"}
            )
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Category added."), flashes)

<<<<<<< HEAD
=======

# =====================================================================
#  SUPPORT TICKETS (PLATFORM-WIDE)
# =====================================================================
>>>>>>> origin/aayushma
class TestSupportTickets(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.controller = make_controller()

    @patch("app.controllers.admin_controller.render_template")
    def test_support_tickets_groups_messages_by_customer(self, mock_render):
        mock_render.return_value = "support_page"
        users = [{"user_id": 1, "customer_name": "Bob", "customer_email": "bob@x.com",
                   "last_message": "2026-01-01"}]
        messages = [{"id": 1, "message": "help"}]
        self.controller._q.side_effect = [users, messages]

        with self.app.test_request_context():
            result = self.controller.support_tickets()
            self.assertEqual(result, "support_page")
            mock_render.assert_called_once()
            _, kwargs = mock_render.call_args
            self.assertEqual(len(kwargs["tickets"]), 1)
            self.assertEqual(kwargs["tickets"][0]["customer_name"], "Bob")
            self.assertEqual(kwargs["tickets"][0]["messages"], messages)

    def test_support_reply_rejects_empty_message(self):
        with self.app.test_request_context(method="POST", data={"customer_id": "1", "message": ""}):
            response = self.controller.support_reply()
            self.controller._run.assert_not_called()
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Reply cannot be empty."), flashes)

    def test_support_reply_sends_message_and_notifies(self):
        with self.app.test_request_context(
            method="POST", data={"customer_id": "1", "message": "We fixed it."}
        ):
            response = self.controller.support_reply()
            self.controller._run.assert_called_once()
            self.controller._notify.assert_called_once()
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Reply sent."), flashes)

<<<<<<< HEAD
=======

>>>>>>> origin/aayushma
if __name__ == "__main__":
    unittest.main()
