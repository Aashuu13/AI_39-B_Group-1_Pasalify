"""
app/routes/store.py
================================================================
URL → controller-method wiring for public store pages and the
chat flow a customer can start directly from a storefront.
No role check needed here — these pages are public by design.
"""

from flask import Blueprint
from app.controllers import store_controller

store_bp = Blueprint('store', __name__)
sc = store_controller

store_bp.add_url_rule('/chat/start/<int:seller_id>','start_chat',   sc.start_chat,  methods=['POST'])
store_bp.add_url_rule('/chat/<int:cid>',            'chat_view',    sc.chat_view,   methods=['GET', 'POST'])
