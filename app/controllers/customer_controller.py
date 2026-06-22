<<<<<<< HEAD
=======
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
>>>>>>> origin/aayushma

import uuid
from datetime import datetime

from flask import render_template, request, redirect, url_for, session, flash, jsonify

from app.controllers.base_controller import BaseController
from app.models import (
    UserModel, ProductModel, CategoryModel,
    OrderModel, NotificationModel, ReviewModel
)
from app import db

<<<<<<< HEAD
class CustomerController(BaseController):
    """
    Handles all customer-facing views:
    home, products, product_detail, cart, wishlist,
    checkout, orders, reviews, profile, notifications, chat.

    Inherited from BaseController:
=======

class CustomerController(BaseController):
    """
    Handles all customer-facing views:
    home, products, product_detail, cart, wishlist,
    checkout, orders, reviews, profile, notifications, chat.

    Inherits from BaseController:
>>>>>>> origin/aayushma
        _ok/_err/_warn/_info, _q/_run, _log, _notify,
        _current_user_id, _is_logged_in
    """

<<<<<<< HEAD
    def _validate_promo(self, code: str, subtotal: float) -> dict:
        """
        Check a promo code against the cart subtotal and, if it's
        valid, mark one use against it.

        Returns a dict shaped like:
            {'valid': bool, 'discount': float, 'promo_id': int|None,
             'message': str}
        so callers (checkout() and the AJAX validate_promo() endpoint)
        both get a consistent result to work with.
=======
    # ── Private Helpers (Encapsulation) ───────────────────────────────────────

    def _validate_promo(self, code: str, subtotal: float) -> dict:
        """
        Validate a promo code against the current subtotal.
        Returns {'valid': bool, 'discount': float, 'promo_id': int|None,
                  'message': str}
        Encapsulation: all promo logic lives here.
>>>>>>> origin/aayushma
        """
        if not code:
            return {'valid': False, 'discount': 0, 'promo_id': None, 'message': ''}

        pc = self._q("""
            SELECT * FROM promo_codes
            WHERE code = %s AND is_active = 1
              AND (valid_until IS NULL OR valid_until >= CURDATE())
        """, (code,), one=True)

        if not pc or (pc['max_uses'] and pc['used_count'] >= pc['max_uses']):
            return {'valid': False, 'discount': 0, 'promo_id': None,
                    'message': 'Invalid or expired promo code.'}

        if subtotal < float(pc['min_order']):
            return {'valid': False, 'discount': 0, 'promo_id': None,
                    'message': f"Minimum order Rs.{pc['min_order']} required."}

        if pc['discount_type'] == 'percent':
            discount = round(subtotal * float(pc['discount_value']) / 100, 2)
        else:
            discount = float(pc['discount_value'])

        self._run("UPDATE promo_codes SET used_count = used_count + 1 WHERE id = %s",
                  (pc['id'],))
        return {'valid': True, 'discount': discount, 'promo_id': pc['id'],
                'message': f"Code applied! Rs.{discount:.2f} off."}

    def _cart_items(self) -> list[dict]:
<<<<<<< HEAD
        """Return the logged-in user's cart rows joined with product,
        image, and store info — everything the cart/checkout pages need
        in a single query."""
=======
        """Return the current user's cart with product info."""
>>>>>>> origin/aayushma
        return self._q("""
            SELECT ci.*, p.name, p.price, p.stock_qty, pi.image_path,
                   s.name AS store_name, p.store_id
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN stores s ON s.id = p.store_id
            WHERE ci.user_id = %s
        """, (self._current_user_id(),))

<<<<<<< HEAD
=======
    # ── Home / Discovery ──────────────────────────────────────────────────────

>>>>>>> origin/aayushma
    def home(self):
        """Landing page: category pills + the 12 newest approved products."""
        cats = CategoryModel.find_all()
        featured = self._q("""
            SELECT p.*, pi.image_path, s.name AS store_name, s.slug AS store_slug
            FROM products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN stores s ON s.id = p.store_id
            WHERE p.is_active = 1 AND p.is_approved = 1
            ORDER BY p.created_at DESC LIMIT 12
        """)
        return render_template('customer/home.html', cats=cats, featured=featured)

    def products(self):
<<<<<<< HEAD
        """Product catalogue with search/filter/sort, all delegated to
        ProductModel.search() so this method just reads query params."""
