"""
Customer routes - Sprint 2
US 2.1 Search Products | US 2.2 View Product | US 2.3 Manage Cart
US 3.1 Place Order     | US 3.3 Make Payment | US 4.1 Browse Stores
US 4.2 Wishlist
"""
from flask import Blueprint
from app.controllers import customer_controller
from app.utils.auth import login_required

customer_bp = Blueprint('customer', __name__)
cc = customer_controller
_lr = login_required

# ── US 2.1 Search Products ────────────────────────────────────────────────────
customer_bp.add_url_rule('/',                           'home',            cc.home)
customer_bp.add_url_rule('/products',                   'products',        cc.products)

# ── US 2.2 View Product ───────────────────────────────────────────────────────
customer_bp.add_url_rule('/product/<int:pid>',          'product_detail',  cc.product_detail)

# ── US 2.3 Manage Cart ────────────────────────────────────────────────────────
customer_bp.add_url_rule('/cart',                       'cart',            _lr(cc.cart))
customer_bp.add_url_rule('/cart/add/<int:pid>',         'cart_add',        _lr(cc.cart_add),        methods=['POST'])
customer_bp.add_url_rule('/cart/update/<int:cid>',      'cart_update',     _lr(cc.cart_update),     methods=['POST'])
customer_bp.add_url_rule('/cart/remove/<int:cid>',      'cart_remove',     _lr(cc.cart_remove))

# ── US 3.1 Place Order & US 3.3 Make Payment ─────────────────────────────────
customer_bp.add_url_rule('/checkout',                   'checkout',        _lr(cc.checkout),        methods=['GET', 'POST'])
customer_bp.add_url_rule('/orders',                     'orders',          _lr(cc.orders))
customer_bp.add_url_rule('/order/<int:oid>',            'order_detail',    _lr(cc.order_detail))

# ── US 4.1 Browse Stores ──────────────────────────────────────────────────────
customer_bp.add_url_rule('/stores',                     'stores',          cc.stores)
customer_bp.add_url_rule('/stores/<slug>',              'store_detail',    cc.store_detail)

# ── US 4.2 Wishlist ───────────────────────────────────────────────────────────
customer_bp.add_url_rule('/wishlist',                   'wishlist',        _lr(cc.wishlist))
customer_bp.add_url_rule('/wishlist/toggle/<int:pid>',  'wishlist_toggle', _lr(cc.wishlist_toggle))

# ── Profile & Account ─────────────────────────────────────────────────────────
customer_bp.add_url_rule('/notifications',              'notifications',   _lr(cc.notifications))
customer_bp.add_url_rule('/payments',                   'payment_history', _lr(cc.payment_history))

# ── Support ───────────────────────────────────────────────────────────────────
customer_bp.add_url_rule('/support',                    'support',         cc.support)
customer_bp.add_url_rule('/product/<int:pid>/review',   'submit_review',   _lr(cc.submit_review),   methods=['POST'])
customer_bp.add_url_rule('/store/<slug>',                'store_page',      cc.store_page)

# ── US 1.5  Edit Profile ──────────────────────────────────────────────────────
customer_bp.add_url_rule(
    '/profile',
    'profile',
    login_required(customer_controller.profile),
    methods=['GET', 'POST'],
)


