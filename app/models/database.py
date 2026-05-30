"""
=============================================================
OOP Concept: ENCAPSULATION  (Database)
=============================================================
All raw pymysql / db.py calls are hidden inside this class.
Models never import db directly — they call Database.query()
and Database.execute().  The connection details are invisible
to the rest of the application.
=============================================================
"""

from app import db as _db


class Database:
    """
    Thin OOP wrapper around app/db.py.

    Encapsulation: one place owns how data is read/written.
    Every model inherits access through BaseModel._db = Database.
    """

    @staticmethod
    def query(sql: str, args: tuple = (), one: bool = False):
        """Run a SELECT.  Returns list[dict] or dict|None when one=True."""
        return _db.query(sql, args, one)

    @staticmethod
    def execute(sql: str, args: tuple = ()) -> int:
        """Run INSERT / UPDATE / DELETE.  Returns lastrowid."""
        return _db.execute(sql, args)
