
from flask import render_template, request, redirect, url_for, session, flash

from app.controllers.base_controller import BaseController
from app.models import StoreModel

class StoreController(BaseController):
    """
    Handles public store pages and customer-seller chat
    initiated from the store page.

    Inherited from BaseController:
        _ok/_err/_warn/_info, _q/_run, _log, _notify,
        _current_user_id, _is_logged_in
    """

    def _get_or_create_chat(self, customer_id: int, seller_id: int,
                            product_id: int | None = None) -> int:
        """
        Return the id of an existing chat between this customer and
        seller, or create a new one and return its id. Callers always
        just get an int back — they never see the SELECT/INSERT logic.
        """
        existing = self._q(
            "SELECT id FROM chats WHERE customer_id = %s AND seller_id = %s",
            (customer_id, seller_id), one=True
        )
        if existing:
            return existing['id']
        return self._run(
            "INSERT INTO chats (customer_id, seller_id, product_id) VALUES (%s,%s,%s)",
            (customer_id, seller_id, product_id)
        )

    def public_store(self, slug: str):
        """
        Storefront for one seller, reached via /store/<slug>. Supports
        the same search/category/sort filters as the main product
        catalogue, but scoped to just this store's products.
        """
        store = self._q(
            "SELECT * FROM stores WHERE slug = %s AND is_approved = 1 AND is_active = 1",
            (slug,), one=True
        )
        if not store:
            self._warn('Store not found or not yet approved.')
            return redirect(url_for('customer.home'))

        q    = request.args.get('q', '')
        cat  = request.args.get('cat', '')
        sort = request.args.get('sort', 'newest')

        sql  = """
            SELECT p.*, pi.image_path, c.name AS cat_name
            FROM products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.store_id = %s AND p.is_active = 1 AND p.is_approved = 1
        """
        args = [store['id']]
        if q:
            sql += " AND p.name LIKE %s"; args.append(f'%{q}%')
        if cat:
            sql += " AND c.slug = %s"; args.append(cat)

        order_map = {
            'newest':     'p.created_at DESC',
            'price_asc':  'p.price ASC',
            'price_desc': 'p.price DESC',
        }
        sql += f" ORDER BY {order_map.get(sort, 'p.created_at DESC')}"

        prods = self._q(sql, args)
        cats  = self._q("""
            SELECT DISTINCT c.* FROM categories c
            JOIN products p ON p.category_id = c.id
            WHERE p.store_id = %s AND p.is_active = 1
        """, (store['id'],))
        owner = self._q("SELECT name FROM users WHERE id = %s",
                         (store['user_id'],), one=True)
        reviews_avg = self._q("""
            SELECT AVG(r.rating) AS avg, COUNT(*) AS cnt
            FROM reviews r JOIN products p ON p.id = r.product_id
            WHERE p.store_id = %s
        """, (store['id'],), one=True)

        return render_template('store/public.html', store=store, products=prods,
                               cats=cats, owner=owner, q=q, sort=sort,
                               reviews_avg=reviews_avg)

    def store_product(self, slug: str, pid: int):
        """A store-scoped product URL just forwards to the main product
        detail page — kept simple rather than duplicating that view."""
        return redirect(url_for('customer.product_detail', pid=pid))

    def start_chat(self, seller_id: int):
        """Begin a chat with a seller from their storefront. Guests are
        sent to log in first since a chat needs a real user_id."""
        if not self._is_logged_in():
            self._warn('Login to chat with seller.')
            return redirect(url_for('auth.login'))

        product_id = request.form.get('product_id')
        cid = self._get_or_create_chat(
            self._current_user_id(), seller_id,
            int(product_id) if product_id else None
        )
        return redirect(url_for('store.chat_view', cid=cid))

    def chat_view(self, cid: int):
        """
        GET  -> show the conversation and mark the seller's messages
                as read.
        POST -> send a new message into the conversation.
        """
        if not self._is_logged_in():
            return redirect(url_for('auth.login'))

        chat = self._q(
            "SELECT * FROM chats WHERE id = %s AND customer_id = %s",
            (cid, self._current_user_id()), one=True
        )
        if not chat:
            self._err('Chat not found.')
            return redirect(url_for('customer.home'))

        if request.method == 'POST':
            msg = request.form.get('message', '').strip()
            if msg:
                self._run(
                    "INSERT INTO chat_messages (chat_id, sender_id, message) VALUES (%s,%s,%s)",
                    (cid, self._current_user_id(), msg)
                )
            return redirect(url_for('store.chat_view', cid=cid))

        msgs = self._q("""
            SELECT cm.*, u.name FROM chat_messages cm
            JOIN users u ON u.id = cm.sender_id
            WHERE cm.chat_id = %s ORDER BY cm.created_at
        """, (cid,))
        seller = self._q("""
            SELECT u.name, s.name AS store_name FROM users u
            JOIN stores s ON s.user_id = u.id WHERE u.id = %s
        """, (chat['seller_id'],), one=True)

        self._run(
            "UPDATE chat_messages SET is_read=1 WHERE chat_id=%s AND sender_id!=%s",
            (cid, self._current_user_id())
        )
        return render_template('store/chat.html', chat=chat,
                               msgs=msgs, seller=seller)

store_controller = StoreController()
