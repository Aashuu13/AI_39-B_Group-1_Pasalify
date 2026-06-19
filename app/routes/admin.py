"""
Admin routes — all protected by role_required('admin').
"""
from flask import Blueprint
from app.controllers import admin_controller
from app.utils.auth import role_required

admin_bp = Blueprint('admin', __name__)
ac     = admin_controller
_admin = role_required('admin')

admin_bp.add_url_rule('/dashboard',                    'dashboard',       _admin(ac.dashboard))

admin_bp.add_url_rule('/sellers',                      'sellers',         _admin(ac.sellers))
admin_bp.add_url_rule('/sellers/<int:sid>/approve',    'seller_approve',  _admin(ac.seller_approve))
admin_bp.add_url_rule('/sellers/<int:sid>/reject',     'seller_reject',   _admin(ac.seller_reject))

admin_bp.add_url_rule('/products',                     'products',        _admin(ac.products))
admin_bp.add_url_rule('/products/<int:pid>/approve',   'product_approve', _admin(ac.product_approve))
admin_bp.add_url_rule('/products/<int:pid>/remove',    'product_remove',  _admin(ac.product_remove))

admin_bp.add_url_rule('/finances',                     'finances',        _admin(ac.finances))
admin_bp.add_url_rule('/finances/export',              'finance_export',  _admin(ac.finance_export))

admin_bp.add_url_rule('/users',                        'users',           _admin(ac.users))
admin_bp.add_url_rule('/users/<int:uid>/toggle',       'user_toggle',     _admin(ac.user_toggle))

admin_bp.add_url_rule('/promos',                       'promos',          _admin(ac.promos))
admin_bp.add_url_rule('/promos/add',                   'promo_add',       _admin(ac.promo_add),   methods=['POST'])
admin_bp.add_url_rule('/promos/<int:pid>/toggle',      'promo_toggle',    _admin(ac.promo_toggle))

admin_bp.add_url_rule('/system',                       'system',          _admin(ac.system))
admin_bp.add_url_rule('/system/backup',                'backup',          _admin(ac.backup))

admin_bp.add_url_rule('/categories',                   'categories',      _admin(ac.categories))
admin_bp.add_url_rule('/categories/add',               'category_add',    _admin(ac.category_add), methods=['POST'])

admin_bp.add_url_rule('/support',                      'support_tickets', _admin(ac.support_tickets))
admin_bp.add_url_rule('/support/reply',                'support_reply',   _admin(ac.support_reply),   methods=['POST'])