=======
>>>>>>> origin/aayushma
        items = ProductModel.search(
            query=request.args.get('q', ''),
            cat_slug=request.args.get('cat', ''),
            min_price=request.args.get('min_price', ''),
            max_price=request.args.get('max_price', ''),
            sort=request.args.get('sort', 'newest'),
            min_rating=request.args.get('rating', ''),
        )
        cats = CategoryModel.find_all()
        return render_template('customer/products.html', items=items, cats=cats,
                               q=request.args.get('q', ''),
                               cat_slug=request.args.get('cat', ''),
                               sort=request.args.get('sort', 'newest'))

    def product_detail(self, pid: int):
        """Single product page: images, reviews, related products from the
        same category, and whether it's already on the viewer's wishlist."""
        p = ProductModel.get_with_images(pid)
        if not p:
            self._err('Product not found.')
            return redirect(url_for('customer.products'))

        images  = self._q("SELECT * FROM product_images WHERE product_id = %s ORDER BY is_primary DESC", (pid,))
        reviews = ReviewModel.find_by_product(pid)
        related = self._q("""
            SELECT p2.*, pi.image_path FROM products p2
            LEFT JOIN product_images pi ON pi.product_id = p2.id AND pi.is_primary = 1
            WHERE p2.category_id = %s AND p2.id != %s
              AND p2.is_active = 1 AND p2.is_approved = 1 LIMIT 4
        """, (p['category_id'], pid))
        in_wish = False
        if self._is_logged_in():
            in_wish = bool(self._q(
                "SELECT id FROM wishlists WHERE user_id = %s AND product_id = %s",
                (self._current_user_id(), pid), one=True
            ))
        return render_template('customer/product_detail.html', p=p, images=images,
                               reviews=reviews, related=related, in_wish=in_wish)

<<<<<<< HEAD
    def cart(self):
        """Show the cart and its running total."""
=======
    # ── Cart ─────────────────────────────────────────────────────────────────

    def cart(self):
>>>>>>> origin/aayushma
        items = self._cart_items()
        total = sum(i['price'] * i['quantity'] for i in items)
        return render_template('customer/cart.html', items=items, total=total)

    def cart_add(self, pid: int):
<<<<<<< HEAD
        """
        Add a product to the cart, or bump its quantity if it's
        already in there (an "upsert": one INSERT path, one UPDATE path).
        """
=======
>>>>>>> origin/aayushma
        qty = int(request.form.get('quantity', 1))
        p   = ProductModel.find_by_id(pid)
        if not p or p['stock_qty'] < qty:
            self._err('Not enough stock.')
            return redirect(request.referrer or url_for('customer.products'))

<<<<<<< HEAD
=======
        # Encapsulation: upsert logic in one place
>>>>>>> origin/aayushma
        existing = self._q(
            "SELECT id, quantity FROM cart_items WHERE user_id = %s AND product_id = %s",
            (self._current_user_id(), pid), one=True
        )
        if existing:
            self._run("UPDATE cart_items SET quantity = quantity + %s WHERE id = %s",
                      (qty, existing['id']))
        else:
            self._run("INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s,%s,%s)",
                      (self._current_user_id(), pid, qty))
        self._ok('Added to cart!')
        return redirect(request.referrer or url_for('customer.cart'))

    def cart_update(self, cid: int):
<<<<<<< HEAD
        """Set an exact quantity for one cart row; dropping to 0 deletes it."""
=======
>>>>>>> origin/aayushma
        qty = int(request.form.get('quantity', 1))
        if qty < 1:
            self._run("DELETE FROM cart_items WHERE id = %s AND user_id = %s",
                      (cid, self._current_user_id()))
        else:
            self._run("UPDATE cart_items SET quantity = %s WHERE id = %s AND user_id = %s",
                      (qty, cid, self._current_user_id()))
        return redirect(url_for('customer.cart'))

    def cart_remove(self, cid: int):
<<<<<<< HEAD
        """Remove a single line item from the cart."""
=======
>>>>>>> origin/aayushma
        self._run("DELETE FROM cart_items WHERE id = %s AND user_id = %s",
                  (cid, self._current_user_id()))
        self._info('Item removed.')
        return redirect(url_for('customer.cart'))
<<<<<<< HEAD
=======

    # ── Wishlist ──────────────────────────────────────────────────────────────
