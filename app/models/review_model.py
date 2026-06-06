"""
=============================================================
OOP Concepts: INHERITANCE, ENCAPSULATION (ReviewModel)
=============================================================
Inheritance  — ReviewModel extends BaseModel; all CRUD
               is inherited automatically.
Encapsulation— After a review is submitted, avg_rating and
               review_count are updated automatically here —
               callers don't need to remember.
=============================================================
Sprint 3  |  US 2.5 – Product Reviews  |  Feature addition
=============================================================
"""

from app.models.base_model import BaseModel
from app.models.database   import Database


class ReviewModel(BaseModel):
    """Represents the `reviews` table."""

    TABLE = 'reviews'

    @property
    def table(self) -> str:
        return self.TABLE

    @classmethod
    def find_by_product(cls, product_id: int, approved_only: bool = True) -> list:
        """Reviews for a product, joined with the reviewer's name."""
        condition = "r.product_id = %s"
        if approved_only:
            condition += " AND r.is_approved = 1"
        return Database.query(f"""
            SELECT r.*, u.name AS reviewer_name
            FROM   reviews r
            JOIN   users   u ON u.id = r.user_id
            WHERE  {condition}
            ORDER  BY r.created_at DESC
        """, (product_id,))

    @classmethod
    def user_already_reviewed(cls, user_id: int, product_id: int) -> bool:
        """Check if a user has already left a review for this product."""
        row = cls.find_where(
            "user_id = %s AND product_id = %s", (user_id, product_id), one=True
        )
        return row is not None

    @classmethod
    def submit_or_update(cls, product_id: int, user_id: int,
                          rating: int, title: str, body: str) -> None:
        """
        Insert a new review or update an existing one (upsert).
        After saving, recalculates the product's avg_rating and review_count.
        Encapsulation: side-effects are handled internally.
        """
        Database.execute(
            """INSERT INTO reviews (product_id, user_id, rating, title, body, is_approved)
               VALUES (%s, %s, %s, %s, %s, 1)
               ON DUPLICATE KEY UPDATE rating=%s, title=%s, body=%s""",
            (product_id, user_id, rating, title, body, rating, title, body)
        )
        cls._update_product_rating(product_id)

    @classmethod
    def _update_product_rating(cls, product_id: int) -> None:
        """
        Recalculate avg_rating and review_count on the product row.
        Encapsulation: rating update logic is kept here.
        """
        Database.execute("""
            UPDATE products
            SET avg_rating   = (SELECT COALESCE(AVG(rating), 0)
                                FROM reviews WHERE product_id = %s AND is_approved = 1),
                review_count = (SELECT COUNT(*)
                                FROM reviews WHERE product_id = %s AND is_approved = 1)
            WHERE id = %s
        """, (product_id, product_id, product_id))
