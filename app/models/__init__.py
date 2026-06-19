"""
app/models/__init__.py
================================================================
OOP concept on display: PACKAGE ORGANISATION

Exports every model class from one place so controllers never
need to know which file a model lives in:

    from app.models import UserModel, ProductModel, OrderModel

Database and BaseModel are exported too, in case a future model
needs to inherit from BaseModel directly.
"""

from app.models.database          import Database
from app.models.basemodel         import BaseModel
from app.models.user_model        import UserModel
from app.models.product_model     import ProductModel
from app.models.store_model       import StoreModel
from app.models.order_model       import OrderModel
from app.models.review_model      import ReviewModel
from app.models.category_model    import CategoryModel
from app.models.cart_model        import CartModel
from app.models.notification_model import NotificationModel

__all__ = [
    'Database',
    'BaseModel',
    'UserModel',
    'ProductModel',
    'StoreModel',
    'OrderModel',
    'ReviewModel',
    'CategoryModel',
    'CartModel',
    'NotificationModel',
]
