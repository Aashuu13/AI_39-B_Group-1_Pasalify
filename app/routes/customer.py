"""
Customer routes
Sprint 2: US 2.2 – View Product       → /customer/products, /customer/products/<pid>
Sprint 3: US 1.4 – Edit Customer UI   → /customer/profile
Sprint 3: US 2.6 – Seller Chat        → /customer/chats, /customer/chat/start/<id>, /customer/chat/<cid>
"""
from flask import Blueprint
from app.controllers import customer_controller
from app.utils.auth import role_required

customer_bp = Blueprint('customer', __name__)
cc = customer_controller
_customer = role_required('customer')

# Home – needed as default landing page after login
customer_bp.add_url_rule('/home', 'home', cc.home)

# Sprint 2 – US 2.2: View Product
customer_bp.add_url_rule('/products',              'products',       cc.products)
customer_bp.add_url_rule('/products/<int:pid>',    'product_detail', cc.product_detail)

# Sprint 3 – US 1.4: Edit Customer UI
customer_bp.add_url_rule('/profile', 'profile', _customer(cc.profile), methods=['GET', 'POST'])

# Sprint 3 – US 2.6: Seller Chat
customer_bp.add_url_rule('/chats',                         'chats',       _customer(cc.chats))
customer_bp.add_url_rule('/chat/start/<int:store_id>',     'chat_start',  _customer(cc.chat_start))
customer_bp.add_url_rule('/chat/<int:cid>',                'chat_detail', _customer(cc.chat_detail), methods=['GET', 'POST'])

# Utility – notification count for navbar badge
customer_bp.add_url_rule('/notif-count', 'notif_count', cc.notif_count)
