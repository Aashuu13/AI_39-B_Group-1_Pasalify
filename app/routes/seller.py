"""
Seller routes
Sprint 3: US 2.6 – Seller Chat        → /seller/chats, /seller/chats/<cid>
Sprint 4: US 4.4 – Organize Products  → /seller/products (CRUD), /seller/categories
"""
from flask import Blueprint
from app.controllers import seller_controller
from app.utils.auth import role_required

seller_bp = Blueprint('seller', __name__)
sc      = seller_controller
_seller = role_required('seller')

# Store setup (required before using seller features)
seller_bp.add_url_rule('/setup',     'setup',     _seller(sc.setup),     methods=['GET', 'POST'])
seller_bp.add_url_rule('/dashboard', 'dashboard', _seller(sc.dashboard))

# Sprint 4 – US 4.4: Organize Products
seller_bp.add_url_rule('/products',                     'products',      _seller(sc.products))
seller_bp.add_url_rule('/products/add',                 'product_add',   _seller(sc.product_add),    methods=['GET', 'POST'])
seller_bp.add_url_rule('/products/edit/<int:pid>',      'product_edit',  _seller(sc.product_edit),   methods=['GET', 'POST'])
seller_bp.add_url_rule('/products/delete/<int:pid>',    'product_delete',_seller(sc.product_delete))
seller_bp.add_url_rule('/categories',                   'categories',    _seller(sc.categories))

# Sprint 3 – US 2.6: Seller Chat
seller_bp.add_url_rule('/chats',            'chats',       _seller(sc.chats))
seller_bp.add_url_rule('/chats/<int:cid>',  'chat_detail', _seller(sc.chat_detail), methods=['GET', 'POST'])
