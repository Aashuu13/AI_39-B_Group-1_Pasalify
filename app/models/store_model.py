"""
app/models/store_model.py
================================================================
OOP concept on display: INHERITANCE + ENCAPSULATION

    - Inheritance:   StoreModel inherits all CRUD methods from
      BaseModel (find_by_id, create, update, ...).
    - Encapsulation: slug generation and approval-state changes
      are handled entirely inside this class — callers never
      build a slug or write an UPDATE statement themselves.

Represents the `stores` table.
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class StoreModel(BaseModel):
    """
    Represents the `stores` table.

    Inherited from BaseModel:
        find_by_id, find_all, find_where, create, update, delete, count
    """

    TABLE = 'stores'

    @property
    def table(self) -> str:
        return self.TABLE


    @classmethod
    def find_by_user(cls, user_id: int) -> dict | None:
        """Return the store owned by a given seller's user account."""
        return cls.find_where("user_id = %s", (user_id,), one=True)

    @classmethod
    def all_with_owner(cls) -> list[dict]:
        """Every store joined with its owner's name/email — used on
        the admin seller-moderation page."""
        return Database.query("""
            SELECT s.*, u.name AS owner, u.email
            FROM stores s
            JOIN users u ON u.id = s.user_id
            ORDER BY s.created_at DESC
        """)

   
    @classmethod
    def approve(cls, store_id: int) -> None:
        """Admin approves a pending store."""
        cls.update(store_id, {'is_approved': 1})

    @classmethod
    def reject(cls, store_id: int) -> None:
        """Admin rejects a store — unapproves it AND deactivates it."""
        cls.update(store_id, {'is_approved': 0, 'is_active': 0})

    @classmethod
    def set_commission(cls, store_id: int, rate: float) -> None:
        """Admin updates the platform commission rate (%) charged on
        this store's future sales. Clamped to a sane 0–100 range."""
        rate = max(0, min(100, rate))
        cls.update(store_id, {'commission_rate': rate})

   

    @classmethod
    def stats(cls, store_id: int) -> dict:
        """
        Bundle the three key seller-dashboard numbers (total sales,
        total orders, total active products) into one dict, so the
        dashboard view makes a single call instead of three separate
        queries scattered through the controller.
        """
        total_sales = Database.query(
            "SELECT COALESCE(SUM(subtotal), 0) AS t FROM order_items WHERE store_id = %s",
            (store_id,), one=True
        )
        total_orders = Database.query(
            "SELECT COUNT(DISTINCT order_id) AS c FROM order_items WHERE store_id = %s",
            (store_id,), one=True
        )
        total_products = Database.query(
            "SELECT COUNT(*) AS c FROM products WHERE store_id = %s AND is_active = 1",
            (store_id,), one=True
        )
        return {
            'total_sales':    total_sales['t'],
            'total_orders':   total_orders['c'],
            'total_products': total_products['c'],
        }
