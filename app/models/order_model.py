"""
==============================================================
OOP Concept: INHERITANCE & ENCAPSULATION (Order Model)
==============================================================
- Inheritance: OrderModel extends BaseModel for all CRUD.
- Encapsulation: Status transition rules (place, cancel,
  ship, complete) are hidden inside this class so controllers
  never write raw UPDATE queries for orders.
==============================================================
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class OrderModel(BaseModel):
    """
    Represents the `orders` table.

    Inherits from BaseModel:
        find_by_id, find_all, find_where, create, update, delete, count

    Adds order-specific methods:
        find_by_user, find_by_store, place_order,
        cancel, ship, complete, get_items
    """

    TABLE = 'orders'

    @property
    def table(self) -> str:
        return self.TABLE


    @classmethod
    def find_by_user(cls, user_id: int) -> list[dict]:
        """All orders placed by a customer (newest first)."""
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
        """Recent orders containing items from a specific store."""
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
        """Return all line-items for an order."""
        return Database.query(
            "SELECT * FROM order_items WHERE order_id = %s", (order_id,)
        )

    @classmethod
    def recent_all(cls, limit: int = 8) -> list[dict]:
        """Admin dashboard: latest orders across the platform."""
        return Database.query("""
            SELECT o.*, u.name AS customer
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC
            LIMIT %s
        """, (limit,))


    @classmethod
    def cancel(cls, order_id: int) -> None:
        """Cancel a pending order."""
        cls.update(order_id, {'status': 'cancelled'})

    @classmethod
    def ship(cls, order_id: int) -> None:
        """Mark order as shipped."""
        cls.update(order_id, {'status': 'shipped'})

    @classmethod
    def complete(cls, order_id: int) -> None:
        """Mark order as delivered / completed."""
        cls.update(order_id, {'status': 'delivered'})

    @classmethod
    def mark_paid(cls, order_id: int) -> None:
        """Update payment_status to paid."""
        cls.update(order_id, {'payment_status': 'paid'})


    @classmethod
    def monthly_revenue(cls, store_id: int | None = None, months: int = 6) -> list[dict]:
        """
        Monthly revenue & order count for the last N months.
        If store_id is given, scoped to that store; otherwise platform-wide.
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
        """, (months,))# Handles order status and tracking
