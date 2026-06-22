"""
app/models/database.py
================================================================
OOP concept on display: ENCAPSULATION

All the raw pymysql connection details live in app/db.py — this
class just wraps those two functions (query/execute) behind a
clean, model-friendly interface. Every model imports and calls
``Database.query(...)`` / ``Database.execute(...)`` and never
touches pymysql, or even app/db.py, directly.
"""

from app import db as _db


class Database:
    """
    Thin wrapper around app/db.py, used the same way everywhere:

        from app.models.database import Database
        Database.query("SELECT * FROM users WHERE id = %s", (uid,), one=True)

    Models never see a pymysql connection object — they only ever
    see dicts (or lists of dicts) coming back from these two methods.
    """

  

    @staticmethod
    def query(sql: str, args: tuple = (), one: bool = False):
        """
        Run a SELECT statement.

        :param sql:  SQL string with %s placeholders
        :param args: Tuple of values to bind
        :param one:  If True, return only the first row (or None)
        :return:     dict | list[dict] | None
        """
        return _db.query(sql, args, one)

   

    @staticmethod
    def execute(sql: str, args: tuple = ()) -> int:
        """
        Run an INSERT / UPDATE / DELETE statement.

        :param sql:  SQL string with %s placeholders
        :param args: Tuple of values to bind
        :return:     lastrowid (useful right after an INSERT)
        """
        return _db.execute(sql, args)
