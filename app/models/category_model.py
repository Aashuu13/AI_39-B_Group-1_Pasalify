"""
=============================================================
OOP Concept: INHERITANCE  (CategoryModel)
=============================================================
CategoryModel extends BaseModel.
find_all() is inherited and used directly by the search
filter sidebar — no extra code needed.
=============================================================
"""

from app.models.base_model import BaseModel
from app.models.database   import Database


class CategoryModel(BaseModel):
    """Represents the `categories` table."""

    TABLE = 'categories'

    @property
    def table(self) -> str:
        return self.TABLE

    @classmethod
    def find_by_slug(cls, slug: str) -> dict | None:
        """Return a single category by its URL slug."""
        return cls.find_where("slug = %s", (slug,), one=True)

    @classmethod
    def all_with_count(cls) -> list:
        """Categories with a count of active, approved products each."""
        return Database.query("""
            SELECT c.*, COUNT(p.id) AS product_count
            FROM   categories c
            LEFT JOIN products p
                   ON p.category_id = c.id
                  AND p.is_active   = 1
                  AND p.is_approved = 1
            GROUP  BY c.id
            ORDER  BY c.name
        """)
