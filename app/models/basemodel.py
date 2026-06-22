"""
app/models/basemodel.py
================================================================
OOP concepts on display: ABSTRACTION + INHERITANCE + ENCAPSULATION

    - Abstraction:   defines WHAT every model can do (find, create,
      update, delete, count) without any subclass repeating HOW.
    - Inheritance:   every model below (UserModel, ProductModel,
      OrderModel, ...) inherits these methods automatically.
    - Encapsulation: database access goes through the Database
      class, which itself wraps app/db.py — none of that is
      visible from inside these methods.
"""

from abc import ABC, abstractmethod
from app.models.database import Database


class BaseModel(ABC):
    """
    Abstract base class for every Pasalify model.

    ABC = Abstract Base Class
    - You can NOT create a BaseModel object directly.
    - Every child class MUST define the ``table`` property
      (enforced by @abstractmethod below).
    - Every child class INHERITS all the CRUD helpers below for free.
    """

   
    @property
    @abstractmethod
    def table(self) -> str:
        """Each child model must specify its database table name."""
        pass

   

    @classmethod
    def _get_table(cls) -> str:
        """
        Internal helper that simply returns cls.TABLE. Kept separate
        from the abstract `table` property above so subclasses can
        expose TABLE as a plain class attribute (simpler than
        instantiating just to read a property).
        """
        return cls.TABLE  # every child class defines TABLE = 'tablename'

    # ── CRUD helpers (inherited by every model) ─────────────────────────────

    @classmethod
    def find_by_id(cls, record_id: int) -> dict | None:
        """
        Return a single row by primary key, or None if it doesn't exist.
        Used by every model: User.find_by_id, Product.find_by_id, etc.
        """
        sql = f"SELECT * FROM {cls.TABLE} WHERE id = %s LIMIT 1"
        return Database.query(sql, (record_id,), one=True)

    @classmethod
    def find_all(cls) -> list[dict]:
        """
        Return every row in the table. Fine for small tables like
        categories — avoid calling this on large tables like orders.
        """
        sql = f"SELECT * FROM {cls.TABLE}"
        return Database.query(sql)

    @classmethod
    def find_where(cls, condition: str, args: tuple = (), one: bool = False):
        """
        Flexible SELECT with a custom WHERE clause, for queries that
        don't fit the simpler helpers above.

        Example:
            User.find_where("email = %s AND is_active = 1", (email,), one=True)
        """
        sql = f"SELECT * FROM {cls.TABLE} WHERE {condition}"
        return Database.query(sql, args, one)

    @classmethod
    def create(cls, data: dict) -> int:
        """
        INSERT a new row from a dict of column -> value pairs.
        Returns the new row's id.

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
        UPDATE an existing row by id, given a dict of column -> new value.

        Example:
            User.update(5, {'name': 'Sita', 'phone': '9800000001'})
        """
        set_clause = ", ".join(f"{col} = %s" for col in data.keys())
        sql = f"UPDATE {cls.TABLE} SET {set_clause} WHERE id = %s"
        Database.execute(sql, (*data.values(), record_id))

    @classmethod
    def delete(cls, record_id: int) -> None:
        """
        Hard-delete a row by id. Most controllers prefer a soft-delete
        (setting is_active = 0) so order history stays intact —
        use this only when permanently removing a row is intended.
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

    # ── Representation ───────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} table='{self.TABLE}'>"
