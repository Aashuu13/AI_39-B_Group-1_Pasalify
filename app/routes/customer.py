"""
Customer routes - Sprint 3
US 1.5 Edit Profile   | US 2.4 Wishlist        | US 2.5 Product Reviews
US 2.6 Seller Chat    | US 3.2 Track Orders    | US 3.5 Apply Promo Code
(Includes all Sprint 1+2 routes)
"""
from flask import Blueprint
from app.controllers import customer_controller
from app.utils.auth import login_required

customer_bp = Blueprint('customer', __name__)
cc = customer_controller
_lr = login_required

customer_bp.add_url_rule('/',                              'home',            cc.home)
customer_bp.add_url_rule('/products',                      'products',        cc.products)

customer_bp.add_url_rule('/product/<int:pid>',             'product_detail',  cc.product_detail)

customer_bp.add_url_rule('/cart',                          'cart',            _lr(cc.cart))
customer_bp.add_url_rule('/cart/add/<int:pid>',            'cart_add',        _lr(cc.cart_add),         methods=['POST'])
customer_bp.add_url_rule('/cart/update/<int:cid>',         'cart_update',     _lr(cc.cart_update),      methods=['POST'])
customer_bp.add_url_rule('/cart/remove/<int:cid>',         'cart_remove',     _lr(cc.cart_remove))

customer_bp.add_url_rule('/wishlist',                      'wishlist',        _lr(cc.wishlist))
customer_bp.add_url_rule('/wishlist/toggle/<int:pid>',     'wishlist_toggle', _lr(cc.wishlist_toggle))

customer_bp.add_url_rule('/product/<int:pid>/review',      'submit_review',   _lr(cc.submit_review),    methods=['POST'])

customer_bp.add_url_rule('/chats',                         'my_chats',        _lr(cc.my_chats))
customer_bp.add_url_rule('/chats/start/<int:seller_id>',   'start_chat',      _lr(cc.start_chat))
customer_bp.add_url_rule('/chats/<int:chat_id>',           'chat_detail',     _lr(cc.chat_detail),      methods=['GET', 'POST'])

customer_bp.add_url_rule('/checkout',                      'checkout',        _lr(cc.checkout),         methods=['GET', 'POST'])
customer_bp.add_url_rule('/orders',                        'orders',          _lr(cc.orders))

customer_bp.add_url_rule('/order/<int:oid>',               'order_detail',    _lr(cc.order_detail))
customer_bp.add_url_rule('/order/<int:oid>/cancel',        'order_cancel',    _lr(cc.order_cancel),     methods=['POST'])

customer_bp.add_url_rule('/payments',                      'payment_history', _lr(cc.payment_history))

customer_bp.add_url_rule('/promo/apply',                   'apply_promo',     _lr(cc.apply_promo),      methods=['POST'])

customer_bp.add_url_rule('/stores',                        'stores',          cc.stores)
customer_bp.add_url_rule('/stores/<slug>',                 'store_detail',    cc.store_detail)
customer_bp.add_url_rule('/store/<slug>',                  'store_page',      cc.store_page)

customer_bp.add_url_rule('/profile',                       'profile',         _lr(cc.profile),          methods=['GET', 'POST'])
customer_bp.add_url_rule('/notifications',                 'notifications',   _lr(cc.notifications))

customer_bp.add_url_rule('/support',                       'support',         cc.support)
