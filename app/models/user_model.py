"""
=============================================================
OOP Concepts: INHERITANCE  &  ENCAPSULATION  (UserModel)
=============================================================
Inheritance  — UserModel extends BaseModel; find_by_id,
               create, update, count are all inherited free.
Encapsulation— Password hashing, email lookup, failed-login
               counter, and last-login update are all hidden
               inside this class.  AuthController never
               touches raw SQL for user operations.
=============================================================
"""

from app.models.base_model import BaseModel
from app.models.database   import Database
from app.utils.auth        import hash_password, check_password


class UserModel(BaseModel):
    """Represents the `users` table."""

    TABLE = 'users'

    @property
    def table(self) -> str:
        return self.TABLE

    # ── Lookups ───────────────────────────────────────────────────────────────

    @classmethod
    def find_by_email(cls, email: str) -> dict | None:
        """Return the user row for a given email, or None."""
        return cls.find_where("email = %s", (email,), one=True)

    @classmethod
    def find_by_email_or_phone(cls, email: str, phone: str) -> dict | None:
        """Used during registration to detect duplicates."""
        return cls.find_where(
            "email = %s OR phone = %s", (email, phone), one=True
        )

    # ── Auth helpers (Encapsulation: password logic lives here) ───────────────

    @classmethod
    def register(cls, name: str, email: str, phone: str,
                 password: str, role: str) -> int:
        """
        Hash the password and INSERT a new user row.
        Returns the new user id.
        """
        return cls.create({
            'name':          name,
            'email':         email,
            'phone':         phone,
            'password_hash': hash_password(password),
            'role':          role,
        })

    @classmethod
    def authenticate(cls, email: str, password: str) -> bool:
        """
        Return True if email+password match a user row.
        Encapsulation: the hash-check never leaks to the controller.
        """
        user = cls.find_by_email(email)
        if not user:
            return False
        return check_password(password, user['password_hash'])

    @classmethod
    def record_failed_login(cls, user_id: int) -> None:
        """Increment the failed_logins counter."""
        Database.execute(
            "UPDATE users SET failed_logins = failed_logins + 1 WHERE id = %s",
            (user_id,)
        )

    @classmethod
    def update_last_login(cls, user_id: int) -> None:
        """Reset failed_logins and stamp last_login on successful auth."""
        Database.execute(
            "UPDATE users SET failed_logins = 0, last_login = NOW() WHERE id = %s",
            (user_id,)
        )

    @classmethod
    def change_password(cls, user_id: int, new_password: str) -> None:
        """Hash and store a new password."""
        cls.update(user_id, {'password_hash': hash_password(new_password)})
