"""
=============================================================
OOP Concepts: INHERITANCE, POLYMORPHISM, ENCAPSULATION
               (CustomerController — US 2.1 Search Products)
=============================================================
Inheritance  — CustomerController extends BaseController;
               _ok, _err, _q, _current_user_id inherited free.
Polymorphism — products() calls ProductModel.search() which
               builds different SQL for every filter combo.
Encapsulation— SQL logic hidden in ProductModel; controller
               only reads request args and renders template.
=============================================================
Sprint 2 | US 2.1 – Search Products | Developer: Yubraj KC
Acceptance Criteria:
  1. Open the search bar on the platform.
  2. Enter a keyword for the desired product.
  3. Apply filters to narrow down the results.
  4. Show the matching results to the user.
  5. Display a no result message if nothing is found.
=============================================================
"""

from flask import render_template, request

from app.controllers.base_controller import BaseController
from app.models import ProductModel, CategoryModel


class CustomerController(BaseController):

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


# Singleton — routes.customer imports this instance
customer_controller = CustomerController()
