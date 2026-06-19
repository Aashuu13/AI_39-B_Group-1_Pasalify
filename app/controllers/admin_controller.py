"""
==============================================================
OOP Concept: INHERITANCE & ENCAPSULATION (Admin Controller)
==============================================================
- Inheritance: AdminController extends BaseController.
- Encapsulation: CSV export logic is hidden in _export_csv();
  dashboard stats are gathered in _dashboard_stats().
  Routes call one method; they never see the SQL.
- Polymorphism: seller_approve / seller_reject both change
  store state but produce different side-effects.
==============================================================
"""

import csv
import io

from flask import render_template, request, redirect, url_for, session, flash, make_response

from app.controllers.base_controller import BaseController
from app.models import UserModel, ProductModel, StoreModel, CategoryModel


class AdminController(BaseController):
    """
    Handles all admin-facing views:
    dashboard, sellers, products, finances, users,
    promo codes, system monitoring, categories.

    Inherits from BaseController:
        _ok/_err/_warn/_info, _q/_run, _log, _notify,
        _current_user_id, _is_logged_in
    """


    def _dashboard_stats(self) -> dict:
        """
        Gather all dashboard KPIs in one method.
        Encapsulation: the dashboard view calls this; it never
        writes a single SQL query itself.
        """
        return {
            'total_users':    UserModel.count("role = 'customer'"),
            'total_sellers':  UserModel.count("role = 'seller'"),
            'total_orders':   self._q("SELECT COUNT(*) AS c FROM orders", one=True)['c'],
            'total_revenue':  self._q(
                "SELECT COALESCE(SUM(total_amount),0) AS t FROM orders WHERE payment_status='paid'",
                one=True
            )['t'],
            'pending_stores': StoreModel.count("is_approved = 0"),
            'pending_prods':  ProductModel.count("is_approved = 0 AND is_active = 1"),
        }

    def _export_csv(self, rows: list[dict], headers: list[str],
                    filename: str):
        """
        Build and return a CSV download response.
        Encapsulation: CSV generation lives here, not in the route.
        """
        si = io.StringIO()
        w  = csv.writer(si)
        w.writerow(headers)
        for r in rows:
            w.writerow([r.get(h.lower().replace(' ', '_'), '') for h in headers])
        out = make_response(si.getvalue())
        out.headers['Content-Disposition'] = f'attachment; filename={filename}'
        out.headers['Content-Type'] = 'text/csv'
        return out


    def dashboard(self):
        stats         = self._dashboard_stats()
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
            LEFT JOIN users u ON u.id = al.user_id ORDER BY al.created_at DESC LIMIT 10
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
        """Approve a store and notify the owner."""
        StoreModel.approve(sid)
        store = StoreModel.find_by_id(sid)
        if store:
            self._notify(
                store['user_id'], 'Store Approved!',
                f'Your store "{store["name"]}" has been approved. Start selling now!',
                'system'
            )
        self._log('seller_approved', 'store', sid)
        self._ok('Seller approved.')
        return redirect(url_for('admin.sellers'))

    def seller_reject(self, sid: int):
        """Reject (deactivate) a store."""
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


    def finances(self):
        transactions = self._q("""
            SELECT p.*, o.order_number, u.name AS customer
            FROM payments p
            JOIN orders o ON o.id = p.order_id
            JOIN users u ON u.id = p.user_id
            ORDER BY p.created_at DESC
        """)
        commissions = self._q("""
            SELECT c.*, s.name AS store_name FROM commissions c
            JOIN stores s ON s.id = c.store_id ORDER BY c.created_at DESC LIMIT 50
        """)
        total_rev = self._q(
            "SELECT COALESCE(SUM(platform_amount),0) AS t FROM commissions", one=True
        )
        return render_template('admin/finances.html',
                               transactions=transactions,
                               commissions=commissions,
                               total_rev=total_rev['t'])

    def finance_export(self):
        """Export transactions as CSV. Encapsulation: _export_csv hides io logic."""
        rows = self._q("""
            SELECT p.id, o.order_number, u.name, p.amount,
                   p.method, p.status, p.created_at
            FROM payments p
            JOIN orders o ON o.id = p.order_id
            JOIN users u ON u.id = p.user_id
            ORDER BY p.created_at DESC
        """)
        return self._export_csv(
            rows,
            ['ID', 'Order', 'Name', 'Amount', 'Method', 'Status', 'Created_at'],
            'pasalify_transactions.csv'
        )


    def users(self):
        all_users = UserModel.find_all()
        return render_template('admin/users.html', users=all_users)

    def user_toggle(self, uid: int):
        """Toggle a user's active status (Polymorphism: same method, two outcomes)."""
        u = UserModel.find_by_id(uid)
        if u:
            new_status = 0 if u['is_active'] else 1
            UserModel.update(uid, {'is_active': new_status})
            status = 'deactivated' if u['is_active'] else 'activated'
            self._log(f'user_{status}', 'user', uid)
            self._info(f'User {status}.')
        return redirect(url_for('admin.users'))


    def promos(self):
        codes = self._q("SELECT * FROM promo_codes ORDER BY created_at DESC")
        return render_template('admin/promos.html', codes=codes)

    def promo_add(self):
        self._run("""
            INSERT INTO promo_codes
              (code, discount_type, discount_value, min_order, max_uses,
               valid_from, valid_until)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form.get('code', '').strip().upper(),
            request.form.get('discount_type', 'percent'),
            float(request.form.get('discount_value', 0)),
            float(request.form.get('min_order', 0)),
            request.form.get('max_uses') or None,
            request.form.get('valid_from') or None,
            request.form.get('valid_until') or None,
        ))
        self._ok('Promo code created!')
        return redirect(url_for('admin.promos'))

    def promo_toggle(self, pid: int):
        p = self._q("SELECT is_active FROM promo_codes WHERE id = %s", (pid,), one=True)
        if p:
            self._run("UPDATE promo_codes SET is_active = %s WHERE id = %s",
                      (0 if p['is_active'] else 1, pid))
        return redirect(url_for('admin.promos'))


    def system(self):
        logs = self._q("""
            SELECT al.*, u.name FROM activity_logs al
            LEFT JOIN users u ON u.id = al.user_id ORDER BY al.created_at DESC LIMIT 100
        """)
        db_size = self._q("""
            SELECT ROUND(SUM(data_length + index_length)/1024/1024, 2) AS size
            FROM information_schema.tables WHERE table_schema = 'pasalify'
        """, one=True)
        table_counts = self._q("""
            SELECT table_name, table_rows FROM information_schema.tables
            WHERE table_schema = 'pasalify' ORDER BY table_rows DESC
        """)
        return render_template('admin/system.html', logs=logs,
                               db_size=db_size, table_counts=table_counts)

    def backup(self):
        self._log('manual_backup_triggered')
        self._info('Backup initiated. In production, connect mysqldump here.')
        return redirect(url_for('admin.system'))


    def categories(self):
        cats = self._q("SELECT * FROM categories ORDER BY name")
        return render_template('admin/categories.html', cats=cats)

    def category_add(self):
        name = request.form.get('name', '').strip()
        slug = name.lower().replace(' ', '-')
        icon = request.form.get('icon', 'tag')
        CategoryModel.create({'name': name, 'slug': slug, 'icon': icon})
        self._ok('Category added.')
        return redirect(url_for('admin.categories'))



    def support_tickets(self):
        tickets = self._q("""
            SELECT sm.*, u.name AS customer_name, u.email AS customer_email
            FROM support_messages sm
            LEFT JOIN users u ON u.id = sm.user_id
            WHERE sm.role = 'user'
            ORDER BY sm.created_at DESC
        """)
        for t in tickets:
            t['replies'] = self._q("""
                SELECT sm.*, u.name AS sender_name
                FROM support_messages sm
                LEFT JOIN users u ON u.id = sm.user_id
                WHERE sm.role = 'admin' AND sm.parent_id = %s
                ORDER BY sm.created_at ASC
            """, (t['id'],))
        return render_template('admin/support.html', tickets=tickets)

    def support_reply(self):
        parent_id   = request.form.get('parent_id', type=int)
        customer_id = request.form.get('customer_id', type=int)
        message     = request.form.get('message', '').strip()
        if not message or not parent_id:
            self._err('Reply cannot be empty.')
            return redirect(url_for('admin.support_tickets'))
        self._run("""
            INSERT INTO support_messages (user_id, role, message, parent_id)
            VALUES (%s, 'admin', %s, %s)
        """, (self._current_user_id(), message, parent_id))
        if customer_id:
            self._notify(customer_id, 'Support Reply',
                         'Admin replied to your support message.', 'system')
        self._ok('Reply sent.')
        return redirect(url_for('admin.support_tickets'))


admin_controller = AdminController()# Manages admin operations and backup
