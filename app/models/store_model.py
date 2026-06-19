"""
==============================================================
OOP Concept: INHERITANCE (Store Model)
==============================================================
- Inheritance: StoreModel inherits all CRUD from BaseModel.
- Encapsulation: Slug generation and approval state changes
  are encapsulated here.
==============================================================
"""

import uuid
from app.models.basemodel import BaseModel
from app.models.database import Database


class StoreModel(BaseModel):
    """
    Represents the `stores` table.

    Inherits from BaseModel:
        find_by_id, find_all, find_where, create, update, delete, count
    """

    TABLE = 'stores'

    @property
    def table(self) -> str:
        return self.TABLE

    # ── Lookups ───────────────────────────────────────────────────────────────

    @classmethod
    def find_by_user(cls, user_id: int) -> dict | None:
        """Return the store owned by a given seller user."""
        return cls.find_where("user_id = %s", (user_id,), one=True)

    @classmethod
    def find_by_slug(cls, slug: str) -> dict | None:
        """Return a store by its URL slug."""
        return cls.find_where("slug = %s AND is_approved = 1", (slug,), one=True)

    @classmethod
    def all_with_owner(cls) -> list[dict]:
        """Return all stores joined with the owner user."""
        return Database.query("""
            SELECT s.*, u.name AS owner, u.email
            FROM stores s
            JOIN users u ON u.id = s.user_id
            ORDER BY s.created_at DESC
        """)

    # ── Creation Helper ───────────────────────────────────────────────────────

    @classmethod
    def make_unique_slug(cls, name: str) -> str:
        """
        Generate a URL-safe slug from the store name.
        Appends a short UUID suffix if the slug already exists.
        Encapsulation: slug logic stays here.
        """
        slug = name.lower().replace(' ', '-').replace("'", '')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        if cls.find_where("slug = %s", (slug,), one=True):
            slug += '-' + str(uuid.uuid4())[:4]
        return slug

    # ── Moderation ────────────────────────────────────────────────────────────

    @classmethod
    def approve(cls, store_id: int) -> None:
        cls.update(store_id, {'is_approved': 1})

    @classmethod
    def reject(cls, store_id: int) -> None:
        cls.update(store_id, {'is_approved': 0, 'is_active': 0})

    # ── Stats ─────────────────────────────────────────────────────────────────

    @classmethod
    def stats(cls, store_id: int) -> dict:
        """
        Return key dashboard stats for a store.
        Encapsulation: multiple queries bundled into one call.
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
# Handles seller store data
