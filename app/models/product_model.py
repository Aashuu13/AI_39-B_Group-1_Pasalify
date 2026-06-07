"""
==============================================================
OOP Concept: INHERITANCE & POLYMORPHISM (Product Model)
==============================================================
- Inheritance: ProductModel extends BaseModel — all CRUD
  operations are inherited for free.
- Polymorphism: ProductModel adds product-specific methods
  on top of the shared interface (approve, reject, update_rating,
  decrement_stock, search, …).
- Encapsulation: Stock validation and rating recalculation
  are hidden inside this class.
==============================================================
"""

from app.models.basemodel import BaseModel
from app.models.database import Database

class ProductModel(BaseModel):
    """
    Represents the `products` table.

    Inherits from BaseModel:
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

    @classmethod
    def find_active(cls) -> list[dict]:
        """Return all approved, active products with their primary image."""
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
        """All products belonging to a specific store."""
        return cls.find_where("store_id = %s ORDER BY created_at DESC", (store_id,))

    @classmethod
    def search(cls, query: str = '', cat_slug: str = '', min_price: str = '',
               max_price: str = '', sort: str = 'newest', min_rating: str = '') -> list[dict]:
        """
        Flexible product search with filters.
        Encapsulation: building the dynamic SQL is hidden here,
        controllers just call ProductModel.search(...).
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
        """Return a product with all its images and related info."""
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
        """Products at or below their low_stock_threshold."""
        return cls.find_where(
            "store_id = %s AND stock_qty <= low_stock_threshold AND is_active = 1",
            (store_id,)
        )

    @classmethod
    def approve(cls, product_id: int) -> None:
        """Admin approves a product."""
        cls.update(product_id, {'is_approved': 1})

    @classmethod
    def reject(cls, product_id: int) -> None:
        """Admin rejects a product (marks unapproved)."""
        cls.update(product_id, {'is_approved': 0})

    @classmethod
    def soft_delete(cls, product_id: int) -> None:
        """Seller removes a product (keeps row for order history)."""
        cls.update(product_id, {'is_active': 0})

    @classmethod
    def decrement_stock(cls, product_id: int, qty: int) -> None:
        """
        Reduce stock by qty.
        Encapsulation: guards against negative stock.
        """
        Database.execute(
            "UPDATE products SET stock_qty = GREATEST(0, stock_qty - %s) WHERE id = %s",
            (qty, product_id)
        )

    @classmethod
    def increment_stock(cls, product_id: int, qty: int) -> None:
        """Add qty back to stock (e.g. after order cancellation)."""
        Database.execute(
            "UPDATE products SET stock_qty = stock_qty + %s WHERE id = %s",
            (qty, product_id)
        )

    @classmethod
    def update_rating(cls, product_id: int) -> None:
        """
        Recalculate avg_rating from the reviews table.
        Called after a new review is approved.
        Encapsulation: rating logic lives here, not in the controller.
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