>>>>>>> origin/aayushma

    def wishlist(self):
        """Show every product the user has saved to their wishlist."""
        items = self._q("""
            SELECT p.*, pi.image_path, s.name AS store_name
            FROM wishlists w JOIN products p ON p.id = w.product_id
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN stores s ON s.id = p.store_id
            WHERE w.user_id = %s
        """, (self._current_user_id(),))
        return render_template('customer/wishlist.html', items=items)

    def wishlist_toggle(self, pid: int):
        """Add or remove a product from the wishlist with a single
        button — checks current state, then does the opposite."""
        uid      = self._current_user_id()
        existing = self._q(
            "SELECT id FROM wishlists WHERE user_id = %s AND product_id = %s",
            (uid, pid), one=True
        )
        if existing:
            self._run("DELETE FROM wishlists WHERE id = %s", (existing['id'],))
            self._info('Removed from wishlist.')
        else:
            self._run("INSERT IGNORE INTO wishlists (user_id, product_id) VALUES (%s,%s)",
                      (uid, pid))
            self._ok('Added to wishlist!')
        return redirect(request.referrer or url_for('customer.wishlist'))

<<<<<<< HEAD
    def checkout(self):
        """
        GET  -> show the checkout form with the cart summary.
        POST -> create the order, its line items, decrement stock,
                record the seller commission per item, clear the
                cart, log the payment, and notify the buyer.
        """
=======
    # ── Checkout ─────────────────────────────────────────────────────────────

    def checkout(self):
>>>>>>> origin/aayushma
        items = self._cart_items()
        if not items:
            self._warn('Your cart is empty.')
            return redirect(url_for('customer.cart'))

        subtotal = sum(float(i['price']) * i['quantity'] for i in items)
        user     = UserModel.find_by_id(self._current_user_id())

        if request.method == 'POST':
            uid       = self._current_user_id()
            full_name = request.form.get('full_name', '')
            phone     = request.form.get('phone', '')
            address   = request.form.get('address', '')
            city      = request.form.get('city', '')
            method    = request.form.get('payment_method', 'cod')

<<<<<<< HEAD
=======
            # Encapsulation: promo validation in one call
