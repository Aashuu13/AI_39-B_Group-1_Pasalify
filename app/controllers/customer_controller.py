"""
Sprint 2 - US 2.2: View Product
CustomerController keeps only the methods needed for the View Product feature.
"""

from flask import render_template, request, redirect, url_for, session, flash

from app.controllers.base_controller import BaseController
from app.models import ProductModel, CategoryModel, ReviewModel
from app import db


class CustomerController(BaseController):

    # ── US 2.1 Browse Products (needed to navigate to a product) ─────────────

    def home(self):
        """Landing page — shows featured products to click into."""
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
        """Product listing — click any product to view its detail page."""
        q          = request.args.get('q', '')
        cat_slug   = request.args.get('cat', '')
        sort       = request.args.get('sort', 'newest')

        items = ProductModel.search(
            query=q,
            cat_slug=cat_slug,
            sort=sort,
        )
        cats = CategoryModel.find_all()
        return render_template(
            'customer/products.html',
            items=items, cats=cats,
            q=q, cat_slug=cat_slug, sort=sort,
        )

    # ── US 2.2 View Product (core feature) ───────────────────────────────────

    def product_detail(self, pid: int):
        """
        US 2.2 - View Product.
        Acceptance Criteria:
          1. Click on the desired product.
          2. Show the product information and details.
          3. Display the availability status of the product.
          4. Load all relevant product data.
          5. Provide a back navigation system to return to the previous page.
        """
        p = ProductModel.get_with_images(pid)
        if not p:
            self._err('Product not found.')
            return redirect(url_for('customer.products'))

        # AC 4: Load all relevant product data — images, reviews, related products
        images = self._q(
            "SELECT * FROM product_images WHERE product_id = %s ORDER BY is_primary DESC",
            (pid,)
        )

        reviews = ReviewModel.find_by_product(pid, approved_only=True)

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
            p=p, images=images, related=related, reviews=reviews,
        )

    # ── Review submission (form is on product_detail page) ───────────────────

    def submit_review(self, pid: int):
        """Submit a review — form lives on the product detail page."""
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

    def handle(self, *args, **kwargs):
        raise NotImplementedError


# ── Singleton ─────────────────────────────────────────────────────────────────
customer_controller = CustomerController()
