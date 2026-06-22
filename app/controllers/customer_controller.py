"""
app/controllers/customer_controller.py
Yubraj's features: view product (Sprint 2), edit customer profile (Sprint 3),
customer chat (Sprint 3), store browsing (Sprint 5).
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify

from app.controllers.base_controller import BaseController
from app.models import (
    UserModel, ProductModel, CategoryModel,
    ReviewModel
)
from app import db


class CustomerController(BaseController):

    # ── Home / Discovery ─────────────────────────────────────────────────────

    def home(self):
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

    # ── Profile (Sprint 3 - edit customer UI) ───────────────────────────────

    def profile(self):
        uid  = self._current_user_id()
        user = UserModel.find_by_id(uid)

        if request.method == 'POST':
            UserModel.update(uid, {
                'name':    request.form.get('name', '').strip(),
                'phone':   request.form.get('phone', '').strip(),
                'address': request.form.get('address', '').strip(),
                'city':    request.form.get('city', '').strip(),
            })
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

    # ── Stores (Sprint 5 - store URL) ───────────────────────────────────────

    def stores(self):
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

    # ── Chat - Sprint 3 (customer side) ─────────────────────────────────────

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

    # ── Stubs needed by other parts of the app (notifications, support) ─────

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

    def support(self):
        user_id = self._current_user_id()
        history = self._q(
            "SELECT * FROM support_messages WHERE user_id = %s ORDER BY created_at ASC",
            (user_id,)
        ) if user_id else []
        return render_template('customer/support.html', history=history)

    def support_chat(self):
        msg     = request.form.get('message', '').strip().lower()
        user_id = self._current_user_id()
        faqs    = {
            'order':   'You can track your orders in Profile → My Orders.',
            'payment': 'We accept COD, eSewa and Khalti.',
            'return':  'Returns accepted within 7 days.',
            'cancel':  'To cancel an order, go to My Orders and click Cancel.',
            'account': 'Manage your account under Profile → Settings.',
            'seller':  'Interested in selling? Register as a seller!',
            'promo':   'Enter your promo code at checkout.',
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


customer_controller = CustomerController()