>>>>>>> origin/aayushma
            promo_code = request.form.get('promo_code', '').strip().upper()
            promo      = self._validate_promo(promo_code, subtotal)
            if promo_code and not promo['valid']:
                self._err(promo['message'])
            if promo_code and promo['valid']:
                self._ok(promo['message'])

            total    = max(0, subtotal - promo['discount'])
            order_no = 'ORD-' + datetime.now().strftime('%Y%m%d') + '-' + str(uuid.uuid4())[:6].upper()

            oid = self._run("""
                INSERT INTO orders
                  (user_id, order_number, full_name, phone, address, city,
                   total_amount, discount_amount, promo_code_id,
                   payment_method, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'placed')
            """, (uid, order_no, full_name, phone, address, city,
                  total, promo['discount'], promo['promo_id'], method))

            for i in items:
                price = float(i['price'])
                self._run("""
                    INSERT INTO order_items
                      (order_id, product_id, store_id, product_name, price, quantity, subtotal)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (oid, i['product_id'], i['store_id'], i['name'],
                      price, i['quantity'], price * i['quantity']))

<<<<<<< HEAD
                ProductModel.decrement_stock(i['product_id'], i['quantity'])

=======
                # Decrement stock (Encapsulation: inside ProductModel)
                ProductModel.decrement_stock(i['product_id'], i['quantity'])

                # Commission calculation
>>>>>>> origin/aayushma
                store = self._q(
                    "SELECT id, commission_rate FROM stores WHERE id = %s",
                    (i['store_id'],), one=True
                )
                if store:
                    comm       = round(price * i['quantity'] * float(store['commission_rate']) / 100, 2)
                    seller_amt = round(price * i['quantity'] - comm, 2)
                    oi         = self._q(
                        "SELECT id FROM order_items WHERE order_id = %s AND product_id = %s",
                        (oid, i['product_id']), one=True
                    )
                    if oi:
                        self._run("""
                            INSERT INTO commissions
                              (order_item_id, store_id, seller_amount, platform_amount)
                            VALUES (%s,%s,%s,%s)
                        """, (oi['id'], i['store_id'], seller_amt, comm))

<<<<<<< HEAD
=======
            # Clear cart & record payment
>>>>>>> origin/aayushma
            self._run("DELETE FROM cart_items WHERE user_id = %s", (uid,))
            pay_status = 'success' if method == 'cod' else 'pending'
            self._run(
                "INSERT INTO payments (order_id, user_id, amount, method, status) VALUES (%s,%s,%s,%s,%s)",
                (oid, uid, total, method, pay_status)
            )
            self._notify(uid, 'Order Placed!',
                         f'Your order {order_no} has been placed successfully.',
                         'order', url_for('customer.order_detail', oid=oid))
            self._ok(f'Order {order_no} placed successfully!')
            return redirect(url_for('customer.order_detail', oid=oid))

        return render_template('customer/checkout.html', items=items,
                               subtotal=subtotal, user=user)

    def validate_promo(self):
<<<<<<< HEAD
        """AJAX endpoint behind the 'Apply' button on the checkout page —
        validates a promo code and returns just enough JSON to update
        the total on screen without a full page reload."""
=======
        """AJAX endpoint — validate a promo code and return JSON."""
>>>>>>> origin/aayushma
        code     = request.form.get('code', '').strip().upper()
        subtotal = float(request.form.get('subtotal', 0))
        result   = self._validate_promo(code, subtotal)
        return jsonify({'valid': result['valid'], 'discount': result['discount'],
                        'message': result['message']})
<<<<<<< HEAD
=======

    # ── Orders ────────────────────────────────────────────────────────────────
>>>>>>> origin/aayushma

    def orders(self):
        """List every order this customer has placed."""
        ords = self._q(
            "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC",
            (self._current_user_id(),)
        )
        return render_template('customer/orders.html', orders=ords)

    def order_detail(self, oid: int):
<<<<<<< HEAD
        """Single order's full details and line items.
        Scoped to user_id so customers can't view each other's orders
        just by guessing an order id in the URL."""
=======
>>>>>>> origin/aayushma
        order = self._q(
            "SELECT * FROM orders WHERE id = %s AND user_id = %s",
            (oid, self._current_user_id()), one=True
        )
        if not order:
            self._err('Order not found.')
            return redirect(url_for('customer.orders'))
        items = self._q("""
            SELECT oi.*, pi.image_path FROM order_items oi
            LEFT JOIN product_images pi ON pi.product_id = oi.product_id AND pi.is_primary = 1
            WHERE oi.order_id = %s
        """, (oid,))
        return render_template('customer/order_detail.html', order=order, items=items)

    def payment_history(self):
<<<<<<< HEAD
        """All payment records for this customer, newest first."""
=======
>>>>>>> origin/aayushma
        pays = self._q("""
            SELECT p.*, o.order_number FROM payments p
            JOIN orders o ON o.id = p.order_id
            WHERE p.user_id = %s ORDER BY p.created_at DESC
        """, (self._current_user_id(),))
        return render_template('customer/payment_history.html', pays=pays)
<<<<<<< HEAD
=======

    # ── Reviews ───────────────────────────────────────────────────────────────
>>>>>>> origin/aayushma

    def submit_review(self, pid: int):
        """
        Create or update this user's review for a product in one
        query (ON DUPLICATE KEY UPDATE relies on the unique
        (product_id, user_id) constraint in schema.sql), then
        recalculate the product's average rating.
        """
        rating = int(request.form.get('rating', 5))
        title  = request.form.get('title', '')
        body   = request.form.get('body', '')
        self._run("""
            INSERT INTO reviews (product_id, user_id, rating, title, body)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE rating=%s, title=%s, body=%s
        """, (pid, self._current_user_id(), rating, title, body, rating, title, body))
        ProductModel.update_rating(pid)
        self._ok('Review submitted!')
        return redirect(url_for('customer.product_detail', pid=pid))

<<<<<<< HEAD
    def profile(self):
        """
        GET  -> show the profile form pre-filled with current details,
                plus a couple of small stats (order count, wishlist count).
        POST -> save the edited fields.
        """
        uid  = self._current_user_id()
        user = UserModel.find_by_id(uid)

=======
    # ── Profile ───────────────────────────────────────────────────────────────

    def profile(self):
        uid  = self._current_user_id()
        user = UserModel.find_by_id(uid)

>>>>>>> origin/aayushma
        if request.method == 'POST':
            UserModel.update(uid, {
                'name':    request.form.get('name', '').strip(),
                'phone':   request.form.get('phone', '').strip(),
                'address': request.form.get('address', '').strip(),
                'city':    request.form.get('city', '').strip(),
            })
<<<<<<< HEAD

=======
>>>>>>> origin/aayushma
            session['name'] = request.form.get('name', '').strip()
            self._ok('Profile updated!')
            return redirect(url_for('customer.profile'))

        orders_count = self._q(
            "SELECT COUNT(*) AS c FROM orders WHERE user_id = %s", (uid,), one=True
        )
        wish_count = self._q(
            "SELECT COUNT(*) AS c FROM wishlists WHERE user_id = %s", (uid,), one=True
        )
        return render_template('customer/profile.html', user=user,
                               orders_count=orders_count['c'],
                               wish_count=wish_count['c'])

<<<<<<< HEAD
    def notifications(self):
        """Show the latest 50 notifications and mark them all as read
        the moment the user opens this page."""
=======
    # ── Notifications ─────────────────────────────────────────────────────────

    def notifications(self):
>>>>>>> origin/aayushma
        uid    = self._current_user_id()
        notifs = self._q(
            "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 50",
            (uid,)
        )
        self._run("UPDATE notifications SET is_read = 1 WHERE user_id = %s", (uid,))
        return render_template('customer/notifications.html', notifs=notifs)

    def notif_count(self):
<<<<<<< HEAD
        """JSON endpoint polled every 30s by pasalify.js to update the
        little red badge on the notification bell."""
=======
>>>>>>> origin/aayushma
        c = self._q(
            "SELECT COUNT(*) AS c FROM notifications WHERE user_id = %s AND is_read = 0",
            (self._current_user_id(),), one=True
        )
        return jsonify({'count': c['c']})

<<<<<<< HEAD
    def support(self):
        """Show the support chat page along with this user's previous
        bot conversation history (guests just see an empty history)."""
        user_id = self._current_user_id()
        history = self._q(
            "SELECT * FROM support_messages WHERE user_id = %s ORDER BY created_at ASC",
            (user_id,)
        ) if user_id else []
        return render_template('customer/support.html', history=history)

    def support_chat(self):
        """
        Very small keyword-matching FAQ bot: scans the user's message
        for known keywords and replies with the matching canned answer.
        Both the user's message and the bot's reply are saved to
        support_messages so a human (seller or admin) can later see the
        full thread and reply on the same conversation.
        """
=======
    # ── Support Chatbot ───────────────────────────────────────────────────────

    def support(self):
        return render_template('customer/support.html')

    def support_chat(self):
        """Simple keyword-based FAQ bot. Encapsulation: FAQ map is local."""
>>>>>>> origin/aayushma
        msg     = request.form.get('message', '').strip().lower()
        user_id = self._current_user_id()
        faqs    = {
            'order':   'You can track your orders in Profile → My Orders.',
            'payment': 'We accept COD, eSewa and Khalti. Issues? Email support@pasalify.com.',
            'return':  'Returns accepted within 7 days. Contact the seller or our support.',
            'cancel':  'To cancel an order, go to My Orders and click Cancel.',
            'account': 'Manage your account under Profile → Settings.',
            'seller':  'Interested in selling? Register as a seller and set up your store!',
            'promo':   'Enter your promo code at checkout in the "Promo Code" field.',
        }
        reply = "Sorry, I didn't understand that. Please email support@pasalify.com for help."
        for key, ans in faqs.items():
            if key in msg:
                reply = ans
                break
        self._run(
            "INSERT INTO support_messages (user_id, role, message) VALUES (%s,'user',%s)",
            (user_id, msg)
        )
        self._run(
            "INSERT INTO support_messages (user_id, role, message) VALUES (%s,'bot',%s)",
            (user_id, reply)
        )
        return jsonify({'reply': reply})

<<<<<<< HEAD
    def stores(self):
        """Directory of every approved store, with an optional name/
        description search."""
=======
    # ── Stores ────────────────────────────────────────────────────────────────

    def stores(self):
>>>>>>> origin/aayushma
        q = request.args.get('q', '')
        if q:
            results = self._q(
                "SELECT * FROM stores WHERE is_approved = 1 AND (name LIKE %s OR description LIKE %s)",
                (f'%{q}%', f'%{q}%')
            )
        else:
            results = self._q("SELECT * FROM stores WHERE is_approved = 1")
        return render_template('customer/store.html', stores=results, q=q)

    def store_page(self, slug: str):
<<<<<<< HEAD
        """Public-facing page for one store (its catalogue), reached
        from the store directory above."""
=======
>>>>>>> origin/aayushma
        store = self._q(
            "SELECT * FROM stores WHERE slug = %s AND is_approved = 1", (slug,), one=True
        )
        if not store:
            self._err('Store not found.')
            return redirect(url_for('customer.stores'))
        prods = self._q("""
            SELECT p.*, pi.image_path FROM products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            WHERE p.store_id = %s AND p.is_active = 1 AND p.is_approved = 1
            ORDER BY p.created_at DESC
        """, (store['id'],))
        return render_template('customer/store_page.html', store=store, products=prods)

<<<<<<< HEAD
    def chats(self):
        """List of this customer's conversations, each with the store's
        name/logo, the most recent message preview, and an unread count."""
        convs = self._q("""
            SELECT ch.*, s.name AS store_name, s.logo AS store_logo,
                   (SELECT message FROM chat_messages WHERE chat_id=ch.id
                    ORDER BY created_at DESC LIMIT 1) AS last_msg,
                   (SELECT COUNT(*) FROM chat_messages
                    WHERE chat_id=ch.id AND is_read=0 AND sender_id!=ch.customer_id) AS unread
            FROM chats ch JOIN stores s ON s.user_id = ch.seller_id
            WHERE ch.customer_id = %s ORDER BY ch.created_at DESC
        """, (self._current_user_id(),))
        return render_template('customer/chats.html', convs=convs)

    def chat_start(self, store_id: int):
        """Start (or resume) a chat with a store's seller, then jump
        straight into that conversation."""
=======
    # ── Chat ──────────────────────────────────────────────────────────────────

    def chats(self):
        convs = self._q("""
            SELECT ch.*, s.name AS store_name, s.logo AS store_logo,
                   (SELECT message FROM chat_messages WHERE chat_id=ch.id
                    ORDER BY created_at DESC LIMIT 1) AS last_msg,
                   (SELECT COUNT(*) FROM chat_messages
                    WHERE chat_id=ch.id AND is_read=0 AND sender_id!=ch.customer_id) AS unread
            FROM chats ch JOIN stores s ON s.user_id = ch.seller_id
            WHERE ch.customer_id = %s ORDER BY ch.created_at DESC
        """, (self._current_user_id(),))
        return render_template('customer/chats.html', convs=convs)

    def chat_start(self, store_id: int):
>>>>>>> origin/aayushma
        store = self._q("SELECT * FROM stores WHERE id = %s", (store_id,), one=True)
        if not store:
            self._err('Store not found.')
            return redirect(url_for('customer.home'))
        uid  = self._current_user_id()
        chat = self._q(
            "SELECT * FROM chats WHERE customer_id = %s AND seller_id = %s",
            (uid, store['user_id']), one=True
        )
        cid = chat['id'] if chat else self._run(
            "INSERT INTO chats (customer_id, seller_id) VALUES (%s,%s)",
            (uid, store['user_id'])
        )
        return redirect(url_for('customer.chat_detail', cid=cid))

    def chat_detail(self, cid: int):
<<<<<<< HEAD
        """
        GET  -> show the full message thread, then mark the seller's
                messages as read since the customer is viewing them now.
        POST -> send a new message into this conversation.
        """
=======
>>>>>>> origin/aayushma
        uid  = self._current_user_id()
        chat = self._q(
            "SELECT * FROM chats WHERE id = %s AND customer_id = %s", (cid, uid), one=True
        )
        if not chat:
            self._err('Not found.')
            return redirect(url_for('customer.chats'))

        if request.method == 'POST':
            msg = request.form.get('message', '').strip()
            if msg:
                self._run(
                    "INSERT INTO chat_messages (chat_id, sender_id, message) VALUES (%s,%s,%s)",
                    (cid, uid, msg)
                )
            return redirect(url_for('customer.chat_detail', cid=cid))

        msgs  = self._q("""
            SELECT cm.*, u.name FROM chat_messages cm
            JOIN users u ON u.id = cm.sender_id
            WHERE cm.chat_id = %s ORDER BY cm.created_at
        """, (cid,))
        store = self._q("SELECT * FROM stores WHERE user_id = %s",
                         (chat['seller_id'],), one=True)
        self._run(
            "UPDATE chat_messages SET is_read=1 WHERE chat_id=%s AND sender_id!=%s",
            (cid, uid)
        )
        return render_template('customer/chat_detail.html', chat=chat,
                               msgs=msgs, store=store)
<<<<<<< HEAD
=======

>>>>>>> origin/aayushma

# ── Singleton instance ────────────────────────────────────────────────────────
customer_controller = CustomerController()