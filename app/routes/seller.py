"""
Seller routes — all protected by role_required('seller').
"""
from flask import Blueprint
from app.controllers import seller_controller
from app.utils.auth import role_required

seller_bp = Blueprint('seller', __name__)
sc      = seller_controller
_seller = role_required('seller')


seller_bp.add_url_rule('/setup',                          'setup',            _seller(sc.setup),            methods=['GET', 'POST'])
seller_bp.add_url_rule('/dashboard',                      'dashboard',        _seller(sc.dashboard))

seller_bp.add_url_rule('/store/profile',                  'store_profile',    _seller(sc.store_profile),    methods=['GET', 'POST'])
seller_bp.add_url_rule('/store/customize',                'store_customize',  _seller(sc.store_customize),  methods=['GET', 'POST'])

seller_bp.add_url_rule('/products',                       'products',         _seller(sc.products))
seller_bp.add_url_rule('/products/add',                   'product_add',      _seller(sc.product_add),      methods=['GET', 'POST'])
seller_bp.add_url_rule('/products/edit/<int:pid>',        'product_edit',     _seller(sc.product_edit),     methods=['GET', 'POST'])
seller_bp.add_url_rule('/products/delete/<int:pid>',      'product_delete',   _seller(sc.product_delete))

seller_bp.add_url_rule('/categories',                     'categories',       _seller(sc.categories))

seller_bp.add_url_rule('/inventory',                      'inventory',        _seller(sc.inventory))
seller_bp.add_url_rule('/inventory/update/<int:pid>',     'inventory_update', _seller(sc.inventory_update), methods=['POST'])

seller_bp.add_url_rule('/orders',                         'orders',           _seller(sc.orders))
seller_bp.add_url_rule('/orders/<int:oid>/update',        'order_update',     _seller(sc.order_update),     methods=['POST'])

seller_bp.add_url_rule('/reviews',                        'reviews',          _seller(sc.reviews))

seller_bp.add_url_rule('/chats',                          'chats',            _seller(sc.chats))
seller_bp.add_url_rule('/chats/<int:cid>',                'chat_detail',      _seller(sc.chat_detail),      methods=['GET', 'POST'])

seller_bp.add_url_rule('/support',                        'support_tickets',  _seller(sc.support_tickets))
seller_bp.add_url_rule('/support/reply',                  'support_reply',    _seller(sc.support_reply),    methods=['POST'])
