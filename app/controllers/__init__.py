"""
app/controllers/__init__.py
================================================================
OOP concept on display: PACKAGE ORGANISATION + INHERITANCE

This file exports one ready-to-use SINGLETON instance of each
controller class, so routes never have to instantiate a
controller themselves — they just import the already-built
object:

    from app.controllers import auth_controller, seller_controller

Every controller class below inherits from BaseController, so
they all share the same helper methods (_ok, _err, _save_file,
_log, ...) without copying that code into each one.

    BaseController (abstract)
    +-- AuthController      -> auth_controller
    +-- SellerController    -> seller_controller
    +-- CustomerController  -> customer_controller
    +-- AdminController     -> admin_controller
    +-- StoreController     -> store_controller
"""

from app.controllers.auth_controller     import auth_controller
from app.controllers.seller_controller   import seller_controller
from app.controllers.customer_controller import customer_controller
from app.controllers.admin_controller    import admin_controller
from app.controllers.store_controller    import store_controller

__all__ = [
    'auth_controller',
    'seller_controller',
    'customer_controller',
    'admin_controller',
    'store_controller',
]
