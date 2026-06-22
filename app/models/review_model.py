
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

    @classmethod
    def find_by_product(cls, product_id: int, approved_only: bool = True) -> list[dict]:
        """All reviews for one product, joined with the reviewer's
        name. Approved-only by default so unmoderated reviews don't
        show on the public product page."""
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
        """True if this user has already left a review on this product
        (used to decide whether submit_review() should INSERT or UPDATE)."""
        row = cls.find_where(
            "user_id = %s AND product_id = %s", (user_id, product_id), one=True
        )
        return row is not None

    @classmethod
    def approve(cls, review_id: int) -> None:
        """
        Approve a review, then immediately recalculate the product's
        avg_rating so the storefront always reflects the latest
        approved reviews. Imported here (rather than at module level)
        to avoid a circular import between review_model and
        product_model.
        """
        from app.models.product_model import ProductModel
        cls.update(review_id, {'is_approved': 1})
        review = cls.find_by_id(review_id)
        if review:
            ProductModel.update_rating(review['product_id'])

    @classmethod
    def pending(cls) -> list[dict]:
        """Every review still awaiting moderation — the admin queue."""
        return Database.query("""
            SELECT r.*, u.name AS user_name, p.name AS product_name
            FROM reviews r
            JOIN users u ON u.id = r.user_id
            JOIN products p ON p.id = r.product_id
            WHERE r.is_approved = 0
            ORDER BY r.created_at DESC
        """)
# Handles product reviews
