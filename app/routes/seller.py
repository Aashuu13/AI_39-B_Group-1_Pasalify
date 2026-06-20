"""
Seller routes - Sprint 3
US 4.5 Manage Inventory | US 4.6 Manage Orders | US 2.6 Seller Chat
"""
from flask import Blueprint
from app.controllers import seller_controller
from app.utils.auth import role_required

seller_bp = Blueprint('seller', __name__)
sc      = seller_controller
_seller = role_required('seller')

seller_bp.add_url_rule('/setup',                            'setup',              _seller(sc.setup),              methods=['GET', 'POST'])
seller_bp.add_url_rule('/dashboard',                        'dashboard',          _seller(sc.dashboard))

seller_bp.add_url_rule('/products',                         'products',           _seller(sc.products))
seller_bp.add_url_rule('/products/add',                     'product_add',        _seller(sc.product_add),        methods=['GET', 'POST'])
seller_bp.add_url_rule('/products/edit/<int:pid>',          'product_edit',       _seller(sc.product_edit),       methods=['GET', 'POST'])
seller_bp.add_url_rule('/products/delete/<int:pid>',        'product_delete',     _seller(sc.product_delete))

seller_bp.add_url_rule('/inventory',                        'inventory',          _seller(sc.inventory))
seller_bp.add_url_rule('/inventory/update/<int:pid>',       'inventory_update',   _seller(sc.inventory_update),   methods=['POST'])
seller_bp.add_url_rule('/inventory/bulk',                   'inventory_bulk',     _seller(sc.inventory_bulk_update), methods=['POST'])

seller_bp.add_url_rule('/orders',                           'orders',             _seller(sc.orders))
seller_bp.add_url_rule('/orders/<int:oid>',                 'order_detail',       _seller(sc.order_detail))
seller_bp.add_url_rule('/orders/<int:oid>/status',          'order_status',       _seller(sc.order_status),       methods=['POST'])
seller_bp.add_url_rule('/orders/<int:oid>/update',          'order_update',       _seller(sc.order_update),       methods=['POST'])

seller_bp.add_url_rule('/categories',                       'categories',         _seller(sc.categories))

seller_bp.add_url_rule('/reviews',                          'reviews',            _seller(sc.reviews))

seller_bp.add_url_rule('/chats',                            'chats',              _seller(sc.chats))
seller_bp.add_url_rule('/chats/<int:chat_id>',              'chat_detail',        _seller(sc.chat_detail),        methods=['GET', 'POST'])
seller_bp.add_url_rule('/chats/<int:chat_id>/send',         'send_message',       _seller(sc.send_message),       methods=['POST'])

seller_bp.add_url_rule('/store/profile',                    'store_profile',      _seller(sc.store_profile),      methods=['GET', 'POST'])
seller_bp.add_url_rule('/store/customize',                'store_customize',  _seller(sc.store_customize),  methods=['GET', 'POST'])
