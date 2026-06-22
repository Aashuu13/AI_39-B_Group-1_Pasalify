<<<<<<< HEAD

import csv
import io

=======
import csv
import io

>>>>>>> origin/aayushma
from flask import render_template, request, redirect, url_for, session, flash, make_response

from app.controllers.base_controller import BaseController
from app.models import UserModel, ProductModel, StoreModel, CategoryModel

class AdminController(BaseController):
    """
    Handles all admin-facing views:
    dashboard, sellers, products, finances, users,
    promo codes, system monitoring, categories.

    Inherited from BaseController:
        _ok/_err/_warn/_info, _q/_run, _log, _notify,
        _current_user_id, _is_logged_in
    """

    def _dashboard_stats(self) -> dict:
        """
        Gather every dashboard KPI (user/seller/order counts, total
        revenue, pending approvals) in one method, so dashboard()
        itself never has to write a single SQL query.
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
        Turn a list of dict rows into a downloadable CSV response.
        Encapsulation: nothing outside this method needs to know
        about io.StringIO or response headers — finance_export()
        just calls this with its rows and a filename.
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
        """Admin home page: platform-wide KPIs, recent orders across
        every store, a 6-month revenue trend, and the latest activity log."""
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
        """List every store along with its owner, for approve/reject actions."""
        all_sellers = StoreModel.all_with_owner()
        return render_template('admin/sellers.html', sellers=all_sellers)

    def seller_approve(self, sid: int):
        """Approve a pending store and notify its owner."""
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
        """Reject a store — marks it unapproved/inactive rather than deleting it."""
        StoreModel.reject(sid)
        self._log('seller_rejected', 'store', sid)
        self._warn('Seller rejected.')
        return redirect(url_for('admin.sellers'))

    def seller_commission(self, sid: int):
        """Update a store's platform commission rate (%) from the
        sellers admin page."""
        try:
            rate = float(request.form.get('commission_rate', 0))
        except (TypeError, ValueError):
            self._err('Invalid commission rate.')
            return redirect(url_for('admin.sellers'))
        StoreModel.set_commission(sid, rate)
        self._log('commission_updated', 'store', sid)
        self._ok('Commission rate updated.')
        return redirect(url_for('admin.sellers'))

    def products(self):
        """All active products, unapproved ones listed first so the
        admin sees what's awaiting review at a glance."""
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
        """Approve a product so it becomes visible to customers."""
        ProductModel.approve(pid)
        self._log('product_approved', 'product', pid)
        self._ok('Product approved.')
        return redirect(url_for('admin.products'))

    def product_remove(self, pid: int):
        """Soft-delete a product (keeps the row for order history)."""
        ProductModel.soft_delete(pid)
        self._log('product_removed', 'product', pid)
        self._warn('Product removed.')
        return redirect(url_for('admin.products'))

    def finances(self):
        """Payment transactions, recent seller commissions, and total
        platform revenue (the platform's cut of every commission)."""
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
        """Download every transaction as a CSV file (Encapsulation:
        _export_csv hides all the io/response plumbing)."""
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
        """List every registered user (customers, sellers, and admins)."""
        all_users = UserModel.find_all()
        return render_template('admin/users.html', users=all_users)

    def user_toggle(self, uid: int):
        """Flip a user's active status with one click — same method
        produces either an activation or a deactivation depending on
        the user's current state (Polymorphism: one call, two outcomes)."""
        u = UserModel.find_by_id(uid)
        if u:
            new_status = 0 if u['is_active'] else 1
            UserModel.update(uid, {'is_active': new_status})
            status = 'deactivated' if u['is_active'] else 'activated'
            self._log(f'user_{status}', 'user', uid)
            self._info(f'User {status}.')
        return redirect(url_for('admin.users'))

    def promos(self):
        """List every promo code that has ever been created."""
        codes = self._q("SELECT * FROM promo_codes ORDER BY created_at DESC")
        return render_template('admin/promos.html', codes=codes)

    def promo_add(self):
        """Create a new promo code from the admin form."""
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
        """Turn a promo code on/off without deleting it."""
        p = self._q("SELECT is_active FROM promo_codes WHERE id = %s", (pid,), one=True)
        if p:
            self._run("UPDATE promo_codes SET is_active = %s WHERE id = %s",
                      (0 if p['is_active'] else 1, pid))
        return redirect(url_for('admin.promos'))

    def system(self):
        """Diagnostics page: the latest 100 activity-log entries, the
        database's total size on disk, and a per-table row-count summary."""
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
<<<<<<< HEAD

    def backup(self):
        """Placeholder for a manual backup trigger — in production this
        would shell out to mysqldump or call a managed backup API."""
        self._log('manual_backup_triggered')
        self._info('Backup initiated. In production, connect mysqldump here.')
        return redirect(url_for('admin.system'))

    def categories(self):
        """List every product category."""
        cats = self._q("SELECT * FROM categories ORDER BY name")
        return render_template('admin/categories.html', cats=cats)

    def category_add(self):
        """Create a new category from the admin form."""
        name = request.form.get('name', '').strip()
        slug = name.lower().replace(' ', '-')
        icon = request.form.get('icon', 'tag')
        CategoryModel.create({'name': name, 'slug': slug, 'icon': icon})
        self._ok('Category added.')
        return redirect(url_for('admin.categories'))

    def support_tickets(self):
        """
        Group every customer's support-chatbot messages into one
        "ticket" per customer, exactly like seller_controller's
        version, but WITHOUT the store filter — an admin should see
        every customer's support thread on the platform, not just
        the ones tied to one store.

        Bug fix: this used to render a template named
        'admin/support_tickets.html', which doesn't exist (the real
        file is 'admin/support.html'), and it passed a flat list of
        raw message rows instead of the grouped-by-customer shape
        the template actually expects (t.customer_name,
        t.customer_email, t.last_message, t.messages). Both are
        corrected below.
        """
        users = self._q("""
            SELECT DISTINCT sm.user_id, u.name AS customer_name, u.email AS customer_email,
                   MAX(sm.created_at) AS last_message
            FROM support_messages sm
            LEFT JOIN users u ON u.id = sm.user_id
            WHERE sm.role = 'user'
            GROUP BY sm.user_id, u.name, u.email
            ORDER BY last_message DESC
        """)
        tickets = []
        for user in users:
            messages = self._q("""
                SELECT * FROM support_messages
                WHERE user_id = %s
                ORDER BY created_at ASC
            """, (user['user_id'],))
            tickets.append({
                'user_id':        user['user_id'],
                'customer_name':  user['customer_name'],
                'customer_email': user['customer_email'],
                'last_message':   user['last_message'],
                'messages':       messages,
            })
        return render_template('admin/support.html', tickets=tickets)

    def support_reply(self):
        """Reply to a customer's support thread directly as 'admin'
        (stored straight in support_messages, unlike the seller's
        reply flow which moves into the regular chat system)."""
        customer_id = request.form.get('customer_id', type=int)
        message     = request.form.get('message', '').strip()
        if not message or not customer_id:
            self._err('Reply cannot be empty.')
            return redirect(url_for('admin.support_tickets'))
        self._run(
            "INSERT INTO support_messages (user_id, role, message) VALUES (%s, 'admin', %s)",
            (customer_id, message)
        )
        self._notify(customer_id, 'Support Reply',
                     'Admin replied to your support message.', 'system')
        self._ok('Reply sent.')
        return redirect(url_for('admin.support_tickets'))
