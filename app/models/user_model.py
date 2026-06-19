"""
==============================================================
OOP Concept: INHERITANCE & ENCAPSULATION (User Model)
==============================================================
- Inheritance: UserModel extends BaseModel and gets find_by_id,
  create, update, delete, etc. for FREE.
- Encapsulation: Password hashing logic is hidden inside this
  class. Controllers call UserModel.authenticate() and never
  deal with raw hashes.
- Polymorphism: UserModel overrides `table` (required by ABC).
==============================================================
"""

from app.models.basemodel import BaseModel
from app.models.database import Database
from app.utils.auth import hash_password, check_password


class UserModel(BaseModel):
    """
    Represents the `users` table.

    Inherits from BaseModel:
        find_by_id, find_all, find_where, create, update, delete, count

    Adds user-specific methods:
        find_by_email, authenticate, soft_delete, activate,
        record_failed_login, update_last_login
    """

    TABLE = 'users'

    @property
    def table(self) -> str:          
        return self.TABLE


    @classmethod
    def find_by_email(cls, email: str) -> dict | None:
        """Look up a user by email (case-insensitive)."""
        return cls.find_where("email = %s", (email.lower(),), one=True)

    @classmethod
    def find_by_email_or_phone(cls, email: str, phone: str) -> dict | None:
        """Check if email OR phone already exists (used in registration)."""
        return cls.find_where(
            "email = %s OR phone = %s", (email.lower(), phone), one=True
        )

    @classmethod
    def register(cls, name: str, email: str, phone: str,
                 password: str, role: str = 'customer') -> int:
        """
        Create a new user with a hashed password.
        Returns the new user's id.

        Encapsulation: callers pass the plain password;
        hashing happens inside this method, invisibly.
        """
        return cls.create({
            'name':          name,
            'email':         email.lower(),
            'phone':         phone,
            'password_hash': hash_password(password),
            'role':          role,
        })

    @classmethod
    def authenticate(cls, email: str, password: str) -> dict | None:
        """
        Verify email + password.
        Returns the user dict on success, None on failure.

        Encapsulation: raw hash comparison stays inside this method.
        """
        user = cls.find_by_email(email)
        if user and check_password(password, user['password_hash']):
            return user
        return None

    @classmethod
    def change_password(cls, user_id: int, new_password: str) -> None:
        """Hash and save a new password for the given user."""
        cls.update(user_id, {'password_hash': hash_password(new_password)})

    @classmethod
    def record_failed_login(cls, user_id: int) -> None:
        """Increment the failed_logins counter."""
        Database.execute(
            "UPDATE users SET failed_logins = failed_logins + 1 WHERE id = %s",
            (user_id,)
        )

    @classmethod
    def update_last_login(cls, user_id: int) -> None:
        """Reset failed_logins and stamp last_login = NOW()."""
        Database.execute(
            "UPDATE users SET failed_logins = 0, last_login = NOW() WHERE id = %s",
            (user_id,)
        )

    @classmethod
    def soft_delete(cls, user_id: int) -> None:
        """Deactivate a user without removing the row."""
        cls.update(user_id, {'is_active': 0})

    @classmethod
    def activate(cls, user_id: int) -> None:
        """Re-activate a previously deactivated user."""
        cls.update(user_id, {'is_active': 1})

    @classmethod
    def all_by_role(cls, role: str) -> list[dict]:
        """Return all users with a specific role."""
        return cls.find_where("role = %s ORDER BY created_at DESC", (role,))# User model handles seller and customer registration
# Handles seller and customer registration
