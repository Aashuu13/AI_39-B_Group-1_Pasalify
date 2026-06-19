"""
app/models/cart_model.py
================================================================
OOP concepts on display: INHERITANCE + ENCAPSULATION

    - Inheritance:   CartModel extends BaseModel.
    - Encapsulation: add_item() hides the "insert vs. update"
      (upsert) decision — callers don't need to check whether the
      product is already in the cart before calling it.

Represents a `cart` table — one row per (user, product) pair.

NOTE: schema.sql actually names this table `cart_items`, and the
live CustomerController writes its own raw SQL against
`cart_items` directly rather than calling through this model
(see CustomerController._cart_items / cart_add / cart_update /
cart_remove in app/controllers/customer_controller.py). That
means this class currently isn't used by any route — it's kept
here, untouched, as it was found, since fixing app behaviour
wasn't part of this comment-cleanup pass.
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

    # ── Cart operations ───────────────────────────────────────────────────

    @classmethod
    def get_cart(cls, user_id: int) -> list[dict]:
        """Return a user's full cart, joined with product/store details."""
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
        Add a product to the cart, or increment its quantity if it's
        already there. Encapsulation: this "upsert" decision is made
        right here, so callers just call add_item() either way.
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
        """Overwrite a cart row's quantity with an exact value."""
        Database.execute(
            "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
            (qty, user_id, product_id)
        )

    @classmethod
    def remove_item(cls, user_id: int, product_id: int) -> None:
        """Remove one product from a user's cart."""
        Database.execute(
            "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )

    @classmethod
    def clear(cls, user_id: int) -> None:
        """Empty a user's entire cart (e.g. right after checkout)."""
        Database.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

    @classmethod
    def item_count(cls, user_id: int) -> int:
        """Number of distinct product rows currently in the cart."""
        row = Database.query(
            "SELECT COUNT(*) AS c FROM cart WHERE user_id = %s", (user_id,), one=True
        )
        return row['c'] if row else 0