=======
>>>>>>> origin/aayushma

    def backup(self):
        """Placeholder for a manual backup trigger — in production this
        would shell out to mysqldump or call a managed backup API."""
        self._log('manual_backup_triggered')
        self._info('Backup initiated. In production, connect mysqldump here.')
        return redirect(url_for('admin.system'))

    def categories(self):
        """List every product category."""
        cats = self._q("SELECT * FROM categories ORDER BY name")
        return render_template('admin/categories.html', cats=cats)

    def category_add(self):
        """Create a new category from the admin form."""
        name = request.form.get('name', '').strip()
        slug = name.lower().replace(' ', '-')
        icon = request.form.get('icon', 'tag')
        CategoryModel.create({'name': name, 'slug': slug, 'icon': icon})
        self._ok('Category added.')
        return redirect(url_for('admin.categories'))

    def support_tickets(self):
        """
        Group every customer's support-chatbot messages into one
        "ticket" per customer, exactly like seller_controller's
        version, but WITHOUT the store filter — an admin should see
        every customer's support thread on the platform, not just
        the ones tied to one store.

        Bug fix: this used to render a template named
        'admin/support_tickets.html', which doesn't exist (the real
        file is 'admin/support.html'), and it passed a flat list of
        raw message rows instead of the grouped-by-customer shape
        the template actually expects (t.customer_name,
        t.customer_email, t.last_message, t.messages). Both are
        corrected below.
        """
        users = self._q("""
            SELECT DISTINCT sm.user_id, u.name AS customer_name, u.email AS customer_email,
                   MAX(sm.created_at) AS last_message
            FROM support_messages sm
            LEFT JOIN users u ON u.id = sm.user_id
            WHERE sm.role = 'user'
            GROUP BY sm.user_id, u.name, u.email
            ORDER BY last_message DESC
        """)
        tickets = []
        for user in users:
            messages = self._q("""
                SELECT * FROM support_messages
                WHERE user_id = %s
                ORDER BY created_at ASC
            """, (user['user_id'],))
            tickets.append({
                'user_id':        user['user_id'],
                'customer_name':  user['customer_name'],
                'customer_email': user['customer_email'],
                'last_message':   user['last_message'],
                'messages':       messages,
            })
        return render_template('admin/support.html', tickets=tickets)

    def support_reply(self):
        """Reply to a customer's support thread directly as 'admin'
        (stored straight in support_messages, unlike the seller's
        reply flow which moves into the regular chat system)."""
        customer_id = request.form.get('customer_id', type=int)
        message     = request.form.get('message', '').strip()
        if not message or not customer_id:
            self._err('Reply cannot be empty.')
            return redirect(url_for('admin.support_tickets'))
        self._run(
            "INSERT INTO support_messages (user_id, role, message) VALUES (%s, 'admin', %s)",
            (customer_id, message)
        )
        self._notify(customer_id, 'Support Reply',
                     'Admin replied to your support message.', 'system')
        self._ok('Reply sent.')
        return redirect(url_for('admin.support_tickets'))

admin_controller = AdminController()