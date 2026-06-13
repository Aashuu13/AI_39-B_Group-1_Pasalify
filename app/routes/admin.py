"""
Admin routes - Sprint 3
US 5.2 Content Control | US 5.3 Track Transactions
"""
from flask import Blueprint
from app.controllers import admin_controller
from app.utils.auth import role_required

admin_bp = Blueprint('admin', __name__)
ac     = admin_controller
_admin = role_required('admin')


admin_bp.add_url_rule('/dashboard',                    'dashboard',        _admin(ac.dashboard))


admin_bp.add_url_rule('/sellers',                      'sellers',          _admin(ac.sellers))
admin_bp.add_url_rule('/sellers/<int:sid>/approve',    'seller_approve',   _admin(ac.seller_approve))
admin_bp.add_url_rule('/sellers/<int:sid>/reject',     'seller_reject',    _admin(ac.seller_reject))


admin_bp.add_url_rule('/products',                     'products',         _admin(ac.products))
admin_bp.add_url_rule('/products/<int:pid>/approve',   'product_approve',  _admin(ac.product_approve))
admin_bp.add_url_rule('/products/<int:pid>/remove',    'product_remove',   _admin(ac.product_remove))


admin_bp.add_url_rule('/users',                        'users',            _admin(ac.users))
admin_bp.add_url_rule('/users/<int:uid>/toggle',       'user_toggle',      _admin(ac.user_toggle))


admin_bp.add_url_rule('/categories',                   'categories',       _admin(ac.categories))
admin_bp.add_url_rule('/categories/add',               'category_add',     _admin(ac.category_add),     methods=['POST'])
admin_bp.add_url_rule('/categories/<int:cid>/delete',  'category_delete',  _admin(ac.category_delete))


admin_bp.add_url_rule('/finances',                     'finances',         _admin(ac.finances))
admin_bp.add_url_rule('/finances/export',              'finance_export',   _admin(ac.finance_export))
admin_bp.add_url_rule('/promos',                       'promos',           _admin(ac.promos))
admin_bp.add_url_rule('/promos/add',                   'promo_add',        _admin(ac.promo_add),        methods=['POST'])
admin_bp.add_url_rule('/promos/<int:pid>/toggle',      'promo_toggle',     _admin(ac.promo_toggle))


admin_bp.add_url_rule('/content',                      'content_control',  _admin(ac.content_control))
admin_bp.add_url_rule('/reviews/<int:rid>/approve',    'review_approve',   _admin(ac.review_approve))
admin_bp.add_url_rule('/reviews/<int:rid>/remove',     'review_remove',    _admin(ac.review_remove))
admin_bp.add_url_rule('/flags/<int:fid>/resolve',      'flag_resolve',     _admin(ac.flag_resolve),     methods=['POST'])


admin_bp.add_url_rule('/transactions',                 'transactions',     _admin(ac.transactions))
admin_bp.add_url_rule('/commissions',                  'commission_report',_admin(ac.commission_report))


admin_bp.add_url_rule('/system',                       'system',           _admin(ac.system))
admin_bp.add_url_rule('/backup',                       'backup',           _admin(ac.backup))
