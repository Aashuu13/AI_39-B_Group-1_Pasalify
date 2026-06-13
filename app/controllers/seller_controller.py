"""
==============================================================
MY FEATURES – Seller Controller
Sprint 3: US 2.6 – Seller Chat (seller side)
Sprint 4: US 4.4 – Organize Products (products CRUD + categories)
==============================================================
"""

from flask import render_template, request, redirect, url_for, session

from app.controllers.base_controller import BaseController
from app.models import StoreModel, ProductModel, CategoryModel, OrderModel


class SellerController(BaseController):

    # ── Private Helpers ───────────────────────────────────────────────────────

    def _get_store(self):
        return StoreModel.find_by_user(self._current_user_id())

    def _require_store(self):
        store = self._get_store()
        if not store:
            return None, redirect(url_for('seller.setup'))
        return store, None

    def _parse_product_form(self) -> dict:
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
        for i, f in enumerate(files):
            path = self._save_file(f, 'products')
            if path:
                self._run(
                    "INSERT INTO product_images (product_id, image_path, is_primary) VALUES (%s,%s,%s)",
                    (product_id, path, 1 if (i == 0 and first_is_primary) else 0)
                )

    # ── Minimal setup / dashboard stubs ──────────────────────────────────────

    def setup(self):
        """Create a store (needed before seller can use any seller features)."""
        if self._get_store():
            return redirect(url_for('seller.products'))
        if request.method == 'POST':
            name   = request.form.get('name', '').strip()
            desc   = request.form.get('description', '').strip()
            slug   = StoreModel.make_unique_slug(name)
            logo   = self._save_file(request.files.get('logo'), 'logos')
            banner = self._save_file(request.files.get('banner'), 'banners')
            sid = StoreModel.create({
                'user_id':     self._current_user_id(),
                'name':        name,
                'slug':        slug,
                'description': desc,
                'logo':        logo,
                'banner':      banner,
                'is_approved': 1,
            })
            self._log('store_created', 'store', sid)
            self._ok('Store created!')
            return redirect(url_for('seller.products'))
        return render_template('seller/setup.html')

    def dashboard(self):
        """Minimal dashboard redirect to products."""
        return redirect(url_for('seller.products'))

    # ── Sprint 4: US 4.4 – Organize Products ─────────────────────────────────

    def products(self):
        """
        Sprint 4 – US 4.4: Organize Products
        Lists all seller's products with category and stock info.
        Sellers can filter, sort, and navigate to add/edit/delete.
        """
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
        cats = CategoryModel.find_all()
        return render_template('seller/products.html', products=prods, store=store, cats=cats)

    def product_add(self):
        """Sprint 4 – US 4.4: Add a new product to the store."""
        store, redir = self._require_store()
        if redir:
            return redir
        cats = CategoryModel.find_all()

        if request.method == 'POST':
            data = self._parse_product_form()
            if not data['name']:
                self._err('Product name is required.')
                return render_template('seller/product_form.html', store=store, cats=cats, product=None)

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

        return render_template('seller/product_form.html', store=store, cats=cats, product=None)

    def product_edit(self, pid: int):
        """Sprint 4 – US 4.4: Edit an existing product (name, category, price, stock, etc.)."""
        store, redir = self._require_store()
        if redir:
            return redir

        prod = ProductModel.find_where("id = %s AND store_id = %s", (pid, store['id']), one=True)
        if not prod:
            self._err('Product not found.')
            return redirect(url_for('seller.products'))

        cats   = CategoryModel.find_all()
        images = self._q("SELECT * FROM product_images WHERE product_id = %s", (pid,))

        if request.method == 'POST':
            data = self._parse_product_form()
            if not data['name']:
                self._err('Product name is required.')
                return render_template('seller/product_form.html', store=store, cats=cats,
                                       product=prod, images=images)

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
            self._save_product_images(pid, request.files.getlist('images'), first_is_primary=False)
            self._ok('Product updated!')
            return redirect(url_for('seller.products'))

        return render_template('seller/product_form.html', store=store,
                               cats=cats, product=prod, images=images)

    def product_delete(self, pid: int):
        """Sprint 4 – US 4.4: Soft-delete (deactivate) a product."""
        store, redir = self._require_store()
        if redir:
            return redir
        ProductModel.soft_delete(pid)
        self._info('Product removed.')
        return redirect(url_for('seller.products'))

    def categories(self):
        """Sprint 4 – US 4.4: View available categories for organizing products."""
        cats = CategoryModel.find_all()
        return render_template('seller/categories.html', cats=cats)

    # ── Sprint 3: US 2.6 – Seller Chat (Seller side) ─────────────────────────

    def chats(self):
        """Sprint 3 – US 2.6: List all chat conversations from customers."""
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
        Sprint 3 – US 2.6: View and reply to a customer chat.
        GET  → show full message thread.
        POST → send a reply.
        """
        chat = self._q(
            "SELECT * FROM chats WHERE id = %s AND seller_id = %s",
            (cid, self._current_user_id()), one=True
        )
        if not chat:
            self._err('Chat not found.')
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
        customer = self._q(
            "SELECT name FROM users WHERE id = %s", (chat['customer_id'],), one=True
        )
        self._run(
            "UPDATE chat_messages SET is_read=1 WHERE chat_id=%s AND sender_id!=%s",
            (cid, self._current_user_id())
        )
        store = self._get_store()
        return render_template('seller/chat_detail.html', chat=chat,
                               msgs=msgs, customer=customer, store=store)


# Singleton
seller_controller = SellerController()
