"""
Customer routes — public and auth-protected.
"""
from flask import Blueprint
from app.controllers import customer_controller
from app.utils.auth import login_required

customer_bp = Blueprint('customer', __name__)
cc = customer_controller   # alias for brevity

_lr = login_required   # alias

# ── Public ────────────────────────────────────────────────────────────────────
customer_bp.add_url_rule('/',                        'home',            cc.home)
customer_bp.add_url_rule('/products',                'products',        cc.products)
customer_bp.add_url_rule('/product/<int:pid>',       'product_detail',  cc.product_detail)
customer_bp.add_url_rule('/support',                 'support',         cc.support)
customer_bp.add_url_rule('/support/chat',            'support_chat',    cc.support_chat,    methods=['POST'])
customer_bp.add_url_rule('/stores',                  'stores',          cc.stores)
customer_bp.add_url_rule('/store/<slug>',            'store_page',      cc.store_page)

# ── Auth-protected ─────────────────────────────────────────────────────────────
customer_bp.add_url_rule('/cart',                    'cart',            _lr(cc.cart))
customer_bp.add_url_rule('/cart/add/<int:pid>',      'cart_add',        _lr(cc.cart_add),       methods=['POST'])
customer_bp.add_url_rule('/cart/update/<int:cid>',   'cart_update',     _lr(cc.cart_update),    methods=['POST'])
customer_bp.add_url_rule('/cart/remove/<int:cid>',   'cart_remove',     _lr(cc.cart_remove))

customer_bp.add_url_rule('/wishlist',                'wishlist',        _lr(cc.wishlist))
customer_bp.add_url_rule('/wishlist/toggle/<int:pid>','wishlist_toggle', _lr(cc.wishlist_toggle))

customer_bp.add_url_rule('/checkout',                'checkout',        _lr(cc.checkout),       methods=['GET', 'POST'])
customer_bp.add_url_rule('/promo/validate',          'validate_promo',  _lr(cc.validate_promo), methods=['POST'])

customer_bp.add_url_rule('/orders',                  'orders',          _lr(cc.orders))
customer_bp.add_url_rule('/order/<int:oid>',         'order_detail',    _lr(cc.order_detail))
customer_bp.add_url_rule('/payments',                'payment_history', _lr(cc.payment_history))

customer_bp.add_url_rule('/review/<int:pid>',        'submit_review',   _lr(cc.submit_review),  methods=['POST'])

customer_bp.add_url_rule('/profile',                 'profile',         _lr(cc.profile),        methods=['GET', 'POST'])
customer_bp.add_url_rule('/notifications',           'notifications',   _lr(cc.notifications))
customer_bp.add_url_rule('/notifications/count',     'notif_count',     _lr(cc.notif_count))

customer_bp.add_url_rule('/chats',                   'chats',           _lr(cc.chats))
customer_bp.add_url_rule('/chat/<int:cid>',          'chat_detail',     _lr(cc.chat_detail),    methods=['GET', 'POST'])
customer_bp.add_url_rule('/chat/start/<int:store_id>','chat_start',      _lr(cc.chat_start))