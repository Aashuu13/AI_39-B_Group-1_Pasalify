"""
app/controllers/store_controller.py
================================================================
OOP concepts on display: INHERITANCE + ENCAPSULATION

    - Inheritance:   StoreController extends BaseController.
    - Encapsulation: _get_or_create_chat() hides the "look it up,
      otherwise insert it" logic so start_chat() never writes raw
      SQL itself — it just asks for a chat id.

Handles public store storefronts (browsing one seller's catalogue
without being logged in) and the chat flow that starts from a
store page.
"""

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

    # ── Private helpers (Encapsulation) ─────────────────────────────────────

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

    # ── Chat (started from a public store page, before login is required) ─

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


# ── Singleton instance imported by app/controllers/__init__.py and routes ──
store_controller = StoreController()
