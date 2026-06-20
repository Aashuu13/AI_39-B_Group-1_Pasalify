"""
Sprint 3 - Seller Controller
US 4.5 Manage Inventory | US 4.6 Manage Orders | US 2.6 Seller Chat
(Builds on Sprint 1+2: Store setup, Products, Reviews, Dashboard)
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.controllers.base_controller import BaseController
from app.models import StoreModel, ProductModel, CategoryModel

class SellerController(BaseController):

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
            """SELECT DISTINCT o.*, u.name AS customer_name FROM orders o
               JOIN order_items oi ON oi.order_id=o.id
               JOIN users u ON u.id=o.user_id
               WHERE oi.store_id=%s ORDER BY o.created_at DESC LIMIT 5""",
            (sid,)
        )

        pending_reviews = self._q(
            """SELECT COUNT(*) AS c FROM reviews r
               JOIN products p ON p.id=r.product_id
               WHERE p.store_id=%s AND r.is_approved=0""",
            (sid,), one=True
        )['c']

        return render_template('seller/dashboard.html',
                               store=store,
                               total_sales=total_sales,
                               total_orders=total_orders,
                               total_products=total_products,
                               low_stock=low_stock,
                               top_products=top_products,
                               monthly=monthly,
                               recent_orders=recent_orders,
                               pending_reviews=pending_reviews)

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

    def inventory(self):
        store, redir = self._require_store()
        if redir:
            return redir

        filter_by = request.args.get('filter', 'all')
        base_sql  = "SELECT * FROM products WHERE store_id = %s AND is_active = 1"

        if filter_by == 'low':
            base_sql += " AND stock_qty <= low_stock_threshold"
        elif filter_by == 'out':
            base_sql += " AND stock_qty = 0"

        base_sql += " ORDER BY stock_qty ASC"
        prods = self._q(base_sql, (store['id'],))

        total_products  = self._q("SELECT COUNT(*) AS c FROM products WHERE store_id=%s AND is_active=1", (store['id'],), one=True)['c']
        low_stock_count = self._q("SELECT COUNT(*) AS c FROM products WHERE store_id=%s AND is_active=1 AND stock_qty <= low_stock_threshold AND stock_qty > 0", (store['id'],), one=True)['c']
        out_of_stock    = self._q("SELECT COUNT(*) AS c FROM products WHERE store_id=%s AND is_active=1 AND stock_qty=0", (store['id'],), one=True)['c']

        return render_template('seller/inventory.html',
                               products=prods, store=store,
                               filter_by=filter_by,
                               total_products=total_products,
                               low_stock_count=low_stock_count,
                               out_of_stock=out_of_stock)

    def inventory_update(self, pid: int):
        store, redir = self._require_store()
        if redir:
            return redir
        qty       = max(0, int(request.form.get('stock_qty', 0)))
        threshold = max(1, int(request.form.get('low_stock_threshold', 5)))
        self._run(
            "UPDATE products SET stock_qty=%s, low_stock_threshold=%s WHERE id=%s AND store_id=%s",
            (qty, threshold, pid, store['id'])
        )
        self._ok('Stock updated!')
        return redirect(url_for('seller.inventory'))

    def inventory_bulk_update(self):
        """US 4.5 - Bulk stock update from inventory page."""
        store, redir = self._require_store()
        if redir:
            return redir

        product_ids = request.form.getlist('product_id')
        for pid in product_ids:
            qty = request.form.get(f'stock_{pid}', 0)
            try:
                self._run(
                    "UPDATE products SET stock_qty=%s WHERE id=%s AND store_id=%s",
                    (int(qty), int(pid), store['id'])
                )
            except Exception:
                pass
        self._ok('Inventory updated!')
        return redirect(url_for('seller.inventory'))

    def orders(self):
        store, redir = self._require_store()
        if redir:
            return redir

        status_filter = request.args.get('status', '')

        sql = """
            SELECT DISTINCT o.*, u.name AS customer_name
            FROM   orders o
            JOIN   order_items oi ON oi.order_id = o.id
            JOIN   users u        ON u.id = o.user_id
            WHERE  oi.store_id = %s
        """
        args = [store['id']]
        if status_filter:
            sql += " AND o.status = %s"
            args.append(status_filter)
        sql += " ORDER BY o.created_at DESC"

        ords = self._q(sql, tuple(args))

        status_counts = self._q("""
            SELECT o.status, COUNT(DISTINCT o.id) AS cnt
            FROM orders o JOIN order_items oi ON oi.order_id=o.id
            WHERE oi.store_id=%s GROUP BY o.status
        """, (store['id'],))
        counts = {r['status']: r['cnt'] for r in status_counts}

        return render_template('seller/orders.html',
                               orders=ords, store=store,
                               status_filter=status_filter,
                               counts=counts)

    def order_detail(self, oid: int):
        store, redir = self._require_store()
        if redir:
            return redir
        order = self._q(
            "SELECT o.*, u.name AS customer_name, u.phone AS customer_phone FROM orders o JOIN users u ON u.id = o.user_id WHERE o.id = %s",
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
        note   = request.form.get('note', '').strip()

        valid_statuses = ['confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered', 'cancelled']
        if status not in valid_statuses:
            self._err('Invalid status.')
            return redirect(url_for('seller.order_detail', oid=oid))

        self._run("UPDATE orders SET status = %s WHERE id = %s", (status, oid))
        self._log('order_status_updated', 'order', oid)

        order = self._q("SELECT user_id, order_number FROM orders WHERE id=%s", (oid,), one=True)
        if order:
            self._notify(
                order['user_id'],
                f'Order {order["order_number"]} Update',
                f'Your order status has been updated to: {status.replace("_", " ").title()}',
                'order',
                f'/customer/order/{oid}'
            )

        self._ok('Order status updated.')
        return redirect(url_for('seller.order_detail', oid=oid))

    def categories(self):
        store, redir = self._require_store()
        if redir:
            return redir
        cats = CategoryModel.find_all()
        return render_template('seller/categories.html', cats=cats, store=store)

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

    def chats(self):
        store, redir = self._require_store()
        if redir:
            return redir
        uid   = self._current_user_id()
        chats = self._q("""
            SELECT c.*, u.name AS customer_name,
                   (SELECT message FROM chat_messages WHERE chat_id=c.id ORDER BY created_at DESC LIMIT 1) AS last_message,
                   (SELECT COUNT(*) FROM chat_messages WHERE chat_id=c.id AND sender_id != %s AND is_read=0) AS unread_count
            FROM chats c
            JOIN users u ON u.id = c.customer_id
            WHERE c.seller_id = %s
            ORDER BY c.created_at DESC
        """, (uid, uid))
        return render_template('seller/chats.html', chats=chats, store=store)

    def chat_detail(self, chat_id: int):
        store, redir = self._require_store()
        if redir:
            return redir
        uid  = self._current_user_id()
        chat = self._q(
            """SELECT c.*, u.name AS customer_name FROM chats c
               JOIN users u ON u.id=c.customer_id
               WHERE c.id=%s AND c.seller_id=%s""",
            (chat_id, uid), one=True
        )
        if not chat:
            self._err('Chat not found.')
            return redirect(url_for('seller.chats'))

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
            return redirect(url_for('seller.chat_detail', chat_id=chat_id))

        return render_template('seller/chat_detail.html',
                               chat=chat, messages=messages, store=store)

    def send_message(self, chat_id: int):
        """POST-only send message endpoint."""
        return self.chat_detail(chat_id)

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


    def order_update(self, oid: int):
        return self.order_status(oid)
    
    def store_customize(self):
       store, redir = self._require_store()
       if redir:
          return redir

       if request.method == 'POST':
          StoreModel.update(store['id'], {
            'theme_color':  request.form.get('theme_color', '#6C3FC8'),
            'theme_layout': request.form.get('theme_layout', 'grid'),
          })
          self._ok('Store design saved!')
          return redirect(url_for('seller.store_customize'))

       return render_template('seller/store_customize.html', store=store)

seller_controller = SellerController()
