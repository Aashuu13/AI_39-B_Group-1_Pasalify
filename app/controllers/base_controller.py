"""
=============================================================
OOP Concepts: ABSTRACTION  &  INHERITANCE  (BaseController)
=============================================================
Abstraction  — BaseController defines WHAT every controller
               can do (flash, session access, DB shorthand)
               without repeating code in each subclass.
Inheritance  — AuthController and CustomerController both
               extend BaseController and get every helper
               (_ok, _err, _q, _run, _current_user_id …)
               completely for free.
Encapsulation— Session reading, flash messaging, and DB
               access are all hidden behind small methods.
               Subclasses never call session[], flash(), or
               db.query() directly.
=============================================================
"""

from abc import ABC
from flask import session, flash
from app import db


class BaseController(ABC):
    """
    Abstract Base Controller.

    AuthController and CustomerController inherit from this.
    Provides:
      - Flash shortcuts     : _ok, _err, _warn, _info
      - Session helpers     : _current_user_id, _current_role, _is_logged_in
      - DB shortcuts        : _q (query), _run (execute)
    """

    # ── Flash shortcuts (Encapsulation) ───────────────────────────────────────

    @staticmethod
    def _ok(msg: str) -> None:
        flash(msg, 'success')

    @staticmethod
    def _err(msg: str) -> None:
        flash(msg, 'danger')

    @staticmethod
    def _warn(msg: str) -> None:
        flash(msg, 'warning')

    @staticmethod
    def _info(msg: str) -> None:
        flash(msg, 'info')

    # ── Session helpers (Encapsulation) ───────────────────────────────────────

    @staticmethod
    def _current_user_id() -> int | None:
        return session.get('user_id')

    @staticmethod
    def _current_role() -> str | None:
        return session.get('role')

    @staticmethod
    def _is_logged_in() -> bool:
        return 'user_id' in session

    # ── DB shortcuts (Encapsulation) ──────────────────────────────────────────

    @staticmethod
    def _q(sql: str, args: tuple = (), one: bool = False):
        """Short for db.query()."""
        return db.query(sql, args, one)

    @staticmethod
    def _run(sql: str, args: tuple = ()) -> int:
        """Short for db.execute(); returns lastrowid."""
        return db.execute(sql, args)

    # ── Representation ────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
