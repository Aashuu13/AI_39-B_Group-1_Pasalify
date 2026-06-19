"""
app/models/category_model.py
================================================================
OOP concept on display: INHERITANCE

CategoryModel extends BaseModel and barely needs anything of its
own — find_all() (inherited) already covers most use cases, since
categories are simple and rarely change.

Represents the `categories` table.
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class CategoryModel(BaseModel):
    """
    Represents the `categories` table.
    A simple model — categories don't change often.
    """

    TABLE = 'categories'

    @property
    def table(self) -> str:
        return self.TABLE

    @classmethod
    def find_by_slug(cls, slug: str) -> dict | None:
        """Look up a category by its URL slug."""
        return cls.find_where("slug = %s", (slug,), one=True)

    @classmethod
    def all_with_product_count(cls) -> list[dict]:
        """Every category along with how many active, approved
        products currently sit in it — used for the category pills
        on the homepage/product browser."""
        return Database.query("""
            SELECT c.*, COUNT(p.id) AS product_count
            FROM categories c
            LEFT JOIN products p
                   ON p.category_id = c.id AND p.is_active = 1 AND p.is_approved = 1
            GROUP BY c.id
            ORDER BY c.name
        """)
