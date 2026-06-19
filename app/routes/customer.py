"""
app/routes/customer.py  — Yubraj's features only
"""

from flask import Blueprint
from app.controllers import customer_controller
from app.utils.auth import login_required

customer_bp = Blueprint('customer', __name__)
cc = customer_controller
_lr = login_required

# ── Public (Sprint 2: view product, Sprint 5: store URL) ────────────
customer_bp.add_url_rule('/',                        'home',           cc.home)
customer_bp.add_url_rule('/products',                'products',       cc.products)
customer_bp.add_url_rule('/product/<int:pid>',       'product_detail', cc.product_detail)
customer_bp.add_url_rule('/stores',                  'stores',         cc.stores)
customer_bp.add_url_rule('/store/<slug>',            'store_page',     cc.store_page)

# ── Public: support (stub so base.html links don't 404) ─────────────
customer_bp.add_url_rule('/support',                 'support',        cc.support)
customer_bp.add_url_rule('/support/chat',            'support_chat',   cc.support_chat, methods=['POST'])

# ── Auth-protected: profile (Sprint 3: edit customer UI) ────────────
customer_bp.add_url_rule('/profile',                 'profile',        _lr(cc.profile), methods=['GET', 'POST'])

# ── Auth-protected: notifications (needed by base.html bell) ────────
customer_bp.add_url_rule('/notifications',           'notifications',  _lr(cc.notifications))
customer_bp.add_url_rule('/notifications/count',     'notif_count',    _lr(cc.notif_count))

# ── Auth-protected: chat (Sprint 3: seller chat) ────────────────────
customer_bp.add_url_rule('/chats',                   'chats',          _lr(cc.chats))
customer_bp.add_url_rule('/chat/<int:cid>',          'chat_detail',    _lr(cc.chat_detail), methods=['GET', 'POST'])
customer_bp.add_url_rule('/chat/start/<int:store_id>','chat_start',    _lr(cc.chat_start))

# ── Stubs for routes referenced in templates/redirects ──────────────
from flask import redirect, url_for, session
from app.utils.auth import login_required as _login_required

@customer_bp.route('/cart')
@_login_required
def cart():
    return redirect(url_for('customer.home'))

@customer_bp.route('/orders')
@_login_required
def orders():
    return redirect(url_for('customer.home'))

@customer_bp.route('/order/<int:oid>')
@_login_required
def order_detail(oid):
    return redirect(url_for('customer.home'))

@customer_bp.route('/wishlist')
@_login_required
def wishlist():
    return redirect(url_for('customer.home'))
