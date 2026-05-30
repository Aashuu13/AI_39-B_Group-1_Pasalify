"""
=============================================================
OOP Concepts: INHERITANCE, POLYMORPHISM, ENCAPSULATION
               (ProductModel — US 2.1 Search Products)
=============================================================
Inheritance  — ProductModel extends BaseModel; all CRUD
               is inherited automatically.
Polymorphism — search() accepts different filter combos and
               builds the correct SQL each time — same method
               name, different behaviour based on arguments.
Encapsulation— The SQL-building logic for search is hidden
               here.  CustomerController just calls
               ProductModel.search(...) and gets results.
=============================================================
Sprint 2  |  US 2.1 – Search Products  |  Developer: Yubraj KC
Acceptance Criteria:
  1. Open the search bar on the platform.
  2. Enter a keyword for the desired product.
  3. Apply filters to narrow down the results.
  4. Show the matching results to the user.
  5. Display a no result message if nothing is found.
=============================================================
"""

from app.models.base_model import BaseModel
from app.models.database   import Database


class ProductModel(BaseModel):
    """Represents the `products` table."""

    TABLE = 'products'

    @property
    def table(self) -> str:
        return self.TABLE

    # ── US 2.1 – Search  (Polymorphism + Encapsulation) ──────────────────────

    @classmethod
    def search(cls,
               query: str    = '',
               cat_slug: str = '',
               min_price: str = '',
               max_price: str = '',
               sort: str      = 'newest',
               min_rating: str = '') -> list:
        """
        Flexible product search with optional filters.

        AC 2 – keyword matched against name and description.
        AC 3 – filters: category slug, price range, rating, sort order.
        AC 4 – returns a list of matching product dicts.
        AC 5 – returns [] when nothing matches (template shows empty-state).

        Polymorphism: the same method produces different SQL depending
        on which filters are supplied — no if/else chains in the controller.
        Encapsulation: SQL building is completely hidden here.
        """

        sql = """
            SELECT p.*,
                   pi.image_path,
                   s.name AS store_name,
                   s.slug AS store_slug,
                   c.name AS cat_name,
                   c.slug AS cat_slug_col
            FROM   products p
            LEFT JOIN product_images pi
                   ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN   stores     s ON s.id = p.store_id
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE  p.is_active   = 1
              AND  p.is_approved = 1
        """
        args = []

        # AC-2: keyword filter
        if query:
            sql  += " AND (p.name LIKE %s OR p.description LIKE %s)"
            args += [f'%{query}%', f'%{query}%']

        # AC-3: category filter
        if cat_slug:
            sql  += " AND c.slug = %s"
            args.append(cat_slug)

        # AC-3: price range filter
        if min_price:
            sql  += " AND p.price >= %s"
            args.append(min_price)
        if max_price:
            sql  += " AND p.price <= %s"
            args.append(max_price)

        # AC-3: rating filter
        if min_rating:
            sql  += " AND p.avg_rating >= %s"
            args.append(min_rating)

        # AC-3: sort order
        order_map = {
            'newest':     'p.created_at DESC',
            'price_asc':  'p.price ASC',
            'price_desc': 'p.price DESC',
            'rating':     'p.avg_rating DESC',
        }
        sql += f" ORDER BY {order_map.get(sort, 'p.created_at DESC')}"

        return Database.query(sql, tuple(args))

    # ── Other catalogue helpers ───────────────────────────────────────────────

    @classmethod
    def find_active(cls) -> list:
        """All approved, active products with their primary image."""
        return Database.query("""
            SELECT p.*, pi.image_path, s.name AS store_name, s.slug AS store_slug
            FROM   products p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            JOIN   stores s ON s.id = p.store_id
            WHERE  p.is_active = 1 AND p.is_approved = 1
            ORDER  BY p.created_at DESC
        """)

    @classmethod
    def decrement_stock(cls, product_id: int, qty: int) -> None:
        """Reduce stock by qty, never below zero (Encapsulation)."""
        Database.execute(
            "UPDATE products SET stock_qty = GREATEST(0, stock_qty - %s) WHERE id = %s",
            (qty, product_id)
        )
