"""
app/controllers/base_controller.py
================================================================
OOP concepts on display: ABSTRACTION + INHERITANCE + ENCAPSULATION

    - Abstraction:   this class defines WHAT every controller is
      able to do (flash a message, save an upload, log an action)
      without any single concrete controller having to repeat HOW.
    - Inheritance:   AuthController, SellerController,
      CustomerController, AdminController and StoreController all
      extend BaseController and inherit every method below for free.
    - Encapsulation: file-upload handling, session reads, and flash
      messaging are all hidden behind small private-style helpers
      (the leading underscore) — subclasses just call
      self._save_file(...) and never touch os.path or uuid directly.
"""

import os
import uuid
from abc import ABC, abstractmethod

from flask import session, flash, redirect, url_for, request, current_app
from app import db
from app.utils.auth import log_action, notify as _notify


class BaseController(ABC):
    """
    Abstract base class for every controller in the app.

    Concrete subclasses (AuthController, SellerController,
    CustomerController, AdminController, StoreController) all
    inherit:
      - session helpers    (_current_user_id, _current_role, _is_logged_in)
      - flash shortcuts    (_ok, _err, _warn, _info)
      - file upload        (_save_file)
      - audit logging      (_log, _notify)
      - DB shorthand       (_q, _run)
    """

    
    _ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # ── Session helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _current_user_id() -> int | None:
        """Return the logged-in user's id, or None if no one is logged in."""
        return session.get('user_id')

    @staticmethod
    def _current_role() -> str | None:
        """Return 'customer' / 'seller' / 'admin', or None if logged out."""
        return session.get('role')

    @staticmethod
    def _is_logged_in() -> bool:
        """True if the current visitor has an active session."""
        return 'user_id' in session

    

    @staticmethod
    def _ok(msg: str):
        flash(msg, 'success')

    @staticmethod
    def _err(msg: str):
        flash(msg, 'danger')

    @staticmethod
    def _warn(msg: str):
        flash(msg, 'warning')

    @staticmethod
    def _info(msg: str):
        flash(msg, 'info')

    # ── Database shortcuts ─────────────────────────────────────────────────

    @staticmethod
    def _q(sql: str, args: tuple = (), one: bool = False):
        """Shorthand for db.query() — run a SELECT."""
        return db.query(sql, args, one)

    @staticmethod
    def _run(sql: str, args: tuple = ()) -> int:
        """Shorthand for db.execute() — run an INSERT/UPDATE/DELETE.
        Returns lastrowid (handy right after an INSERT)."""
        return db.execute(sql, args)

    # ── File upload (Encapsulation) ────────────────────────────────────────

    @classmethod
    def _allowed_file(cls, filename: str) -> bool:
        """True if the file's extension is in the allow-list."""
        return (
            '.' in filename
            and filename.rsplit('.', 1)[1].lower() in cls._ALLOWED_EXTENSIONS
        )

    @classmethod
    def _save_file(cls, file_obj, folder: str = 'uploads') -> str | None:
        """
        Save an uploaded file under UPLOAD_FOLDER/<folder>/ with a
        random UUID filename (so two uploads never collide), and
        return the relative path 'uploads/<folder>/<uuid>.<ext>'
        ready to store in the database.

        Returns None if no file was actually selected, or its
        extension isn't on the allow-list — callers can just check
        `if path:` without worrying about the details.
        """
        if not file_obj or not file_obj.filename:
            return None
        if not cls._allowed_file(file_obj.filename):
            return None
        ext  = file_obj.filename.rsplit('.', 1)[1].lower()
        name = f"{uuid.uuid4()}.{ext}"
        dest = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(dest, exist_ok=True)
        file_obj.save(os.path.join(dest, name))
        return f'uploads/{folder}/{name}'

    # ── Audit helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _log(action: str, entity_type: str = None, entity_id: int = None):
        """Write an activity_logs row for whoever is currently logged in."""
        log_action(session.get('user_id'), action, entity_type, entity_id)

    @staticmethod
    def _notify(user_id: int, title: str, message: str,
                 ntype: str = 'system', link: str = None):
        """Send an in-app notification to a specific user."""
        _notify(user_id, title, message, ntype, link)

    # ── Abstract hook (optional — subclasses may override) ──────────────────

    def handle(self, *args, **kwargs):
        """
        Optional generic dispatch hook, kept for completeness.
        None of the concrete controllers actually need it — they
        expose individually named methods instead (login, register,
        dashboard, ...), which Flask binds straight to routes.
        """
        raise NotImplementedError

    # ── Representation ─────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
