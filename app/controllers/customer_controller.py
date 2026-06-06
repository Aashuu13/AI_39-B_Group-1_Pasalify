"""
=============================================================
OOP Concepts: INHERITANCE, POLYMORPHISM, ENCAPSULATION
               (CustomerController)
=============================================================
Inheritance  — CustomerController extends BaseController;
               _ok, _err, _q, _current_user_id inherited free.
Polymorphism — products() calls ProductModel.search() which
               builds different SQL for every filter combo.
Encapsulation— SQL logic hidden in Models; controller
               only reads request args and renders templates.
=============================================================
Sprint 2 | US 2.1 – Search Products  | Developer: Yubraj KC
Sprint 3 | US 2.4 – Wishlist
          US 2.5 – Product Reviews
=============================================================
"""

from flask import render_template, request, redirect, url_for

from app.controllers.base_controller import BaseController
from app.models import ProductModel, CategoryModel, WishlistModel, ReviewModel


class CustomerController(BaseController):

    # ── US 2.1  Search Products ───────────────────────────────────────────────

    def products(self):
        """
        US 2.1 — Search Products.

        AC 1: /customer/products shows the search bar.
        AC 2: 'q' param is the keyword typed by the user.
        AC 3: cat, min_price, max_price, rating, sort apply filters.
        AC 4: matching items rendered in products.html grid.
        AC 5: empty-state shown by template when items == [].

        Polymorphism: ProductModel.search() adapts its SQL
        to whichever filters are provided — same method call,
        different SQL each time.
        """
        q          = request.args.get('q',         '').strip()
        cat_slug   = request.args.get('cat',        '').strip()
        min_price  = request.args.get('min_price',  '').strip()
        max_price  = request.args.get('max_price',  '').strip()
        sort       = request.args.get('sort',       'newest')
        min_rating = request.args.get('rating',     '').strip()

        # Polymorphism: same method, different SQL based on filters
        items = ProductModel.search(
            query=q,
            cat_slug=cat_slug,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            min_rating=min_rating,
        )

        # Inheritance: CategoryModel.find_all() inherited from BaseModel
        cats = CategoryModel.find_all()

        return render_template(
            'customer/products.html',
            items=items,
            cats=cats,
            q=q,
            cat_slug=cat_slug,
            min_p=min_price,
            max_p=max_price,
            sort=sort,
            rating=min_rating,
            result_count=len(items),
        )

    # ── US 2.4  Wishlist ──────────────────────────────────────────────────────

    def wishlist(self):
        """
        US 2.4 — View Wishlist.
        Shows all products the logged-in customer has wishlisted.
        """
        uid   = self._current_user_id()
        items = WishlistModel.find_by_user(uid)
        return render_template('customer/wishlist.html', items=items)

    def wishlist_toggle(self, pid: int):
        """
        US 2.4 — Add / Remove from Wishlist.
        Toggles the wishlist entry for product `pid`.
        Encapsulation: toggle SQL is hidden in WishlistModel.
        """
        uid   = self._current_user_id()
        added = WishlistModel.toggle(uid, pid)
        if added:
            self._ok('Added to wishlist!')
        else:
            self._info('Removed from wishlist.')
        return redirect(request.referrer or url_for('customer.wishlist'))

    # ── US 2.5  Product Reviews ───────────────────────────────────────────────

    def product_detail(self, pid: int):
        """
        US 2.5 — Product detail page with reviews.
        Fetches the product, its reviews, and whether the current
        user has already reviewed it (to show/hide the review form).
        """
        p = ProductModel.find_by_id(pid)
        if not p:
            self._err('Product not found.')
            return redirect(url_for('customer.products'))

        reviews      = ReviewModel.find_by_product(pid)
        user_reviewed = False
        in_wish       = False

        if self._is_logged_in():
            uid           = self._current_user_id()
            user_reviewed = ReviewModel.user_already_reviewed(uid, pid)
            in_wish       = WishlistModel.is_wishlisted(uid, pid)

        return render_template(
            'customer/product_detail.html',
            p=p,
            reviews=reviews,
            user_reviewed=user_reviewed,
            in_wish=in_wish,
        )

    def submit_review(self, pid: int):
        """
        US 2.5 — Submit a product review (POST).
        Creates or updates the review and recalculates avg_rating.
        Encapsulation: upsert + rating update hidden in ReviewModel.
        """
        if not self._is_logged_in():
            self._warn('Please log in to leave a review.')
            return redirect(url_for('auth.login'))

        rating = int(request.form.get('rating', 5))
        title  = request.form.get('title', '').strip()
        body   = request.form.get('body', '').strip()
        uid    = self._current_user_id()

        try:
            ReviewModel.submit_or_update(pid, uid, rating, title, body)
            self._ok('Review submitted!')
        except Exception:
            self._err('Could not submit review.')

        return redirect(url_for('customer.product_detail', pid=pid))


# Singleton — routes.customer imports this instance
customer_controller = CustomerController()
