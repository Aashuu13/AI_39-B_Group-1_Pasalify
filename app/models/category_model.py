"""
==============================================================
OOP Concept: INHERITANCE (Category Model)
==============================================================
- Inheritance: CategoryModel extends BaseModel.
  find_all() is sufficient for most category operations.
==============================================================
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class CategoryModel(BaseModel):
    """
    Represents the `categories` table.
    Simple model — categories don't change often.
    """

    TABLE = 'categories'

    @property
    def table(self) -> str:
        return self.TABLE

    @classmethod
    def find_by_slug(cls, slug: str) -> dict | None:
        return cls.find_where("slug = %s", (slug,), one=True)

    @classmethod
    def all_with_product_count(cls) -> list[dict]:
        """Return categories together with how many active products each has."""
        return Database.query("""
            SELECT c.*, COUNT(p.id) AS product_count
            FROM categories c
            LEFT JOIN products p
                   ON p.category_id = c.id AND p.is_active = 1 AND p.is_approved = 1
            GROUP BY c.id
            ORDER BY c.name
        """)
