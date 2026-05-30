"""
=============================================================
OOP Concepts: ABSTRACTION  &  INHERITANCE  (BaseModel)
=============================================================
Abstraction  — BaseModel defines WHAT every model can do
               (find, create, update, delete) without saying
               HOW at the business level.
Inheritance  — UserModel, ProductModel, CategoryModel all
               extend BaseModel and get every CRUD method
               for free.  Zero repetition.
Encapsulation— The TABLE name and db access are kept inside
               the class; callers never write raw SQL for
               simple lookups.
=============================================================
"""

from abc import ABC, abstractmethod
from app.models.database import Database


class BaseModel(ABC):
    """
    Abstract Base Class shared by all Pasalify models.

    Child classes MUST set the class-level TABLE attribute.
    They automatically inherit:
        find_by_id, find_all, find_where, create, update, delete, count
    """

    # Every child class defines this, e.g. TABLE = 'users'
    TABLE: str = ''

    # ── Abstract property forces child to declare TABLE ───────────────────────
    @property
    @abstractmethod
    def table(self) -> str:
        """Return the database table name for this model."""

    # ── Shared CRUD (Inheritance: every child gets these for free) ─────────────

    @classmethod
    def find_by_id(cls, record_id: int) -> dict | None:
        """Return one row by primary key, or None."""
        return Database.query(
            f"SELECT * FROM {cls.TABLE} WHERE id = %s LIMIT 1",
            (record_id,), one=True
        )

    @classmethod
    def find_all(cls) -> list:
        """Return every row in the table."""
        return Database.query(f"SELECT * FROM {cls.TABLE}")

    @classmethod
    def find_where(cls, condition: str, args: tuple = (), one: bool = False):
        """
        Flexible SELECT with a custom WHERE clause.
        Example: UserModel.find_where("email = %s", (email,), one=True)
        """
        return Database.query(
            f"SELECT * FROM {cls.TABLE} WHERE {condition}", args, one
        )

    @classmethod
    def create(cls, data: dict) -> int:
        """INSERT a row from a column→value dict.  Returns new row id."""
        cols  = ", ".join(data.keys())
        holes = ", ".join(["%s"] * len(data))
        return Database.execute(
            f"INSERT INTO {cls.TABLE} ({cols}) VALUES ({holes})",
            tuple(data.values())
        )

    @classmethod
    def update(cls, record_id: int, data: dict) -> None:
        """UPDATE an existing row by id."""
        set_clause = ", ".join(f"{col} = %s" for col in data.keys())
        Database.execute(
            f"UPDATE {cls.TABLE} SET {set_clause} WHERE id = %s",
            (*data.values(), record_id)
        )

    @classmethod
    def delete(cls, record_id: int) -> None:
        """Hard-delete a row by id."""
        Database.execute(f"DELETE FROM {cls.TABLE} WHERE id = %s", (record_id,))

    @classmethod
    def count(cls, condition: str = "1", args: tuple = ()) -> int:
        """Return COUNT(*) with an optional WHERE condition."""
        row = Database.query(
            f"SELECT COUNT(*) AS c FROM {cls.TABLE} WHERE {condition}", args, one=True
        )
        return row['c'] if row else 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} table='{self.TABLE}'>"
