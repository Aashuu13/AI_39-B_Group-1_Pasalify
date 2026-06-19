"""
==============================================================
OOP Concept: INHERITANCE (Notification Model)
==============================================================
"""

from app.models.basemodel import BaseModel
from app.models.database import Database


class NotificationModel(BaseModel):
    """
    Represents the `notifications` table.
    """

    TABLE = 'notifications'

    @property
    def table(self) -> str:
        return self.TABLE

    @classmethod
    def for_user(cls, user_id: int, limit: int = 20) -> list[dict]:
        """Return recent notifications for a user."""
        return cls.find_where(
            f"user_id = %s ORDER BY created_at DESC LIMIT {limit}", (user_id,)
        )

    @classmethod
    def unread_count(cls, user_id: int) -> int:
        """Count unread notifications."""
        return cls.count("user_id = %s AND is_read = 0", (user_id,))

    @classmethod
    def mark_all_read(cls, user_id: int) -> None:
        """Mark every notification as read for a user."""
        Database.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = %s", (user_id,)
        )

    @classmethod
    def send(cls, user_id: int, title: str, message: str,
             notif_type: str = 'info') -> int:
        """
        Create a new notification.
        Encapsulation: wrapper around create() with defaults.
        """
        return cls.create({
            'user_id': user_id,
            'title':   title,
            'message': message,
            'type':    notif_type,
            'is_read': 0,
        })
# Handles low stock and system notifications
