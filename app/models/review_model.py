"""
==============================================================
OOP Concept: INHERITANCE (Review Model)
==============================================================
- Inheritance: ReviewModel extends BaseModel.
- Encapsulation: After approving a review, avg_rating is
  updated automatically — callers don't need to remember.
==============================================================
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class ReviewModel(BaseModel):
    """
    Represents the `reviews` table.
    """

    TABLE = 'reviews'

    @property
    def table(self) -> str:
        return self.TABLE

    # ── Lookups ───────────────────────────────────────────────────────────────

    @classmethod
    def find_by_product(cls, product_id: int, approved_only: bool = True) -> list[dict]:
        """Reviews for a product, joined with the reviewer's name."""
        condition = "r.product_id = %s"
        if approved_only:
            condition += " AND r.is_approved = 1"
        return Database.query(f"""
            SELECT r.*, u.name AS user_name
            FROM reviews r
            JOIN users u ON u.id = r.user_id
            WHERE {condition}
            ORDER BY r.created_at DESC
        """, (product_id,))

    @classmethod
    def user_already_reviewed(cls, user_id: int, product_id: int) -> bool:
        """Check if a user has already left a review for this product."""
        row = cls.find_where(
            "user_id = %s AND product_id = %s", (user_id, product_id), one=True
        )
        return row is not None

    # ── Moderation ────────────────────────────────────────────────────────────

    @classmethod
    def approve(cls, review_id: int) -> None:
        """
        Approve a review and recalculate the product's avg_rating.
        Encapsulation: side-effect (rating update) is handled internally.
        """
        from app.models.product_model import ProductModel
        cls.update(review_id, {'is_approved': 1})
        review = cls.find_by_id(review_id)
        if review:
            ProductModel.update_rating(review['product_id'])

    @classmethod
    def pending(cls) -> list[dict]:
        """All reviews awaiting moderation (admin view)."""
        return Database.query("""
            SELECT r.*, u.name AS user_name, p.name AS product_name
            FROM reviews r
            JOIN users u ON u.id = r.user_id
            JOIN products p ON p.id = r.product_id
            WHERE r.is_approved = 0
            ORDER BY r.created_at DESC
        """)
# Handles product reviews
