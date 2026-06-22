
from app.models.basemodel import BaseModel
from app.models.database import Database
from app.utils.auth import hash_password, check_password

class UserModel(BaseModel):
    """
    Represents the `users` table.

    Inherited from BaseModel:
        find_by_id, find_all, find_where, create, update, delete, count

    Adds user-specific methods:
        find_by_email, authenticate, soft_delete, activate,
        record_failed_login, update_last_login
    """

    TABLE = 'users'

    @property
    def table(self) -> str:          
        return self.TABLE

<<<<<<< HEAD
=======

>>>>>>> origin/sandesh
    @classmethod
    def find_by_email(cls, email: str) -> dict | None:
        """Look up a user by email (case-insensitive)."""
        return cls.find_where("email = %s", (email.lower(),), one=True)

    @classmethod
    def find_by_email_or_phone(cls, email: str, phone: str) -> dict | None:
        """Used during registration to check whether the email OR
        the phone number is already taken by someone else."""
        return cls.find_where(
            "email = %s OR phone = %s", (email.lower(), phone), one=True
        )

    @classmethod
    def register(cls, name: str, email: str, phone: str,
                 password: str, role: str = 'customer') -> int:
        """
        Create a new user. The caller passes a plain-text password;
        hashing happens invisibly inside this method, so nowhere else
        in the codebase needs to know how passwords are hashed.
        Returns the new user's id.
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
        Verify an email + password combination.
        Returns the user dict on success, or None on failure —
        callers never see (or need to compare) a raw hash themselves.
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
        """Increment the failed_logins counter after a wrong password."""
        Database.execute(
            "UPDATE users SET failed_logins = failed_logins + 1 WHERE id = %s",
            (user_id,)
        )

    @classmethod
    def update_last_login(cls, user_id: int) -> None:
        """Reset failed_logins back to 0 and stamp last_login = NOW()
        after a successful login."""
        Database.execute(
            "UPDATE users SET failed_logins = 0, last_login = NOW() WHERE id = %s",
            (user_id,)
        )

    @classmethod
    def soft_delete(cls, user_id: int) -> None:
        """Deactivate a user account without deleting the row."""
        cls.update(user_id, {'is_active': 0})

    @classmethod
    def activate(cls, user_id: int) -> None:
        """Re-activate a previously deactivated user."""
        cls.update(user_id, {'is_active': 1})

    @classmethod
    def all_by_role(cls, role: str) -> list[dict]:
<<<<<<< HEAD
        """Return all users that have a specific role (customer/seller/admin)."""
        return cls.find_where("role = %s ORDER BY created_at DESC", (role,))
=======
        """Return all users with a specific role."""
        return cls.find_where("role = %s ORDER BY created_at DESC", (role,))# User model handles seller and customer registration
# Handles seller and customer registration
>>>>>>> origin/sandesh
