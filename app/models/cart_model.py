"""
==============================================================
OOP Concept: INHERITANCE & ENCAPSULATION (Cart Model)
==============================================================
- Inheritance: CartModel extends BaseModel.
- Encapsulation: add_item handles both INSERT and UPDATE
  (upsert) so callers don't need to know whether the item
  already exists in the cart.
==============================================================
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class CartModel(BaseModel):
    """
    Represents the `cart` table (one row per user+product pair).
    """

    TABLE = 'cart'

    @property
    def table(self) -> str:
        return self.TABLE

    # ── Cart Operations ───────────────────────────────────────────────────────

    @classmethod
    def get_cart(cls, user_id: int) -> list[dict]:
        """Return full cart for a user, joined with product details."""
        return Database.query("""
            SELECT c.*, p.name, p.price, p.stock_qty,
                   pi.image_path, s.name AS store_name, s.id AS store_id
            FROM cart c
            JOIN products p ON p.id = c.product_id
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN stores s ON s.id = p.store_id
            WHERE c.user_id = %s
        """, (user_id,))

    @classmethod
    def add_item(cls, user_id: int, product_id: int, qty: int = 1) -> None:
        """
        Add a product to the cart or increment its quantity.
        Encapsulation: upsert logic is hidden from the controller.
        """
        existing = cls.find_where(
            "user_id = %s AND product_id = %s", (user_id, product_id), one=True
        )
        if existing:
            Database.execute(
                "UPDATE cart SET quantity = quantity + %s WHERE user_id = %s AND product_id = %s",
                (qty, user_id, product_id)
            )
        else:
            cls.create({'user_id': user_id, 'product_id': product_id, 'quantity': qty})

    @classmethod
    def update_qty(cls, user_id: int, product_id: int, qty: int) -> None:
        """Set an exact quantity for a cart item."""
        Database.execute(
            "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
            (qty, user_id, product_id)
        )

    @classmethod
    def remove_item(cls, user_id: int, product_id: int) -> None:
        """Remove a single item from the cart."""
        Database.execute(
            "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )

    @classmethod
    def clear(cls, user_id: int) -> None:
        """Empty the entire cart for a user (called after checkout)."""
        Database.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

    @classmethod
    def item_count(cls, user_id: int) -> int:
        """Total number of distinct items in the cart."""
        row = Database.query(
            "SELECT COUNT(*) AS c FROM cart WHERE user_id = %s", (user_id,), one=True
        )
        return row['c'] if row else 0
