"""
app/models/order_model.py
================================================================
OOP concepts on display: INHERITANCE + ENCAPSULATION

    - Inheritance:   OrderModel extends BaseModel and gets every
      CRUD method (find_by_id, create, update, ...) for free.
    - Encapsulation: every status change (cancel/ship/complete/
      mark_paid) goes through its own small method instead of
      controllers writing raw "UPDATE orders SET status=..."
      statements scattered across the codebase.

Represents the `orders` table.
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class OrderModel(BaseModel):
    """
    Represents the `orders` table.

    Inherited from BaseModel:
        find_by_id, find_all, find_where, create, update, delete, count

    Adds order-specific methods:
        find_by_user, find_by_store, get_items, recent_all,
        cancel, ship, complete, mark_paid, monthly_revenue
    """

    TABLE = 'orders'

    @property
    def table(self) -> str:
        return self.TABLE

    # ── Lookups ─────────────────────────────────────────────────────────

    @classmethod
    def find_by_user(cls, user_id: int) -> list[dict]:
        """All orders placed by one customer, newest first, with each
        order's line items concatenated into a single readable string."""
        return Database.query("""
            SELECT o.*, GROUP_CONCAT(oi.product_name SEPARATOR ', ') AS items
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            WHERE o.user_id = %s
            GROUP BY o.id
            ORDER BY o.created_at DESC
        """, (user_id,))

    @classmethod
    def find_by_store(cls, store_id: int, limit: int = 50) -> list[dict]:
        """Recent orders that include at least one item from a
        specific store (used on the seller's order list/dashboard)."""
        return Database.query("""
            SELECT o.*, GROUP_CONCAT(oi.product_name SEPARATOR ', ') AS items
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            WHERE oi.store_id = %s
            GROUP BY o.id
            ORDER BY o.created_at DESC
            LIMIT %s
        """, (store_id, limit))

    @classmethod
    def get_items(cls, order_id: int) -> list[dict]:
        """Every line item that belongs to one order."""
        return Database.query(
            "SELECT * FROM order_items WHERE order_id = %s", (order_id,)
        )

    @classmethod
    def recent_all(cls, limit: int = 8) -> list[dict]:
        """Latest orders across the entire platform — used on the
        admin dashboard."""
        return Database.query("""
            SELECT o.*, u.name AS customer
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC
            LIMIT %s
        """, (limit,))

    # ── Status transitions (Encapsulation) ───────────────────────────────

    @classmethod
    def cancel(cls, order_id: int) -> None:
        """Move an order to the 'cancelled' status."""
        cls.update(order_id, {'status': 'cancelled'})

    @classmethod
    def ship(cls, order_id: int) -> None:
        """Move an order to the 'shipped' status."""
        cls.update(order_id, {'status': 'shipped'})

    @classmethod
    def complete(cls, order_id: int) -> None:
        """Move an order to the 'delivered' status."""
        cls.update(order_id, {'status': 'delivered'})

    @classmethod
    def mark_paid(cls, order_id: int) -> None:
        """Flip payment_status to 'paid', separate from the
        shipping/delivery status above."""
        cls.update(order_id, {'payment_status': 'paid'})

    # ── Revenue stats ───────────────────────────────────────────────────

    @classmethod
    def monthly_revenue(cls, store_id: int | None = None, months: int = 6) -> list[dict]:
        """
        Revenue and order count grouped by month for the last N
        months — feeds the line chart on both the seller dashboard
        (store_id given) and the admin dashboard (store_id=None,
        meaning platform-wide).
        """
        if store_id:
            return Database.query("""
                SELECT DATE_FORMAT(o.created_at,'%%Y-%%m') AS month,
                       SUM(oi.subtotal) AS revenue,
                       COUNT(DISTINCT o.id) AS orders
                FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                WHERE oi.store_id = %s
                  AND o.created_at >= DATE_SUB(NOW(), INTERVAL %s MONTH)
                GROUP BY month
                ORDER BY month
            """, (store_id, months))
        return Database.query("""
            SELECT DATE_FORMAT(created_at,'%%Y-%%m') AS month,
                   COUNT(*) AS orders,
                   SUM(total_amount) AS revenue
            FROM orders
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s MONTH)
            GROUP BY month
            ORDER BY month
        """, (months,))
