
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
<<<<<<< HEAD
        Add a product to the cart, or increment its quantity if it's
        already there. Encapsulation: this "upsert" decision is made
        right here, so callers just call add_item() either way.
=======
        Add a product to the cart or increment its quantity.
        Encapsulation: upsert logic is hidden from the controller.
        Validates that requested quantity doesn't exceed available stock.
>>>>>>> origin/aayushma
        """
        product = Database.query(
            "SELECT stock_qty FROM products WHERE id = %s", (product_id,), one=True
        )
        if not product:
            raise ValueError("Product not found")

        existing = cls.find_where(
            "user_id = %s AND product_id = %s", (user_id, product_id), one=True
        )
        current_qty = existing['quantity'] if existing else 0
        new_qty = current_qty + qty

        if new_qty > product['stock_qty']:
            raise ValueError(f"Only {product['stock_qty']} item(s) in stock")

        if existing:
            Database.execute(
                "UPDATE cart SET quantity = quantity + %s WHERE user_id = %s AND product_id = %s",
                (qty, user_id, product_id)
            )
        else:
            cls.create({'user_id': user_id, 'product_id': product_id, 'quantity': qty})

    @classmethod
    def update_qty(cls, user_id: int, product_id: int, qty: int) -> None:
<<<<<<< HEAD
        """Overwrite a cart row's quantity with an exact value."""
=======
        """Set an exact quantity for a cart item. Quantity must be at least 1."""
        if qty < 1:
            raise ValueError("Quantity must be at least 1")
>>>>>>> origin/aayushma
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
