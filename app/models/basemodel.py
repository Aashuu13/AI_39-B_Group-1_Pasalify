"""
==============================================================
OOP Concept: ABSTRACTION & INHERITANCE (Base Model)
==============================================================
- Abstraction: We define WHAT every model should do
  (find, create, update, delete) without saying HOW.
- Inheritance: Child classes (User, Product, Order, …) will
  inherit these methods and reuse them automatically.
- Encapsulation: The database connection details are hidden
  inside the Database class — outside code never sees them.
==============================================================
"""

from abc import ABC, abstractmethod
from app.models.database import Database


class BaseModel(ABC):
    """
    Abstract Base Class for all Pasalify models.

    ABC = Abstract Base Class
    - You CANNOT create an object of BaseModel directly.
    - Child classes MUST define the ``table`` property.
    - Child classes INHERIT all the helper methods below.
    """

    

    @property
    @abstractmethod
    def table(self) -> str:
        """Each child model must specify its database table name."""
        pass

    

    @classmethod
    def _get_table(cls) -> str:
        """
        Return the table name from the concrete class.
        Uses a temporary instance to access the abstract property.
        Child classes expose `table` as a plain class-level string,
        so this helper just reads it from the class.
        """
        return cls.TABLE  # child classes define TABLE = 'tablename'

    

    @classmethod
    def find_by_id(cls, record_id: int) -> dict | None:
        """
        Return a single row by primary key, or None.

        Inherited by: User, Product, Order, Store, Review, …
        """
        sql = f"SELECT * FROM {cls.TABLE} WHERE id = %s LIMIT 1"
        return Database.query(sql, (record_id,), one=True)

    @classmethod
    def find_all(cls) -> list[dict]:
        """
        Return every row in the table (use sparingly on large tables).

        Inherited by: Category, …
        """
        sql = f"SELECT * FROM {cls.TABLE}"
        return Database.query(sql)

    @classmethod
    def find_where(cls, condition: str, args: tuple = (), one: bool = False):
        """
        Flexible SELECT with a custom WHERE clause.

        Example:
            User.find_where("email = %s AND is_active = 1", (email,), one=True)
        """
        sql = f"SELECT * FROM {cls.TABLE} WHERE {condition}"
        return Database.query(sql, args, one)

    @classmethod
    def create(cls, data: dict) -> int:
        """
        INSERT a new row from a dict of column→value pairs.
        Returns the new row's id (lastrowid).

        Example:
            User.create({'name': 'Ram', 'email': 'ram@np.com', ...})
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {cls.TABLE} ({columns}) VALUES ({placeholders})"
        return Database.execute(sql, tuple(data.values()))

    @classmethod
    def update(cls, record_id: int, data: dict) -> None:
        """
        UPDATE an existing row by id.

        Example:
            User.update(5, {'name': 'Sita', 'phone': '9800000001'})
        """
        set_clause = ", ".join(f"{col} = %s" for col in data.keys())
        sql = f"UPDATE {cls.TABLE} SET {set_clause} WHERE id = %s"
        Database.execute(sql, (*data.values(), record_id))

    @classmethod
    def delete(cls, record_id: int) -> None:
        """
        Hard-delete a row by id.
        Prefer soft-delete (is_active=0) in most controllers.
        """
        sql = f"DELETE FROM {cls.TABLE} WHERE id = %s"
        Database.execute(sql, (record_id,))

    @classmethod
    def count(cls, condition: str = "1", args: tuple = ()) -> int:
        """
        Return COUNT(*) with an optional WHERE condition.

        Example:
            User.count("role = %s", ('seller',))
        """
        sql = f"SELECT COUNT(*) AS c FROM {cls.TABLE} WHERE {condition}"
        row = Database.query(sql, args, one=True)
        return row['c'] if row else 0

   

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} table='{self.TABLE}'>"
