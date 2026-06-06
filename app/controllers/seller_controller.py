"""
Sprint 2 - Seller Controller
US 4.1 Register Store | US 4.3 Manage Products
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.controllers.base_controller import BaseController
from app.models import StoreModel, ProductModel, CategoryModel


class SellerController(BaseController):

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_store(self) -> dict | None:
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

    # ── US 4.1 Register Store ─────────────────────────────────────────────────

    def setup(self):
        if self._get_store():
            return redirect(url_for('seller.dashboard'))

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
            self._ok('Store created successfully!')
            return redirect(url_for('seller.dashboard'))

        return render_template('seller/setup.html')

    def dashboard(self):
        store, redir = self._require_store()
        if redir:
            return redir

        sid = store['id']

        total_sales = self._q(
            """SELECT COALESCE(SUM(oi.subtotal),0) AS t FROM order_items oi
               JOIN orders o ON o.id=oi.order_id WHERE oi.store_id=%s AND o.payment_status='paid'""",
            (sid,), one=True
        )['t']

        total_orders = self._q(
            "SELECT COUNT(DISTINCT order_id) AS c FROM order_items WHERE store_id=%s", (sid,), one=True
        )['c']

        total_products = self._q(
            "SELECT COUNT(*) AS c FROM products WHERE store_id=%s AND is_active=1", (sid,), one=True
        )['c']

        low_stock = self._q(
            "SELECT * FROM products WHERE store_id=%s AND is_active=1 AND stock_qty <= low_stock_threshold ORDER BY stock_qty ASC LIMIT 5",
            (sid,)
        )

        top_products = self._q(
            """SELECT p.name, COALESCE(SUM(oi.quantity),0) AS sold,
                      COALESCE(SUM(oi.subtotal),0) AS revenue
               FROM products p LEFT JOIN order_items oi ON oi.product_id=p.id
               WHERE p.store_id=%s GROUP BY p.id ORDER BY sold DESC LIMIT 5""",
            (sid,)
        )

        monthly = self._q(
            """SELECT DATE_FORMAT(o.created_at,'%%Y-%%m') AS month,
                      COALESCE(SUM(oi.subtotal),0) AS revenue
               FROM order_items oi JOIN orders o ON o.id=oi.order_id
               WHERE oi.store_id=%s AND o.created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
               GROUP BY month ORDER BY month""",
            (sid,)
        )

        recent_orders = self._q(
            """SELECT DISTINCT o.* FROM orders o JOIN order_items oi ON oi.order_id=o.id
               WHERE oi.store_id=%s ORDER BY o.created_at DESC LIMIT 5""",
            (sid,)
        )

        return render_template('seller/dashboard.html',
                               store=store,
                               total_sales=total_sales,
                               total_orders=total_orders,
                               total_products=total_products,
                               low_stock=low_stock,
                               top_products=top_products,
                               monthly=monthly,
                               recent_orders=recent_orders)

    # ── US 4.3 Manage Products ────────────────────────────────────────────────

    def products(self):
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
        store, redir = self._require_store()
        if redir:
            return redir
        ProductModel.soft_delete(pid)
        self._info('Product removed.')
        return redirect(url_for('seller.products'))

    # ── Inventory ─────────────────────────────────────────────────────────────

    def inventory(self):
        store, redir = self._require_store()
        if redir:
            return redir
        prods = ProductModel.find_where(
            "store_id = %s AND is_active = 1 ORDER BY stock_qty ASC", (store['id'],)
        )
        return render_template('seller/inventory.html', products=prods, store=store)

    def inventory_update(self, pid: int):
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

    # ── Orders ────────────────────────────────────────────────────────────────

    def orders(self):
        store, redir = self._require_store()
        if redir:
            return redir
        ords = self._q("""
            SELECT DISTINCT o.*, u.name AS customer_name
            FROM   orders o
            JOIN   order_items oi ON oi.order_id = o.id
            JOIN   users u        ON u.id = o.user_id
            WHERE  oi.store_id = %s
            ORDER  BY o.created_at DESC
        """, (store['id'],))
        return render_template('seller/orders.html', orders=ords, store=store)

    def order_detail(self, oid: int):
        store, redir = self._require_store()
        if redir:
            return redir
        order = self._q(
            "SELECT o.*, u.name AS customer_name FROM orders o JOIN users u ON u.id = o.user_id WHERE o.id = %s",
            (oid,), one=True
        )
        if not order:
            self._err('Order not found.')
            return redirect(url_for('seller.orders'))
        items = self._q("""
            SELECT oi.*, pi.image_path FROM order_items oi
            LEFT JOIN product_images pi ON pi.product_id = oi.product_id AND pi.is_primary = 1
            WHERE oi.order_id = %s AND oi.store_id = %s
        """, (oid, store['id']))
        return render_template('seller/order_detail.html', order=order, items=items, store=store)

    def order_status(self, oid: int):
        store, redir = self._require_store()
        if redir:
            return redir
        status = request.form.get('status')
        self._run("UPDATE orders SET status = %s WHERE id = %s", (status, oid))
        self._ok('Order status updated.')
        return redirect(url_for('seller.order_detail', oid=oid))

    # ── Categories ────────────────────────────────────────────────────────────

    def categories(self):
        store, redir = self._require_store()
        if redir:
            return redir
        cats = CategoryModel.find_all()
        return render_template('seller/categories.html', cats=cats, store=store)

    # ── Reviews ───────────────────────────────────────────────────────────────

    def reviews(self):
        store, redir = self._require_store()
        if redir:
            return redir
        reviews = self._q("""
            SELECT r.*, u.name AS customer_name, p.name AS product_name
            FROM   reviews r
            JOIN   users    u ON u.id = r.user_id
            JOIN   products p ON p.id = r.product_id
            WHERE  p.store_id = %s
            ORDER  BY r.created_at DESC
        """, (store['id'],))
        return render_template('seller/reviews.html', reviews=reviews, store=store)

    # ── Chats ─────────────────────────────────────────────────────────────────

    def chats(self):
        store, redir = self._require_store()
        if redir:
            return redir
        return render_template('seller/chats.html', store=store)

    # ── Store Profile & Customize ─────────────────────────────────────────────

    def store_profile(self):
        store, redir = self._require_store()
        if redir:
            return redir
        if request.method == 'POST':
            name   = request.form.get('name', '').strip()
            desc   = request.form.get('description', '').strip()
            logo   = self._save_file(request.files.get('logo'), 'logos') or store['logo']
            banner = self._save_file(request.files.get('banner'), 'banners') or store['banner']
            self._run(
                "UPDATE stores SET name=%s, description=%s, logo=%s, banner=%s WHERE id=%s",
                (name, desc, logo, banner, store['id'])
            )
            self._ok('Store profile updated!')
            return redirect(url_for('seller.store_profile'))
        return render_template('seller/store_profile.html', store=store)

    def store_customize(self):
        store, redir = self._require_store()
        if redir:
            return redir
        if request.method == 'POST':
            primary_color = request.form.get('primary_color', '')
            banner_text   = request.form.get('banner_text', '')
            self._run(
                "UPDATE stores SET primary_color=%s, banner_text=%s WHERE id=%s",
                (primary_color, banner_text, store['id'])
            )
            self._ok('Store customized!')
            return redirect(url_for('seller.store_customize'))
        return render_template('seller/store_customize.html', store=store)

    # ── Chat Detail ───────────────────────────────────────────────────────────

    def chat_detail(self, chat_id: int):
        store, redir = self._require_store()
        if redir:
            return redir
        chat = self._q(
            "SELECT * FROM chats WHERE id=%s AND seller_id=%s",
            (chat_id, self._current_user_id()), one=True
        )
        if not chat:
            self._err('Chat not found.')
            return redirect(url_for('seller.chats'))
        messages = self._q(
            """SELECT cm.*, u.name FROM chat_messages cm
               JOIN users u ON u.id = cm.sender_id
               WHERE cm.chat_id = %s ORDER BY cm.created_at""",
            (chat_id,)
        )
        return render_template('seller/chat_detail.html',
                               chat=chat, messages=messages, store=store)

    # ── Order Update (alias for order_status) ────────────────────────────────

    def order_update(self, oid: int):
        return self.order_status(oid)


# ── Singleton ─────────────────────────────────────────────────────────────────
seller_controller = SellerController()