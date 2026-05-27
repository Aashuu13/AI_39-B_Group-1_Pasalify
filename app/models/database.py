"""
==============================================================
OOP Concept: ENCAPSULATION (Database Wrapper)
==============================================================
- Encapsulation: All raw pymysql connection logic is hidden
  inside the Database class. Models never touch pymysql directly.
- The Database class wraps app/db.py and exposes a clean, safe
  interface (query / execute / last_insert_id) to all models.
- Outside code never sees the connection details.
==============================================================
"""

from app import db as _db


class Database:
    """
    Singleton-style wrapper around app/db.py.

    Models import and use ONE shared instance of this class
    (``from app.models.database import Database``).
    They call ``Database.query()``, ``Database.execute()``, etc.
    — and never touch pymysql themselves (Encapsulation).
    """

    # ── Read ──────────────────────────────────────────────────────────────────

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

    # ── Write ─────────────────────────────────────────────────────────────────

    @staticmethod
    def execute(sql: str, args: tuple = ()) -> int:
        """
        Run an INSERT / UPDATE / DELETE statement.

        :param sql:  SQL string with %s placeholders
        :param args: Tuple of values to bind
        :return:     lastrowid (useful after INSERT)
        """
        return _db.execute(sql, args)
