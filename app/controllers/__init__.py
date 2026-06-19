"""
==============================================================
OOP Concept: PACKAGE ORGANISATION (Controllers __init__)
==============================================================
Exports one singleton instance of each controller class.
Routes import from here:

    from app.controllers import auth_controller, seller_controller

Each instance is of a class that inherits from BaseController,
so all shared helpers (_ok, _err, _save_file, _log, …) are
available on every controller without repetition.

Inheritance hierarchy:
    BaseController (ABC)
    ├── AuthController      → auth_controller
    ├── SellerController    → seller_controller
    ├── CustomerController  → customer_controller
    ├── AdminController     → admin_controller
    └── StoreController     → store_controller
==============================================================
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
