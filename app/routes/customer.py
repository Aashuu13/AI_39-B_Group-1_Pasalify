"""
Sprint 2 - US 2.2: View Product
Routes kept:
  - /products       (browse list to reach a product)
  - /product/<pid>  (view product detail — the core feature)
  - /               (home — starting point)
  - /product/<pid>/review  (submit review — shown on product_detail page)
Other US 2.x routes (cart, checkout, wishlist, orders) are removed.
"""
from flask import Blueprint
from app.controllers import customer_controller
from app.utils.auth import login_required

customer_bp = Blueprint('customer', __name__)
cc = customer_controller
_lr = login_required

# ── US 2.2 View Product (core feature) ────────────────────────────────────────
customer_bp.add_url_rule('/product/<int:pid>', 'product_detail', cc.product_detail)

# ── Supporting routes (needed to reach the product page) ─────────────────────
customer_bp.add_url_rule('/',          'home',     cc.home)
customer_bp.add_url_rule('/products',  'products', cc.products)

# ── Review submission (shown on product_detail page) ─────────────────────────
customer_bp.add_url_rule('/product/<int:pid>/review', 'submit_review', _lr(cc.submit_review), methods=['POST'])
