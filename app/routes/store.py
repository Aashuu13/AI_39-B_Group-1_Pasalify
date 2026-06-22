<<<<<<< HEAD
<<<<<<< HEAD

=======
"""
Store routes — public store pages and customer-seller chat.
"""
>>>>>>> origin/aayushma
=======
"""
Store routes — public store pages and customer-seller chat.
"""
>>>>>>> origin/sandesh
from flask import Blueprint
from app.controllers import store_controller

store_bp = Blueprint('store', __name__)
sc = store_controller

store_bp.add_url_rule('/<slug>',                    'public_store', sc.public_store)
store_bp.add_url_rule('/<slug>/product/<int:pid>',  'store_product', sc.store_product)
store_bp.add_url_rule('/chat/start/<int:seller_id>','start_chat',   sc.start_chat,  methods=['POST'])
store_bp.add_url_rule('/chat/<int:cid>',            'chat_view',    sc.chat_view,   methods=['GET', 'POST'])
