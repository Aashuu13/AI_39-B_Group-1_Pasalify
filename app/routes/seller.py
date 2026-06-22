"""
app/routes/seller.py
================================================================
URL → controller-method wiring for every seller-facing page.

Every real route below is wrapped with _seller
(role_required('seller')), so only logged-in users with the
'seller' role can reach them — guests are sent to login, and
customers/admins are redirected home.
"""

from flask import Blueprint, request, current_app, jsonify
from app.controllers import seller_controller
from app.utils.auth import role_required

seller_bp = Blueprint('seller', __name__)
sc      = seller_controller
_seller = role_required('seller')

# ── DEBUG ROUTE — NOT protected by role_required, REMOVE BEFORE PRODUCTION ──
# Quick manual check that file uploads reach the configured UPLOAD_FOLDER
# and pass the extension allow-list. Left in place (not removed) since
# only commenting was requested here, but flagged clearly: this route
# has no login/role check at all and should not ship to a live server.
@seller_bp.route('/debug-upload', methods=['GET', 'POST'])
def debug_upload():
    ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    def _allowed(fn): return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED
    if request.method == 'POST':
        f = request.files.get('logo')
        return jsonify({
            'upload_folder': current_app.config.get('UPLOAD_FOLDER'),
            'file_present':  f is not None,
            'filename':      f.filename if f else None,
            'allowed':       _allowed(f.filename) if f and f.filename else False,
        })
    return '<form method=POST enctype=multipart/form-data><input type=file name=logo><button>Test</button></form>'
# ──────────────────────────────────────────────────────────────────────────

# ── Setup & dashboard ───────────────────────────────────────────────────
seller_bp.add_url_rule('/setup',                          'setup',            _seller(sc.setup),            methods=['GET', 'POST'])
seller_bp.add_url_rule('/dashboard',                      'dashboard',        _seller(sc.dashboard))

# ── Store profile & customization ──────────────────────────────────────
seller_bp.add_url_rule('/store/profile',                  'store_profile',    _seller(sc.store_profile),    methods=['GET', 'POST'])
seller_bp.add_url_rule('/store/customize',                'store_customize',  _seller(sc.store_customize),  methods=['GET', 'POST'])

# ── Products ────────────────────────────────────────────────────────────
seller_bp.add_url_rule('/products',                       'products',         _seller(sc.products))
seller_bp.add_url_rule('/products/add',                   'product_add',      _seller(sc.product_add),      methods=['GET', 'POST'])
seller_bp.add_url_rule('/products/edit/<int:pid>',        'product_edit',     _seller(sc.product_edit),     methods=['GET', 'POST'])
seller_bp.add_url_rule('/products/delete/<int:pid>',      'product_delete',   _seller(sc.product_delete))

# ── Categories (read-only for sellers) ─────────────────────────────────
seller_bp.add_url_rule('/categories',                     'categories',       _seller(sc.categories))

# ── Inventory ───────────────────────────────────────────────────────────
seller_bp.add_url_rule('/inventory',                      'inventory',        _seller(sc.inventory))
seller_bp.add_url_rule('/inventory/update/<int:pid>',     'inventory_update', _seller(sc.inventory_update), methods=['POST'])

# ── Orders ──────────────────────────────────────────────────────────────
seller_bp.add_url_rule('/orders',                         'orders',           _seller(sc.orders))
seller_bp.add_url_rule('/orders/<int:oid>/update',        'order_update',     _seller(sc.order_update),     methods=['POST'])

# ── Reviews ─────────────────────────────────────────────────────────────
seller_bp.add_url_rule('/reviews',                        'reviews',          _seller(sc.reviews))

# ── Customer<->seller chat ──────────────────────────────────────────────
seller_bp.add_url_rule('/chats',                          'chats',            _seller(sc.chats))
seller_bp.add_url_rule('/chats/<int:cid>',                'chat_detail',      _seller(sc.chat_detail),      methods=['GET', 'POST'])

# ── Support tickets (escalated customer chatbot conversations) ─────────
seller_bp.add_url_rule('/support',                        'support_tickets',  _seller(sc.support_tickets))
seller_bp.add_url_rule('/support/reply',                  'support_reply',    _seller(sc.support_reply),    methods=['POST'])
