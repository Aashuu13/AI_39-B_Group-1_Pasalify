"""
Sprint 2 - Customer Controller
US 2.1 Search Products  | US 2.2 View Product   | US 2.3 Manage Cart
US 3.1 Place Order      | US 3.3 Make Payment   | US 4.1 Browse Stores
US 4.2 Wishlist
"""

import uuid
from datetime import datetime

from flask import render_template, request, redirect, url_for, session, flash, jsonify

from app.controllers.base_controller import BaseController
from app.models import UserModel, ProductModel, CategoryModel, OrderModel
from app import db


class CustomerController(BaseController):

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_cart_items(self) -> list[dict]:
        """Return all cart items for the current user, enriched with product/store info."""
        return self._q("""
            SELECT
                ci.id, ci.quantity,
                p.id        AS product_id,
                p.name,
                p.price,
                p.stock_qty,
                p.store_id,
                pi.image_path,
                s.name      AS store_name
            FROM cart_items ci
            JOIN  products       p  ON p.id  = ci.product_id
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN  stores         s  ON s.id  = p.store_id
            WHERE ci.user_id = %s
        """, (self._current_user_id(),))

    def _cart_total(self, items: list[dict]) -> float:
        return sum(float(i['price']) * i['quantity'] for i in items)

    def _generate_order_number(self) -> str:
        suffix = str(uuid.uuid4())[:6].upper()
        return f"ORD-{datetime.now().strftime('%Y%m%d')}-{suffix}"

    # ── US 2.1  Browse / Search Products ─────────────────────────────────────

    def home(self):
        cats = CategoryModel.find_all()
        featured = self._q("""
            SELECT p.*, pi.image_path, s.name AS store_name, s.slug AS store_slug
            FROM   products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN   stores s ON s.id = p.store_id
            WHERE  p.is_active = 1 AND p.is_approved = 1
            ORDER  BY p.created_at DESC
            LIMIT  12
        """)
        return render_template('customer/home.html', cats=cats, featured=featured)

    def products(self):
        q          = request.args.get('q', '')
        cat_slug   = request.args.get('cat', '')
        sort       = request.args.get('sort', 'newest')
        min_price  = request.args.get('min_price', '')
        max_price  = request.args.get('max_price', '')
        min_rating = request.args.get('rating', '')

        items = ProductModel.search(
            query=q,
            cat_slug=cat_slug,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            min_rating=min_rating,
        )
        cats = CategoryModel.find_all()
        return render_template(
            'customer/products.html',
            items=items, cats=cats,
            q=q, cat_slug=cat_slug, sort=sort,
        )

    # ── US 2.2  View Product ──────────────────────────────────────────────────

    def product_detail(self, pid: int):
        p = ProductModel.get_with_images(pid)
        if not p:
            self._err('Product not found.')
            return redirect(url_for('customer.products'))

        images = self._q(
            "SELECT * FROM product_images WHERE product_id = %s ORDER BY is_primary DESC",
            (pid,)
        )
        related = self._q("""
            SELECT p2.*, pi.image_path
            FROM   products p2
            LEFT JOIN product_images pi ON pi.product_id = p2.id AND pi.is_primary = 1
            WHERE  p2.category_id = %s
              AND  p2.id          != %s
              AND  p2.is_active   = 1
              AND  p2.is_approved = 1
            LIMIT  4
        """, (p['category_id'], pid))

        return render_template(
            'customer/product_detail.html',
            p=p, images=images, related=related,
        )

    # ── US 4.1  Browse Stores ─────────────────────────────────────────────────

    def stores(self):
        stores = self._q("""
            SELECT s.*, COUNT(p.id) AS product_count
            FROM   stores s
            LEFT JOIN products p
                   ON p.store_id    = s.id
                  AND p.is_active   = 1
                  AND p.is_approved = 1
            GROUP  BY s.id
            ORDER  BY s.name ASC
        """)
        return render_template('customer/stores.html', stores=stores)

    def store_detail(self, slug: str):
        store = self._q(
            "SELECT * FROM stores WHERE slug = %s AND is_active = 1",
            (slug,), one=True
        )
        if not store:
            self._err('Store not found.')
            return redirect(url_for('customer.stores'))

        products = self._q("""
            SELECT p.*, pi.image_path
            FROM   products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            WHERE  p.store_id    = %s
              AND  p.is_active   = 1
              AND  p.is_approved = 1
            ORDER  BY p.created_at DESC
        """, (store['id'],))

        return render_template('customer/store_detail.html', store=store, products=products)

    # ── US 4.2  Wishlist ──────────────────────────────────────────────────────

    def wishlist(self):
        items = self._q("""
            SELECT w.id, p.*, pi.image_path, s.name AS store_name
            FROM   wishlist w
            JOIN   products p  ON p.id  = w.product_id
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN   stores   s  ON s.id  = p.store_id
            WHERE  w.user_id = %s
            ORDER  BY w.created_at DESC
        """, (self._current_user_id(),))
        return render_template('customer/wishlist.html', items=items)

    def wishlist_toggle(self, pid: int):
        uid      = self._current_user_id()
        existing = self._q(
            "SELECT id FROM wishlist WHERE user_id = %s AND product_id = %s",
            (uid, pid), one=True,
        )
        if existing:
            self._run("DELETE FROM wishlist WHERE id = %s", (existing['id'],))
            self._info('Removed from wishlist.')
        else:
            self._run(
                "INSERT INTO wishlist (user_id, product_id) VALUES (%s, %s)",
                (uid, pid),
            )
            self._ok('Added to wishlist!')
        return redirect(request.referrer or url_for('customer.wishlist'))

    # ── US 2.3  Manage Cart ───────────────────────────────────────────────────

    def cart(self):
        items = self._get_cart_items()
        return render_template(
            'customer/cart.html',
            items=items,
            total=self._cart_total(items),
        )

    def cart_add(self, pid: int):
        qty = int(request.form.get('quantity', 1))
        p   = ProductModel.find_by_id(pid)

        if not p:
            self._err('Product not found.')
            return redirect(url_for('customer.products'))

        if p['stock_qty'] < qty:
            self._err('Not enough stock.')
            return redirect(request.referrer or url_for('customer.products'))

        uid      = self._current_user_id()
        existing = self._q(
            "SELECT id FROM cart_items WHERE user_id = %s AND product_id = %s",
            (uid, pid), one=True,
        )
        if existing:
            self._run(
                "UPDATE cart_items SET quantity = quantity + %s WHERE id = %s",
                (qty, existing['id']),
            )
        else:
            self._run(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (uid, pid, qty),
            )

        self._ok('Added to cart!')
        return redirect(request.referrer or url_for('customer.cart'))

    def cart_update(self, cid: int):
        qty = int(request.form.get('quantity', 1))
        uid = self._current_user_id()

        if qty < 1:
            self._run(
                "DELETE FROM cart_items WHERE id = %s AND user_id = %s",
                (cid, uid),
            )
        else:
            self._run(
                "UPDATE cart_items SET quantity = %s WHERE id = %s AND user_id = %s",
                (qty, cid, uid),
            )
        return redirect(url_for('customer.cart'))

    def cart_remove(self, cid: int):
        self._run(
            "DELETE FROM cart_items WHERE id = %s AND user_id = %s",
            (cid, self._current_user_id()),
        )
        self._info('Item removed.')
        return redirect(url_for('customer.cart'))

    # ── US 3.1 / 3.3  Checkout & Payment ─────────────────────────────────────

    def checkout(self):
        items = self._get_cart_items()
        if not items:
            self._warn('Your cart is empty.')
            return redirect(url_for('customer.cart'))

        subtotal = self._cart_total(items)
        user     = UserModel.find_by_id(self._current_user_id())

        if request.method == 'POST':
            return self._process_checkout(items, subtotal)

        return render_template(
            'customer/checkout.html',
            items=items, subtotal=subtotal, user=user,
        )

    def _process_checkout(self, items: list[dict], subtotal: float):
        uid      = self._current_user_id()
        method   = request.form.get('payment_method', 'cod')
        order_no = self._generate_order_number()

        # ── Create order ──────────────────────────────────────────────────────
        oid = self._run("""
            INSERT INTO orders
              (user_id, order_number, full_name, phone, address, city,
               total_amount, payment_method, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'placed')
        """, (
            uid,
            order_no,
            request.form.get('full_name', ''),
            request.form.get('phone', ''),
            request.form.get('address', ''),
            request.form.get('city', ''),
            subtotal,
            method,
        ))

        # ── Create order items & update stock ─────────────────────────────────
        for item in items:
            price = float(item['price'])
            self._run("""
                INSERT INTO order_items
                  (order_id, product_id, store_id, product_name, price, quantity, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                oid,
                item['product_id'],
                item['store_id'],
                item['name'],
                price,
                item['quantity'],
                price * item['quantity'],
            ))
            ProductModel.decrement_stock(item['product_id'], item['quantity'])

        # ── Clear cart ────────────────────────────────────────────────────────
        self._run("DELETE FROM cart_items WHERE user_id = %s", (uid,))

        # ── Record payment ────────────────────────────────────────────────────
        pay_status = 'success' if method == 'cod' else 'pending'
        self._run(
            "INSERT INTO payments (order_id, user_id, amount, method, status) VALUES (%s, %s, %s, %s, %s)",
            (oid, uid, subtotal, method, pay_status),
        )

        self._ok(f'Order {order_no} placed successfully!')
        return redirect(url_for('customer.order_detail', oid=oid))

    # ── Orders ────────────────────────────────────────────────────────────────

    def orders(self):
        ords = self._q(
            "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC",
            (self._current_user_id(),)
        )
        return render_template('customer/orders.html', orders=ords)

    def order_detail(self, oid: int):
        order = self._q(
            "SELECT * FROM orders WHERE id = %s AND user_id = %s",
            (oid, self._current_user_id()), one=True,
        )
        if not order:
            self._err('Order not found.')
            return redirect(url_for('customer.orders'))

        items = self._q("""
            SELECT oi.*, pi.image_path
            FROM   order_items oi
            LEFT JOIN product_images pi
                   ON pi.product_id = oi.product_id AND pi.is_primary = 1
            WHERE  oi.order_id = %s
        """, (oid,))

        return render_template('customer/order_detail.html', order=order, items=items)
    # ── Support ───────────────────────────────────────────────────────────────────

    def support(self):
        return render_template('customer/support.html')

    # ── Profile ───────────────────────────────────────────────────────────────────

    def profile(self):
        user = self._q("SELECT * FROM users WHERE id = %s",
                       (self._current_user_id(),), one=True)
        if not user:
            return redirect(url_for('auth.login'))
        if request.method == 'POST':
            name  = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            self._run("UPDATE users SET name=%s, phone=%s WHERE id=%s",
                      (name, phone, self._current_user_id()))
            session['name'] = name
            self._ok('Profile updated!')
            return redirect(url_for('customer.profile'))
        return render_template('customer/profile.html', user=user)

    # ── Notifications ─────────────────────────────────────────────────────────────

    def notifications(self):
        notifs = self._q(
            "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 30",
            (self._current_user_id(),)
        )
        self._run("UPDATE notifications SET is_read=1 WHERE user_id=%s",
                  (self._current_user_id(),))
        return render_template('customer/notifications.html', notifications=notifs)

    # ── Payment History ───────────────────────────────────────────────────────────

    def payment_history(self):
        payments = self._q("""
            SELECT p.*, o.order_number FROM payments p
            JOIN orders o ON o.id = p.order_id
            WHERE p.user_id = %s ORDER BY p.created_at DESC
        """, (self._current_user_id(),))
        return render_template('customer/payment_history.html', payments=payments)

    # ── Reviews ───────────────────────────────────────────────────────────────────

    def submit_review(self, pid: int):
        rating = int(request.form.get('rating', 5))
        title  = request.form.get('title', '').strip()
        body   = request.form.get('body', '').strip()
        uid    = self._current_user_id()
        try:
            self._run(
                """INSERT INTO reviews (product_id,user_id,rating,title,body,is_approved)
                   VALUES (%s,%s,%s,%s,%s,1)
                   ON DUPLICATE KEY UPDATE rating=%s,title=%s,body=%s""",
                (pid, uid, rating, title, body, rating, title, body)
            )
            self._ok('Review submitted!')
        except Exception:
            self._err('Could not submit review.')
        return redirect(url_for('customer.product_detail', pid=pid))

    # ── Store page alias ──────────────────────────────────────────────────────────

    def store_page(self, slug: str):
        return self.store_detail(slug)
    

     # ── US 1.5  Edit Profile ──────────────────────────────────────────────────

    def profile(self):
        """
        GET  /profile  → show the edit-profile form pre-filled with user data
        POST /profile  → validate & save name, phone, address, city, avatar
        """
        user = self._q(
            "SELECT * FROM users WHERE id = %s",
            (self._current_user_id(),),
            one=True,
        )
        if not user:
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            name    = request.form.get('name', '').strip()
            phone   = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            city    = request.form.get('city', '').strip()

            # Save uploaded avatar; fall back to existing avatar if none uploaded
            avatar = (
                self._save_file(request.files.get('avatar'), 'images')
                or user.get('avatar')
            )

            # Step 3 – Validate input data
            if not name:
                self._err('Full name is required.')
                return render_template('customer/profile.html', user=user)

            # Step 4 – Save the search history (persist updated fields)
            self._run(
                "UPDATE users SET name=%s, phone=%s, address=%s, city=%s, avatar=%s "
                "WHERE id=%s",
                (name, phone, address, city, avatar, self._current_user_id()),
            )

            # Keep session name in sync
            session['name'] = name

            self._ok('Profile updated!')
            return redirect(url_for('customer.profile'))

        return render_template('customer/profile.html', user=user)

# ── Singleton ─────────────────────────────────────────────────────────────────
customer_controller = CustomerController()