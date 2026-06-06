"""
Admin Controller - Sprint 3
US 5.2 Content Control | US 5.3 Track Transactions
(Builds on Sprint 1+2: Dashboard, Sellers, Products, Users, Finance)
"""

from flask import render_template, request, redirect, url_for, Response
import csv, io
from datetime import datetime

from app.controllers.base_controller import BaseController
from app.models import UserModel, ProductModel, StoreModel, CategoryModel


class AdminController(BaseController):

    def _dashboard_stats(self) -> dict:
        orders_row  = self._q("SELECT COUNT(*) AS c FROM orders", one=True)
        revenue_row = self._q(
            "SELECT COALESCE(SUM(total_amount),0) AS t FROM orders WHERE payment_status='paid'",
            one=True
        )
        flags_row = self._q("SELECT COUNT(*) AS c FROM content_flags WHERE status='pending'", one=True)
        return {
            'total_users':    UserModel.count("role = 'customer'"),
            'total_sellers':  UserModel.count("role = 'seller'"),
            'total_orders':   orders_row['c'] if orders_row else 0,
            'total_revenue':  revenue_row['t'] if revenue_row else 0,
            'pending_stores': StoreModel.count("is_approved = 0"),
            'pending_prods':  ProductModel.count("is_approved = 0 AND is_active = 1"),
            'pending_flags':  flags_row['c'] if flags_row else 0,
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

    # ── Finance ───────────────────────────────────────────────────────────────

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

    def finance_export(self):
        """US 5.3 - Export transactions as CSV."""
        orders = self._q("""
            SELECT o.order_number, u.name AS customer, o.total_amount,
                   o.discount_amount, o.payment_method, o.payment_status,
                   o.status, o.created_at
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC
        """)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Order Number', 'Customer', 'Total', 'Discount',
                         'Payment Method', 'Payment Status', 'Order Status', 'Date'])
        for o in orders:
            writer.writerow([
                o['order_number'], o['customer'], o['total_amount'],
                o['discount_amount'], o['payment_method'], o['payment_status'],
                o['status'], o['created_at']
            ])

        filename = f"pasalify_transactions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    def promos(self):
        promos = self._q('SELECT * FROM promo_codes ORDER BY created_at DESC')
        return render_template('admin/promos.html', promos=promos)

    def backup(self):
        self._info('Backup triggered (stub).')
        return redirect(url_for('admin.dashboard'))

    def promo_add(self):
        if request.method == 'POST':
            code      = request.form.get('code', '').strip().upper()
            discount  = request.form.get('discount_value', 0)
            dtype     = request.form.get('discount_type', 'percent')
            min_order = request.form.get('min_order', 0)
            max_uses  = request.form.get('max_uses') or None
            valid_from  = request.form.get('valid_from') or None
            valid_until = request.form.get('valid_until') or None
            if code:
                self._run(
                    """INSERT INTO promo_codes
                       (code, discount_type, discount_value, min_order, max_uses, valid_from, valid_until, is_active)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,1)""",
                    (code, dtype, discount, min_order, max_uses, valid_from, valid_until)
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

    # ── US 5.2 Content Control ────────────────────────────────────────────────

    def content_control(self):
        """US 5.2 - View flagged content and manage reviews/products."""
        flags = self._q("""
            SELECT cf.*, u.name AS flagged_by_name
            FROM content_flags cf
            LEFT JOIN users u ON u.id = cf.flagged_by
            WHERE cf.status = 'pending'
            ORDER BY cf.created_at DESC
        """)

        # Pending reviews (not yet approved)
        pending_reviews = self._q("""
            SELECT r.*, u.name AS reviewer_name, p.name AS product_name,
                   s.name AS store_name
            FROM reviews r
            JOIN users u ON u.id = r.user_id
            JOIN products p ON p.id = r.product_id
            JOIN stores s ON s.id = p.store_id
            WHERE r.is_approved = 0
            ORDER BY r.created_at DESC
        """)

        return render_template('admin/content_control.html',
                               flags=flags,
                               pending_reviews=pending_reviews)

    def review_approve(self, rid: int):
        self._run("UPDATE reviews SET is_approved=1 WHERE id=%s", (rid,))
        self._ok('Review approved.')
        return redirect(url_for('admin.content_control'))

    def review_remove(self, rid: int):
        self._run("DELETE FROM reviews WHERE id=%s", (rid,))
        self._warn('Review removed.')
        return redirect(url_for('admin.content_control'))

    def flag_resolve(self, fid: int):
        action = request.form.get('action', 'dismiss')
        if action == 'dismiss':
            self._run("UPDATE content_flags SET status='dismissed' WHERE id=%s", (fid,))
            self._info('Flag dismissed.')
        elif action == 'remove':
            flag = self._q("SELECT * FROM content_flags WHERE id=%s", (fid,), one=True)
            if flag:
                if flag['entity_type'] == 'review':
                    self._run("DELETE FROM reviews WHERE id=%s", (flag['entity_id'],))
                elif flag['entity_type'] == 'product':
                    self._run("UPDATE products SET is_active=0 WHERE id=%s", (flag['entity_id'],))
                self._run("UPDATE content_flags SET status='reviewed' WHERE id=%s", (fid,))
                self._warn('Content removed.')
        return redirect(url_for('admin.content_control'))

    # ── US 5.3 Track Transactions ─────────────────────────────────────────────

    def transactions(self):
        """US 5.3 - Detailed transaction tracking."""
        page     = int(request.args.get('page', 1))
        per_page = 20
        offset   = (page - 1) * per_page

        status_filter = request.args.get('status', '')
        method_filter = request.args.get('method', '')

        sql  = """
            SELECT p.*, o.order_number, u.name AS customer_name,
                   o.status AS order_status
            FROM payments p
            JOIN orders o ON o.id = p.order_id
            JOIN users  u ON u.id = p.user_id
            WHERE 1=1
        """
        args = []
        if status_filter:
            sql += " AND p.status = %s"
            args.append(status_filter)
        if method_filter:
            sql += " AND p.method = %s"
            args.append(method_filter)

        total_count = self._q(
            f"SELECT COUNT(*) AS c FROM ({sql}) t", tuple(args), one=True
        )['c']

        sql += f" ORDER BY p.created_at DESC LIMIT {per_page} OFFSET {offset}"
        payments = self._q(sql, tuple(args))

        # Aggregates
        summary = self._q("""
            SELECT
                COALESCE(SUM(CASE WHEN status='success' THEN amount ELSE 0 END), 0) AS total_success,
                COALESCE(SUM(CASE WHEN status='pending' THEN amount ELSE 0 END), 0) AS total_pending,
                COALESCE(SUM(CASE WHEN status='refunded' THEN amount ELSE 0 END), 0) AS total_refunded,
                COUNT(*) AS total_transactions
            FROM payments
        """, one=True)

        return render_template('admin/transactions.html',
                               payments=payments,
                               summary=summary,
                               page=page,
                               total_pages=(total_count + per_page - 1) // per_page,
                               status_filter=status_filter,
                               method_filter=method_filter)

    def commission_report(self):
        """US 5.3 - Commission tracking per store."""
        commissions = self._q("""
            SELECT s.name AS store_name, u.name AS seller_name,
                   COALESCE(SUM(c.seller_amount),0) AS total_seller,
                   COALESCE(SUM(c.platform_amount),0) AS total_platform,
                   COUNT(*) AS transaction_count
            FROM commissions c
            JOIN stores s ON s.id = c.store_id
            JOIN users  u ON u.id = s.user_id
            GROUP BY s.id
            ORDER BY total_platform DESC
        """)
        return render_template('admin/commissions.html', commissions=commissions)


admin_controller = AdminController()
