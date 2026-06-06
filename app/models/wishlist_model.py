"""
=============================================================
OOP Concepts: INHERITANCE, ENCAPSULATION (WishlistModel)
=============================================================
Inheritance  — WishlistModel extends BaseModel; all CRUD
               is inherited automatically.
Encapsulation— Wishlist toggle logic (add/remove) is
               hidden here; controllers just call methods.
=============================================================
Sprint 3  |  US 2.4 – Wishlist  |  Feature addition
=============================================================
"""

from app.models.base_model import BaseModel
from app.models.database   import Database


class WishlistModel(BaseModel):
    """Represents the `wishlists` table."""

    TABLE = 'wishlists'

    @property
    def table(self) -> str:
        return self.TABLE

    @classmethod
    def find_by_user(cls, user_id: int) -> list:
        """All wishlist items for a user, joined with product and store info."""
        return Database.query("""
            SELECT w.id, p.*, pi.image_path, s.name AS store_name
            FROM   wishlists w
            JOIN   products p  ON p.id  = w.product_id
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN   stores   s  ON s.id  = p.store_id
            WHERE  w.user_id = %s
            ORDER  BY w.created_at DESC
        """, (user_id,))

    @classmethod
    def is_wishlisted(cls, user_id: int, product_id: int) -> bool:
        """Check if a product is in the user's wishlist."""
        row = cls.find_where(
            "user_id = %s AND product_id = %s", (user_id, product_id), one=True
        )
        return row is not None

    @classmethod
    def toggle(cls, user_id: int, product_id: int) -> bool:
        """
        Add product to wishlist if not present, remove if it is.
        Returns True if added, False if removed.
        Encapsulation: toggle logic is hidden here.
        """
        existing = Database.query(
            "SELECT id FROM wishlists WHERE user_id = %s AND product_id = %s",
            (user_id, product_id), one=True
        )
        if existing:
            Database.execute("DELETE FROM wishlists WHERE id = %s", (existing['id'],))
            return False
        else:
            Database.execute(
                "INSERT INTO wishlists (user_id, product_id) VALUES (%s, %s)",
                (user_id, product_id)
            )
            return True
