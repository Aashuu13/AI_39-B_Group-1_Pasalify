"""
==============================================================
OOP Concept: INHERITANCE & ENCAPSULATION (Customer Controller)
==============================================================
- Inheritance: CustomerController extends BaseController.
- Encapsulation: Promo-code validation, checkout logic,
  and cart upsert are all private methods — the route layer
  calls one public method and never sees the internals.
- Polymorphism: cart_add / cart_update / cart_remove all
  operate on the same cart table but behave differently.
==============================================================
"""

import uuid
from datetime import datetime

from flask import render_template, request, redirect, url_for, session, flash, jsonify

from app.controllers.base_controller import BaseController
from app.models import UserModel, ProductModel, CategoryModel, OrderModel
from app import db

class CustomerController(BaseController):

    def _get_cart_items(self) -> list[dict]:
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

        reviews = self._q("""
            SELECT r.*, u.name AS reviewer_name
            FROM   reviews r
            JOIN   users   u ON u.id = r.user_id
            WHERE  r.product_id = %s AND r.is_approved = 1
            ORDER  BY r.created_at DESC
        """, (pid,))

        user_reviewed = False
        if self._is_logged_in():
            existing = self._q(
                "SELECT id FROM reviews WHERE product_id=%s AND user_id=%s",
                (pid, self._current_user_id()), one=True
            )
            user_reviewed = bool(existing)

        return render_template(
            'customer/product_detail.html',
            p=p, images=images, related=related,
            reviews=reviews, user_reviewed=user_reviewed,
        )

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

    def wishlist(self):
        items = self._q("""
            SELECT w.id, p.*, pi.image_path, s.name AS store_name
            FROM   wishlists w
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
            "SELECT id FROM wishlists WHERE user_id = %s AND product_id = %s",
            (uid, pid), one=True,
        )
        if existing:
            self._run("DELETE FROM wishlists WHERE id = %s", (existing['id'],))
            self._info('Removed from wishlist.')
        else:
            self._run(
                "INSERT INTO wishlists (user_id, product_id) VALUES (%s, %s)",
                (uid, pid),
            )
            self._ok('Added to wishlist!')
        return redirect(request.referrer or url_for('customer.wishlist'))

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

    def apply_promo(self):
        """AJAX endpoint: validate promo code and return discount info."""
        code     = request.json.get('code', '').strip().upper()
        subtotal = float(request.json.get('subtotal', 0))

        promo = self._q(
            """SELECT * FROM promo_codes
               WHERE code = %s AND is_active = 1
                 AND (valid_until IS NULL OR valid_until >= CURDATE())
                 AND (valid_from IS NULL OR valid_from <= CURDATE())
                 AND (max_uses IS NULL OR used_count < max_uses)""",
            (code,), one=True
        )

        if not promo:
            return jsonify({'valid': False, 'message': 'Invalid or expired promo code.'})

        if float(promo['min_order']) > subtotal:
            return jsonify({
                'valid': False,
                'message': f"Minimum order of Rs {promo['min_order']} required."
            })

        if promo['discount_type'] == 'percent':
            discount = subtotal * float(promo['discount_value']) / 100
        else:
            discount = float(promo['discount_value'])

        discount = min(discount, subtotal)
        return jsonify({
            'valid':       True,
            'promo_id':    promo['id'],
            'code':        code,
            'discount':    round(discount, 2),
            'final_total': round(subtotal - discount, 2),
            'message':     f"Promo applied! You save Rs {discount:.2f}",
        })

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
        uid        = self._current_user_id()
        method     = request.form.get('payment_method', 'cod')
        order_no   = self._generate_order_number()
        promo_id   = request.form.get('promo_code_id') or None
        promo_code = request.form.get('promo_code', '') or None
        discount   = float(request.form.get('discount_amount', 0))
        final_total = subtotal - discount

        if promo_id:
            self._run(
                "UPDATE promo_codes SET used_count = used_count + 1 WHERE id = %s",
                (promo_id,)
            )

        oid = self._run("""
            INSERT INTO orders
              (user_id, order_number, full_name, phone, address, city,
               total_amount, discount_amount, promo_code_id, promo_code,
               payment_method, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'placed')
        """, (
            uid,
            order_no,
            request.form.get('full_name', ''),
            request.form.get('phone', ''),
            request.form.get('address', ''),
            request.form.get('city', ''),
            final_total,
            discount,
            promo_id,
            promo_code,
            method,
        ))

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

        self._run("DELETE FROM cart_items WHERE user_id = %s", (uid,))

        pay_status = 'success' if method == 'cod' else 'pending'
        self._run(
            "INSERT INTO payments (order_id, user_id, amount, method, status) VALUES (%s, %s, %s, %s, %s)",
            (oid, uid, final_total, method, pay_status),
        )

        self._notify(uid, 'Order Placed!',
                     f'Your order {order_no} has been placed successfully.',
                     'order', f'/customer/order/{oid}')

        self._ok(f'Order {order_no} placed successfully!')
        return redirect(url_for('customer.order_detail', oid=oid))

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

        status_steps = ['placed', 'confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered']
        current_step = order['status'] if order['status'] in status_steps else 'placed'

        return render_template('customer/order_detail.html',
                               order=order, items=items,
                               status_steps=status_steps,
                               current_step=current_step)

    def order_cancel(self, oid: int):
        """US 3.2 - Customer can cancel order if still 'placed'."""
        order = self._q(
            "SELECT * FROM orders WHERE id = %s AND user_id = %s",
            (oid, self._current_user_id()), one=True
        )
        if not order:
            self._err('Order not found.')
            return redirect(url_for('customer.orders'))

        if order['status'] != 'placed':
            self._warn('Order cannot be cancelled at this stage.')
            return redirect(url_for('customer.order_detail', oid=oid))

        self._run("UPDATE orders SET status='cancelled' WHERE id=%s", (oid,))

        items = self._q("SELECT * FROM order_items WHERE order_id=%s", (oid,))
        for item in items:
            self._run(
                "UPDATE products SET stock_qty = stock_qty + %s WHERE id = %s",
                (item['quantity'], item['product_id'])
            )
        self._ok('Order cancelled.')
        return redirect(url_for('customer.order_detail', oid=oid))

    def support(self):
        return render_template('customer/support.html')

    def profile(self):
        user = self._q("SELECT * FROM users WHERE id = %s",
                       (self._current_user_id(),), one=True)
        if not user:
            return redirect(url_for('auth.login'))
        if request.method == 'POST':
            name    = request.form.get('name', '').strip()
            phone   = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            city    = request.form.get('city', '').strip()
            avatar  = self._save_file(request.files.get('avatar'), 'images') or user.get('avatar')

            self._run(
                "UPDATE users SET name=%s, phone=%s, address=%s, city=%s, avatar=%s WHERE id=%s",
                (name, phone, address, city, avatar, self._current_user_id())
            )
            session['name'] = name
            self._ok('Profile updated!')
            return redirect(url_for('customer.profile'))
        return render_template('customer/profile.html', user=user)

    

    def payment_history(self):
        payments = self._q("""
            SELECT p.*, o.order_number FROM payments p
            JOIN orders o ON o.id = p.order_id
            WHERE p.user_id = %s ORDER BY p.created_at DESC
        """, (self._current_user_id(),))
        return render_template('customer/payment_history.html', payments=payments)

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

            self._run("""
                UPDATE products SET
                    avg_rating = (SELECT AVG(rating) FROM reviews WHERE product_id=%s AND is_approved=1),
                    review_count = (SELECT COUNT(*) FROM reviews WHERE product_id=%s AND is_approved=1)
                WHERE id=%s
            """, (pid, pid, pid))
            self._ok('Review submitted!')
        except Exception:
            self._err('Could not submit review.')
        return redirect(url_for('customer.product_detail', pid=pid))

    def start_chat(self, seller_id: int):
        """Start or resume a chat with a seller."""
        uid    = self._current_user_id()
        pid    = request.args.get('product_id')

        existing = self._q(
            "SELECT id FROM chats WHERE customer_id=%s AND seller_id=%s",
            (uid, seller_id), one=True
        )
        if existing:
            chat_id = existing['id']
        else:
            chat_id = self._run(
                "INSERT INTO chats (customer_id, seller_id, product_id) VALUES (%s,%s,%s)",
                (uid, seller_id, pid)
            )

        return redirect(url_for('customer.chat_detail', chat_id=chat_id))

    def my_chats(self):
        """List all chats for current customer."""
        uid = self._current_user_id()
        chats = self._q("""
            SELECT c.*, u.name AS seller_name, s.name AS store_name,
                   (SELECT message FROM chat_messages WHERE chat_id=c.id ORDER BY created_at DESC LIMIT 1) AS last_message,
                   (SELECT COUNT(*) FROM chat_messages WHERE chat_id=c.id AND sender_id != %s AND is_read=0) AS unread_count
            FROM chats c
            JOIN users u ON u.id = c.seller_id
            LEFT JOIN stores s ON s.user_id = c.seller_id
            WHERE c.customer_id = %s
            ORDER BY c.created_at DESC
        """, (uid, uid))
        return render_template('customer/chats.html', chats=chats)

    def chat_detail(self, chat_id: int):
        uid  = self._current_user_id()
        chat = self._q(
            "SELECT c.*, u.name AS other_name FROM chats c JOIN users u ON u.id=c.seller_id WHERE c.id=%s AND c.customer_id=%s",
            (chat_id, uid), one=True
        )
        if not chat:
            self._err('Chat not found.')
            return redirect(url_for('customer.my_chats'))

        messages = self._q(
            """SELECT cm.*, u.name AS sender_name FROM chat_messages cm
               JOIN users u ON u.id = cm.sender_id
               WHERE cm.chat_id = %s ORDER BY cm.created_at""",
            (chat_id,)
        )

        self._run(
            "UPDATE chat_messages SET is_read=1 WHERE chat_id=%s AND sender_id != %s",
            (chat_id, uid)
        )

        if request.method == 'POST':
            msg = request.form.get('message', '').strip()
            if msg:
                self._run(
                    "INSERT INTO chat_messages (chat_id, sender_id, message) VALUES (%s,%s,%s)",
                    (chat_id, uid, msg)
                )
            return redirect(url_for('customer.chat_detail', chat_id=chat_id))

        return render_template('customer/chat_detail.html', chat=chat, messages=messages)

    def store_page(self, slug: str):
        return self.store_detail(slug)
    
    def notifications(self):
        uid    = self._current_user_id()
        notifs = self._q(
            "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 50",
            (uid,)
        )
        self._run("UPDATE notifications SET is_read = 1 WHERE user_id = %s", (uid,))
        return render_template('customer/notifications.html', notifs=notifs)

    def notif_count(self):
        c = self._q(
            "SELECT COUNT(*) AS c FROM notifications WHERE user_id = %s AND is_read = 0",
            (self._current_user_id(),), one=True
        )
        return jsonify({'count': c['c']})

    

customer_controller = CustomerController()
