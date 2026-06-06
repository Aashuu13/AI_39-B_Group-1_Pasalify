"""
Customer routes
US 2.1 Search Products | US 2.4 Wishlist | US 2.5 Product Reviews
"""
from flask import Blueprint
from app.controllers import customer_controller
from app.utils.auth  import login_required

customer_bp = Blueprint('customer', __name__)
cc  = customer_controller
_lr = login_required

# ── US 2.1 Search Products ────────────────────────────────────────────────────
customer_bp.add_url_rule('/products', 'products', cc.products)

# ── US 2.2 View Product Detail (with reviews) ─────────────────────────────────
customer_bp.add_url_rule('/product/<int:pid>', 'product_detail', cc.product_detail)

# ── US 2.4 Wishlist ───────────────────────────────────────────────────────────
customer_bp.add_url_rule('/wishlist',                  'wishlist',        _lr(cc.wishlist))
customer_bp.add_url_rule('/wishlist/toggle/<int:pid>', 'wishlist_toggle', _lr(cc.wishlist_toggle))

# ── US 2.5 Product Reviews ────────────────────────────────────────────────────
customer_bp.add_url_rule('/product/<int:pid>/review', 'submit_review', _lr(cc.submit_review), methods=['POST'])
