"""
Admin Controller - Sprint 2
US 5.1 Admin Dashboard
"""

from flask import render_template, request, redirect, url_for

from app.controllers.base_controller import BaseController
from app.models import UserModel, ProductModel, StoreModel, CategoryModel


class AdminController(BaseController):

    def _dashboard_stats(self) -> dict:
        orders_row = self._q("SELECT COUNT(*) AS c FROM orders", one=True)
        revenue_row = self._q(
            "SELECT COALESCE(SUM(total_amount),0) AS t FROM orders WHERE payment_status='paid'",
            one=True
        )
        return {
            'total_users':    UserModel.count("role = 'customer'"),
            'total_sellers':  UserModel.count("role = 'seller'"),
            'total_orders':   orders_row['c'] if orders_row else 0,
            'total_revenue':  revenue_row['t'] if revenue_row else 0,
            'pending_stores': StoreModel.count("is_approved = 0"),
            'pending_prods':  ProductModel.count("is_approved = 0 AND is_active = 1"),
        }

    # ── US 5.1 Admin Dashboard ────────────────────────────────────────────────

    def dashboard(self):
        stats = self._dashboard_stats()
        recent_orders = self._q("""
            SELECT o.*, u.name AS customer FROM orders o
            JOIN users u ON u.id = o.user_id ORDER BY o.created_at DESC LIMIT 8
        """)
        monthly = self._q("""
            SELECT DATE_FORMAT(created_at,'%%Y-%%m') AS month,
                   COUNT(*) AS orders, SUM(total_amount) AS revenue
            FROM orders WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY month ORDER BY month
        """)
        logs = self._q("""
            SELECT al.*, u.name FROM activity_logs al
            LEFT JOIN users u ON u.id = al.user_id
            ORDER BY al.created_at DESC LIMIT 10
        """)
        return render_template('admin/dashboard.html',
                               **stats,
                               recent_orders=recent_orders,
                               monthly=monthly,
                               logs=logs)

    def sellers(self):
        all_sellers = StoreModel.all_with_owner()
        return render_template('admin/sellers.html', sellers=all_sellers)

    def seller_approve(self, sid: int):
        StoreModel.approve(sid)
        self._log('seller_approved', 'store', sid)
        self._ok('Seller approved.')
        return redirect(url_for('admin.sellers'))

    def seller_reject(self, sid: int):
        StoreModel.reject(sid)
        self._log('seller_rejected', 'store', sid)
        self._warn('Seller rejected.')
        return redirect(url_for('admin.sellers'))

    def products(self):
        prods = self._q("""
            SELECT p.*, s.name AS store_name, c.name AS cat_name, pi.image_path
            FROM products p
            JOIN stores s ON s.id = p.store_id
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            WHERE p.is_active = 1 ORDER BY p.is_approved ASC, p.created_at DESC
        """)
        return render_template('admin/products.html', products=prods)

    def product_approve(self, pid: int):
        ProductModel.approve(pid)
        self._log('product_approved', 'product', pid)
        self._ok('Product approved.')
        return redirect(url_for('admin.products'))

    def product_remove(self, pid: int):
        ProductModel.soft_delete(pid)
        self._log('product_removed', 'product', pid)
        self._warn('Product removed.')
        return redirect(url_for('admin.products'))

    def users(self):
        all_users = UserModel.find_all()
        return render_template('admin/users.html', users=all_users)

    def user_toggle(self, uid: int):
        user = UserModel.find_by_id(uid)
        if user:
            if user['is_active']:
                UserModel.soft_delete(uid)
                self._warn('User deactivated.')
            else:
                UserModel.activate(uid)
                self._ok('User activated.')
        return redirect(url_for('admin.users'))

    def categories(self):
        cats = CategoryModel.find_all()
        return render_template('admin/categories.html', cats=cats)

    def category_add(self):
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            slug = name.lower().replace(' ', '-')
            if name:
                CategoryModel.create({'name': name, 'slug': slug})
                self._ok(f'Category "{name}" added.')
        return redirect(url_for('admin.categories'))

    def category_delete(self, cid: int):
        self._run("DELETE FROM categories WHERE id = %s", (cid,))
        self._warn('Category deleted.')
        return redirect(url_for('admin.categories'))

    def system(self):
        logs = self._q("""
            SELECT al.*, u.name FROM activity_logs al
            LEFT JOIN users u ON u.id = al.user_id
            ORDER BY al.created_at DESC LIMIT 50
        """)
        return render_template('admin/system.html', logs=logs)

    def finances(self):
        orders = self._q("""
            SELECT o.*, u.name AS customer FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC LIMIT 100
        """)
        total = self._q(
            "SELECT COALESCE(SUM(total_amount),0) AS t FROM orders WHERE payment_status='paid'",
            one=True
        )
        return render_template('admin/finances.html', orders=orders,
                               total_revenue=total['t'] if total else 0)

    def promos(self):
        promos = self._q('SELECT * FROM promo_codes ORDER BY created_at DESC')
        return render_template('admin/promos.html', promos=promos)

    def finance_export(self):
        self._info('Export feature coming in Sprint 3.')
        return redirect(url_for('admin.finances'))

    def backup(self):
        self._info('Backup triggered (stub).')
        return redirect(url_for('admin.dashboard'))


    def promo_add(self):
        if request.method == 'POST':
            code     = request.form.get('code','').strip().upper()
            discount = request.form.get('discount_value', 0)
            dtype    = request.form.get('discount_type','percent')
            if code:
                self._run(
                    "INSERT INTO promo_codes (code,discount_type,discount_value,is_active) VALUES (%s,%s,%s,1)",
                    (code, dtype, discount)
                )
                self._ok(f'Promo code {code} created.')
        return redirect(url_for('admin.promos'))

    def promo_toggle(self, pid: int):
        promo = self._q("SELECT * FROM promo_codes WHERE id=%s", (pid,), one=True)
        if promo:
            new_state = 0 if promo['is_active'] else 1
            self._run("UPDATE promo_codes SET is_active=%s WHERE id=%s", (new_state, pid))
            self._ok('Promo code updated.')
        return redirect(url_for('admin.promos'))
    


admin_controller = AdminController()
