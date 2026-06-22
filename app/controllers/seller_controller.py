"""
app/controllers/seller_controller.py
================================================================
OOP concepts on display: INHERITANCE + ENCAPSULATION + POLYMORPHISM

    - Inheritance:   SellerController extends BaseController and
      gets _save_file, _ok/_err, _q/_run, _log, _notify for free.
    - Encapsulation: _get_store() hides the store lookup, and
      _require_store() hides the "redirect to setup if no store
      yet" guard, so every seller-only action is protected with
      just one line instead of repeating the same check everywhere.
    - Polymorphism:  product_add() and product_edit() both lean on
      the same _parse_product_form() helper and produce a similar
      shape of result, even though one inserts a new row and the
      other updates an existing one.

Handles all seller-facing pages: store setup, dashboard, store
profile/customization, products, categories, inventory, orders,
reviews, chat, and support tickets.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.controllers.base_controller import BaseController
from app.models import (
    StoreModel, ProductModel, CategoryModel,
    OrderModel, ReviewModel, NotificationModel
)
from app import db


class SellerController(BaseController):
    """
    Handles all seller-facing views:
    setup, dashboard, store profile, products, inventory,
    orders, reviews, chat.

    Inherited from BaseController:
        _save_file, _ok/_err/_warn/_info, _q/_run, _log, _notify,
        _current_user_id, _is_logged_in
    """
# ── Private helpers (Encapsulation) ─────────────────────────────────────

    def _get_store(self) -> dict | None:
        """Return the current seller's store row, or None if they
        haven't created one yet."""
        return StoreModel.find_by_user(self._current_user_id())

    def _require_store(self):
        """
        Look up the seller's store; if it doesn't exist yet, return a
        redirect to the setup wizard instead. Every method below that
        needs a store calls this exact same line:

            store, redir = self._require_store()
            if redir:
                return redir

        so the "no store yet" guard is written once, not in every method.
        """
        store = self._get_store()
        if not store:
            return None, redirect(url_for('seller.setup'))
        return store, None

    def _parse_product_form(self) -> dict:
        """
        Pull the product fields out of request.form and coerce them
        to the right types (float price, int stock, etc.) with sane
        defaults. Both product_add() and product_edit() call this so
        the type-casting rules only live in one place.
        """
        return {
            'name':                request.form.get('name', ''),
            'description':         request.form.get('description', ''),
            'price':               float(request.form.get('price', 0)),
            'compare_price':       request.form.get('compare_price') or None,
            'category_id':         request.form.get('category_id') or None,
            'stock_qty':           int(request.form.get('stock_qty', 0)),
            'low_stock_threshold': int(request.form.get('low_stock_threshold', 5)),
            'sku':                 request.form.get('sku', ''),
        }

    def _save_product_images(self, product_id: int, files, first_is_primary: bool = True):
        """Save every uploaded image file and insert a product_images
        row for each one. The first image becomes the "primary" (cover)
        image unless first_is_primary is explicitly turned off — used
        when editing a product that already has a primary image set."""
        for i, f in enumerate(files):
            path = self._save_file(f, 'products')
            if path:
                self._run(
                    "INSERT INTO product_images (product_id, image_path, is_primary) VALUES (%s,%s,%s)",
                    (product_id, path, 1 if (i == 0 and first_is_primary) else 0)
                )

    # ── Setup ───────────────────────────────────────────────────────────────

    def setup(self):
        """One-time wizard: create the store for a brand-new seller.
        Sellers who already have a store skip straight to the dashboard."""
        if self._get_store():
            return redirect(url_for('seller.dashboard'))

        if request.method == 'POST':
            name   = request.form.get('name', '').strip()
            desc   = request.form.get('description', '').strip()
            logo   = self._save_file(request.files.get('logo'), 'logos')
            banner = self._save_file(request.files.get('banner'), 'banners')

            sid = StoreModel.create({
                'user_id':     self._current_user_id(),
                'name':        name,
                'description': desc,
                'logo':        logo,
                'banner':      banner,
                'is_approved': 1,
            })
            self._log('store_created', 'store', sid)
            self._ok('Store created successfully!')
            return redirect(url_for('seller.dashboard'))

        return render_template('seller/setup.html')

    # ── Dashboard ───────────────────────────────────────────────────────────

    def dashboard(self):
        """Seller's home page: revenue/order/product totals, low-stock
        warnings, recent orders, a 6-month revenue trend, and a top-5
        best-selling products list."""
        store, redir = self._require_store()
        if redir:
            return redir

        stats        = StoreModel.stats(store['id'])
        low_stock    = ProductModel.low_stock(store['id'])
        recent_orders = OrderModel.find_by_store(store['id'], limit=5)
        monthly      = OrderModel.monthly_revenue(store['id'])
        top_products = self._q("""
            SELECT p.name, SUM(oi.quantity) AS sold, SUM(oi.subtotal) AS revenue
            FROM order_items oi JOIN products p ON p.id = oi.product_id
            WHERE oi.store_id = %s GROUP BY p.id ORDER BY sold DESC LIMIT 5
        """, (store['id'],))

        return render_template('seller/dashboard.html', store=store,
                               total_sales=stats['total_sales'],
                               total_orders=stats['total_orders'],
                               total_products=stats['total_products'],
                               low_stock=low_stock,
                               recent_orders=recent_orders,
                               monthly=monthly,
                               top_products=top_products)

    # ── Store profile & customization ───────────────────────────────────────

    def store_profile(self):
        """Edit basic store info (name, description, logo, banner)."""
        store, redir = self._require_store()
        if redir:
            return redir

        if request.method == 'POST':
            # Keep the old logo/banner if no new file was chosen
            logo   = self._save_file(request.files.get('logo'), 'logos')   or store['logo']
            banner = self._save_file(request.files.get('banner'), 'banners') or store['banner']
            StoreModel.update(store['id'], {
                'name':        request.form.get('name', ''),
                'description': request.form.get('description', ''),
                'logo':        logo,
                'banner':      banner,
            })
            self._ok('Store profile updated!')
            return redirect(url_for('seller.store_profile'))

        return render_template('seller/store_profile.html', store=store)

    # ── Products ────────────────────────────────────────────────────────────

    def products(self):
        """List every product this seller's store has (active or not)."""
        store, redir = self._require_store()
        if redir:
            return redir

        prods = self._q("""
            SELECT p.*, pi.image_path, c.name AS cat_name
            FROM products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.store_id = %s ORDER BY p.created_at DESC
        """, (store['id'],))
        return render_template('seller/products.html', products=prods, store=store)

    def product_add(self):
        """
        GET  -> show the empty product form.
        POST -> create the product, save any uploaded images, and
                go back to the product list.
        """
        store, redir = self._require_store()
        if redir:
            return redir
        cats = CategoryModel.find_all()

        if request.method == 'POST':
            data = self._parse_product_form()
            slug = data['name'].lower().replace(' ', '-')
            pid  = ProductModel.create({
                'store_id':            store['id'],
                'category_id':         data['category_id'],
                'name':                data['name'],
                'slug':                slug,
                'description':         data['description'],
                'price':               data['price'],
                'compare_price':       data['compare_price'],
                'sku':                 data['sku'],
                'stock_qty':           data['stock_qty'],
                'low_stock_threshold': data['low_stock_threshold'],
                'is_approved':         1,
                'is_active':           1,
            })
            self._save_product_images(pid, request.files.getlist('images'))
            self._log('product_added', 'product', pid)
            self._ok('Product added successfully!')
            return redirect(url_for('seller.products'))

        return render_template('seller/product_form.html', store=store,
                               cats=cats, product=None)

    def product_edit(self, pid: int):
        """
        GET  -> show the form pre-filled with the existing product's
                data and any images already uploaded.
        POST -> save the changes and add any newly uploaded images
                (without overwriting the existing primary image).
        """
        store, redir = self._require_store()
        if redir:
            return redir

        prod = ProductModel.find_where(
            "id = %s AND store_id = %s", (pid, store['id']), one=True
        )
        if not prod:
            self._err('Product not found.')
            return redirect(url_for('seller.products'))

        cats   = CategoryModel.find_all()
        images = self._q("SELECT * FROM product_images WHERE product_id = %s", (pid,))

        if request.method == 'POST':
            data = self._parse_product_form()
            ProductModel.update(pid, {
                'name':                data['name'],
                'description':         data['description'],
                'price':               data['price'],
                'compare_price':       data['compare_price'],
                'category_id':         data['category_id'],
                'stock_qty':           data['stock_qty'],
                'low_stock_threshold': data['low_stock_threshold'],
                'sku':                 data['sku'],
            })
            self._save_product_images(pid, request.files.getlist('images'),
                                       first_is_primary=False)
            self._ok('Product updated!')
            return redirect(url_for('seller.products'))

        return render_template('seller/product_form.html', store=store,
                               cats=cats, product=prod, images=images)

    def product_delete(self, pid: int):
        """Soft-delete: marks the product inactive instead of removing
        the row, so past orders that reference it still display fine."""
        store, redir = self._require_store()
        if redir:
            return redir
        ProductModel.soft_delete(pid)
        self._info('Product removed.')
        return redirect(url_for('seller.products'))

    # ── Categories ──────────────────────────────────────────────────────────

    def categories(self):
        """Read-only category browser for sellers (categories are
        managed by admins, see admin_controller.categories)."""
        cats = CategoryModel.find_all()
        return render_template('seller/categories.html', cats=cats)

    # ── Inventory ───────────────────────────────────────────────────────────

    def inventory(self):
        """Stock-focused product list, sorted lowest-stock-first so
        items that need restocking show up at the top."""
        store, redir = self._require_store()
        if redir:
            return redir
        prods = ProductModel.find_where(
            "store_id = %s AND is_active = 1 ORDER BY stock_qty ASC", (store['id'],)
        )
        return render_template('seller/inventory.html', products=prods, store=store)

    def inventory_update(self, pid: int):
        """Manually set a product's stock count (e.g. after a physical
        recount). Never allows a negative quantity."""
        store, redir = self._require_store()
        if redir:
            return redir
        qty = max(0, int(request.form.get('stock_qty', 0)))
        self._run(
            "UPDATE products SET stock_qty = %s WHERE id = %s AND store_id = %s",
            (qty, pid, store['id'])
        )
        self._ok('Stock updated!')
        return redirect(url_for('seller.inventory'))

    # ── Orders ──────────────────────────────────────────────────────────────

    def orders(self):
        """All orders that include at least one item from this store,
        with the items concatenated into one readable string per row."""
        store, redir = self._require_store()
        if redir:
            return redir
        ords = self._q("""
            SELECT o.*, GROUP_CONCAT(oi.product_name SEPARATOR ', ') AS items,
                   SUM(oi.subtotal) AS store_total
            FROM orders o JOIN order_items oi ON oi.order_id = o.id
            WHERE oi.store_id = %s GROUP BY o.id ORDER BY o.created_at DESC
        """, (store['id'],))
        return render_template('seller/orders.html', orders=ords, store=store)

    def order_update(self, oid: int):
        """Move an order to its next status (confirmed -> processing ->
        shipped -> delivered, or cancelled) and notify the buyer."""
        status = request.form.get('status')
        valid  = ('confirmed', 'processing', 'shipped', 'delivered', 'cancelled')
        if status in valid:
            OrderModel.update(oid, {'status': status})
            order = OrderModel.find_by_id(oid)
            if order:
                self._notify(
                    order['user_id'], 'Order Updated',
                    f'Your order {order["order_number"]} is now: {status.upper()}',
                    'order', url_for('customer.order_detail', oid=oid)
                )
            self._ok('Order status updated.')
        return redirect(url_for('seller.orders'))

    # ── Reviews ─────────────────────────────────────────────────────────────

    def reviews(self):
        """Every review left on any product from this store."""
        store, redir = self._require_store()
        if redir:
            return redir
        revs = self._q("""
            SELECT r.*, p.name AS product_name, u.name AS user_name
            FROM reviews r
            JOIN products p ON p.id = r.product_id
            JOIN users u ON u.id = r.user_id
            WHERE p.store_id = %s ORDER BY r.created_at DESC
        """, (store['id'],))
        return render_template('seller/reviews.html', reviews=revs, store=store)

    # ── Chat (seller side of customer<->seller messaging) ──────────────────

    def chats(self):
        """List of this seller's conversations with customers, each with
        a message preview and unread count."""
        store, redir = self._require_store()
        if redir:
            return redir
        convs = self._q("""
            SELECT ch.*, u.name AS customer_name,
                   (SELECT message FROM chat_messages WHERE chat_id=ch.id
                    ORDER BY created_at DESC LIMIT 1) AS last_msg,
                   (SELECT COUNT(*) FROM chat_messages
                    WHERE chat_id=ch.id AND is_read=0 AND sender_id!=ch.seller_id) AS unread
            FROM chats ch JOIN users u ON u.id = ch.customer_id
            WHERE ch.seller_id = %s ORDER BY ch.created_at DESC
        """, (self._current_user_id(),))
        return render_template('seller/chats.html', convs=convs, store=store)

    def chat_detail(self, cid: int):
        """
        GET  -> show the full thread with one customer and mark their
                messages as read.
        POST -> send a new message into the conversation.
        """
        chat = self._q(
            "SELECT * FROM chats WHERE id = %s AND seller_id = %s",
            (cid, self._current_user_id()), one=True
        )
        if not chat:
            self._err('Not found.')
            return redirect(url_for('seller.chats'))

        if request.method == 'POST':
            msg = request.form.get('message', '').strip()
            if msg:
                self._run(
                    "INSERT INTO chat_messages (chat_id, sender_id, message) VALUES (%s,%s,%s)",
                    (cid, self._current_user_id(), msg)
                )
            return redirect(url_for('seller.chat_detail', cid=cid))

        msgs     = self._q("""
            SELECT cm.*, u.name FROM chat_messages cm
            JOIN users u ON u.id = cm.sender_id
            WHERE cm.chat_id = %s ORDER BY cm.created_at
        """, (cid,))
        customer = self._q("SELECT name FROM users WHERE id = %s",
                            (chat['customer_id'],), one=True)
        self._run(
            "UPDATE chat_messages SET is_read=1 WHERE chat_id=%s AND sender_id!=%s",
            (cid, self._current_user_id())
        )
        store = self._get_store()
        return render_template('seller/chat_detail.html', chat=chat,
                               msgs=msgs, customer=customer, store=store)

    # ── Support tickets (customers asking the chatbot, escalated here) ─────

    def support_tickets(self):
        """
        Build one "ticket" per customer who has both (a) messaged the
        support chatbot, and (b) ordered something from this store —
        sellers should only see support threads relevant to their own
        buyers, not the whole platform's support inbox (that's the
        admin view in admin_controller.support_tickets).

        Encapsulation: the grouping-by-customer logic lives entirely
        here; the template just loops over the finished `tickets` list.
        """
        store, redir = self._require_store()
        if redir:
            return redir
        users = self._q("""
            SELECT DISTINCT sm.user_id, u.name AS customer_name, u.email AS customer_email,
                   MAX(sm.created_at) AS last_message
            FROM support_messages sm
            LEFT JOIN users u ON u.id = sm.user_id
            WHERE sm.role = 'user'
            AND EXISTS (
                SELECT 1 FROM orders o
                JOIN order_items oi ON oi.order_id = o.id
                JOIN products p ON p.id = oi.product_id
                WHERE o.user_id = sm.user_id AND p.store_id = %s
            )
            GROUP BY sm.user_id, u.name, u.email
            ORDER BY last_message DESC
        """, (store['id'],))
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
        return render_template('seller/support.html', tickets=tickets, store=store)

    def support_reply(self):
        """
        Reply to a customer's support thread from the seller side.
        Finds (or starts) a direct chat with that customer and drops
        the reply in there, so the conversation continues in the
        regular chat UI rather than a separate "support" inbox.
        """
        store, redir = self._require_store()
        if redir:
            return redir
        customer_id = request.form.get('customer_id', type=int)
        message     = request.form.get('message', '').strip()
        if not message or not customer_id:
            self._err('Reply cannot be empty.')
            return redirect(url_for('seller.support_tickets'))
        chat = self._q(
            "SELECT * FROM chats WHERE customer_id = %s AND seller_id = %s",
            (customer_id, self._current_user_id()), one=True
        )
        cid = chat['id'] if chat else self._run(
            "INSERT INTO chats (customer_id, seller_id) VALUES (%s,%s)",
            (customer_id, self._current_user_id())
        )
        self._run(
            "INSERT INTO chat_messages (chat_id, sender_id, message) VALUES (%s,%s,%s)",
            (cid, self._current_user_id(), message)
        )
        self._notify(customer_id, 'New message from seller',
                     f'{store["name"]} replied to your support question.', 'system')
        self._ok('Message sent to customer.')
        return redirect(url_for('seller.chat_detail', cid=cid))


# ── Singleton instance imported by app/controllers/__init__.py and routes ──
seller_controller = SellerController()
