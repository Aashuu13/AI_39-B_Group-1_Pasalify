"""
app/models/product_model.py
================================================================
OOP concepts on display: INHERITANCE + POLYMORPHISM + ENCAPSULATION

    - Inheritance:   ProductModel extends BaseModel — every CRUD
      method is inherited for free.
    - Polymorphism:  on top of the shared CRUD interface, this class
      adds its own product-specific behaviour (approve, reject,
      update_rating, decrement_stock, search, ...).
    - Encapsulation: stock-guarding logic (never goes below 0) and
      rating recalculation are both hidden inside this class.

Represents the `products` table.
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class ProductModel(BaseModel):
    """
    Represents the `products` table.

    Inherited from BaseModel:
        find_by_id, find_all, find_where, create, update, delete, count

    Adds product-specific methods:
        find_active, find_by_store, search, approve, reject,
        decrement_stock, increment_stock, update_rating,
        soft_delete, get_with_images
    """

    TABLE = 'products'

    @property
    def table(self) -> str:
        return self.TABLE

    # ── Catalogue queries ────────────────────────────────────────────────

    @classmethod
    def find_active(cls) -> list[dict]:
        """Every approved, active product with its primary image and
        store/category names attached, newest first."""
        sql = """
            SELECT p.*, pi.image_path, s.name AS store_name, s.slug AS store_slug,
                   c.name AS cat_name
            FROM products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN stores s ON s.id = p.store_id
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.is_active = 1 AND p.is_approved = 1
            ORDER BY p.created_at DESC
        """
        return Database.query(sql)

    @classmethod
    def find_by_store(cls, store_id: int) -> list[dict]:
        """Every product belonging to one specific store."""
        return cls.find_where("store_id = %s ORDER BY created_at DESC", (store_id,))

    @classmethod
    def search(cls, query: str = '', cat_slug: str = '', min_price: str = '',
               max_price: str = '', sort: str = 'newest', min_rating: str = '') -> list[dict]:
        """
        Flexible product search with optional filters. Builds the SQL
        WHERE clause dynamically based on which filters were actually
        supplied, so the controller just calls
        ProductModel.search(**request.args) without writing any SQL.
        """
        sql = """
            SELECT p.*, pi.image_path, s.name AS store_name, s.slug AS store_slug,
                   c.name AS cat_name
            FROM products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN stores s ON s.id = p.store_id
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.is_active = 1 AND p.is_approved = 1
        """
        args = []
        if query:
            sql += " AND (p.name LIKE %s OR p.description LIKE %s)"
            args += [f'%{query}%', f'%{query}%']
        if cat_slug:
            sql += " AND c.slug = %s"
            args.append(cat_slug)
        if min_price:
            sql += " AND p.price >= %s"
            args.append(min_price)
        if max_price:
            sql += " AND p.price <= %s"
            args.append(max_price)
        if min_rating:
            sql += " AND p.avg_rating >= %s"
            args.append(min_rating)

        order_map = {
            'newest':     'p.created_at DESC',
            'price_asc':  'p.price ASC',
            'price_desc': 'p.price DESC',
            'rating':     'p.avg_rating DESC',
        }
        sql += f" ORDER BY {order_map.get(sort, 'p.created_at DESC')}"
        return Database.query(sql, tuple(args))

    @classmethod
    def get_with_images(cls, product_id: int) -> dict | None:
        """One product plus its store/category info, used for the
        product detail page. Image rows themselves are fetched
        separately in the controller (a product can have many)."""
        product = Database.query("""
            SELECT p.*, s.name AS store_name, s.slug AS store_slug,
                   s.theme_color, s.user_id AS seller_user_id,
                   s.id AS store_id, c.name AS cat_name
            FROM products p
            JOIN stores s ON s.id = p.store_id
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.id = %s AND p.is_active = 1 AND p.is_approved = 1
        """, (product_id,), one=True)
        return product

    @classmethod
    def low_stock(cls, store_id: int) -> list[dict]:
        """Products whose stock has fallen to or below their own
        low_stock_threshold — powers the dashboard low-stock warning."""
        return cls.find_where(
            "store_id = %s AND stock_qty <= low_stock_threshold AND is_active = 1",
            (store_id,)
        )

    # ── Moderation ──────────────────────────────────────────────────────

    @classmethod
    def approve(cls, product_id: int) -> None:
        """Admin approves a product, making it visible to customers."""
        cls.update(product_id, {'is_approved': 1})

    @classmethod
    def reject(cls, product_id: int) -> None:
        """Admin rejects a product (marks it unapproved again)."""
        cls.update(product_id, {'is_approved': 0})

    @classmethod
    def soft_delete(cls, product_id: int) -> None:
        """Seller removes a product, keeping the row so past orders
        that reference it still display correctly."""
        cls.update(product_id, {'is_active': 0})

    # ── Stock management ───────────────────────────────────────────────

    @classmethod
    def decrement_stock(cls, product_id: int, qty: int) -> None:
        """
        Reduce stock after a sale. GREATEST(0, ...) guards against
        stock ever going negative even under unusual timing.
        """
        Database.execute(
            "UPDATE products SET stock_qty = GREATEST(0, stock_qty - %s) WHERE id = %s",
            (qty, product_id)
        )

    @classmethod
    def increment_stock(cls, product_id: int, qty: int) -> None:
        """Add stock back (e.g. after an order is cancelled)."""
        Database.execute(
            "UPDATE products SET stock_qty = stock_qty + %s WHERE id = %s",
            (qty, product_id)
        )

    # ── Rating ──────────────────────────────────────────────────────────

    @classmethod
    def update_rating(cls, product_id: int) -> None:
        """
        Recalculate avg_rating directly from the reviews table.
        Called after a review is submitted/approved, so the product's
        rating is always accurate without storing it redundantly
        anywhere else.
        """
        Database.execute("""
            UPDATE products p
            SET p.avg_rating = (
                SELECT COALESCE(AVG(r.rating), 0)
                FROM reviews r
                WHERE r.product_id = p.id AND r.is_approved = 1
            )
            WHERE p.id = %s
        """, (product_id,))
