"""
==============================================================
OOP Concept: ABSTRACTION & INHERITANCE (Base Controller)
==============================================================
- Abstraction: BaseController defines WHAT every controller
  can do (flash helpers, redirect helpers, session access,
  file upload) without repeating that code in every subclass.
- Inheritance: AuthController, SellerController, etc. all
  extend BaseController and get these helpers for free.
- Encapsulation: File-upload logic, session reading, and
  flash messaging are hidden here — subclasses just call
  self._save_file(), self._current_user_id(), etc.
==============================================================
"""

import os
import uuid
from abc import ABC, abstractmethod

from flask import session, flash, redirect, url_for, request, current_app
from app.utils import db
from app.utils.auth import log_action, notify as _notify


class BaseController(ABC):
    """
    Abstract Base Controller.

    All controller classes (AuthController, SellerController,
    CustomerController, AdminController, StoreController)
    inherit from this class.

    Provides shared:
      - session helpers    (_current_user_id, _current_role)
      - flash shortcuts    (_ok, _err, _warn, _info)
      - file upload        (_save_file)
      - audit logging      (_log, _notify)
      - DB shorthand       (_q, _run)
    """

    
    _ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

   

    @staticmethod
    def _current_user_id() -> int | None:
        return session.get('user_id')

    @staticmethod
    def _current_role() -> str | None:
        return session.get('role')

    @staticmethod
    def _is_logged_in() -> bool:
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

    

    @staticmethod
    def _q(sql: str, args: tuple = (), one: bool = False):
        """Shorthand for db.query()."""
        return db.query(sql, args, one)

    @staticmethod
    def _run(sql: str, args: tuple = ()) -> int:
        """Shorthand for db.execute(); returns lastrowid."""
        return db.execute(sql, args)

    

    @classmethod
    def _allowed_file(cls, filename: str) -> bool:
        """Return True if the file extension is permitted."""
        return (
            '.' in filename
            and filename.rsplit('.', 1)[1].lower() in cls._ALLOWED_EXTENSIONS
        )

    @classmethod
    def _save_file(cls, file_obj, folder: str = 'uploads') -> str | None:
        """
        Save an uploaded file to UPLOAD_FOLDER/<folder>/.
        Returns the relative path 'uploads/<folder>/<uuid>.<ext>'
        or None if the file is missing / not allowed.

        Encapsulation: callers never deal with paths or UUIDs.
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

    

    @staticmethod
    def _log(action: str, entity_type: str = None, entity_id: int = None):
        """Write an activity_log row for the current user."""
        log_action(session.get('user_id'), action, entity_type, entity_id)

    @staticmethod
    def _notify(user_id: int, title: str, message: str,
                 ntype: str = 'system', link: str = None):
        """Send an in-app notification."""
        _notify(user_id, title, message, ntype, link)

    

    def handle(self, *args, **kwargs):
        """
        Optional dispatch hook.
        Concrete controllers don't have to implement this;
        they expose named methods instead (login, register, …).
        """
        raise NotImplementedError

    

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
"""
==============================================================
OOP Concept: ABSTRACTION & INHERITANCE (Base Controller)
==============================================================
- Abstraction: BaseController defines WHAT every controller
  can do (flash helpers, redirect helpers, session access,
  file upload) without repeating that code in every subclass.
- Inheritance: AuthController, SellerController, etc. all
  extend BaseController and get these helpers for free.
- Encapsulation: File-upload logic, session reading, and
  flash messaging are hidden here — subclasses just call
  self._save_file(), self._current_user_id(), etc.
==============================================================
"""

import os
import uuid
from abc import ABC, abstractmethod

from flask import session, flash, redirect, url_for, request, current_app
from app.utils import db
from app.utils.auth import log_action, notify as _notify


class BaseController(ABC):
    """
    Abstract Base Controller.

    All controller classes (AuthController, SellerController,
    CustomerController, AdminController, StoreController)
    inherit from this class.

    Provides shared:
      - session helpers    (_current_user_id, _current_role)
      - flash shortcuts    (_ok, _err, _warn, _info)
      - file upload        (_save_file)
      - audit logging      (_log, _notify)
      - DB shorthand       (_q, _run)
    """

    
    _ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    

    @staticmethod
    def _current_user_id() -> int | None:
        return session.get('user_id')

    @staticmethod
    def _current_role() -> str | None:
        return session.get('role')

    @staticmethod
    def _is_logged_in() -> bool:
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

   

    @staticmethod
    def _q(sql: str, args: tuple = (), one: bool = False):
        """Shorthand for db.query()."""
        return db.query(sql, args, one)

    @staticmethod
    def _run(sql: str, args: tuple = ()) -> int:
        """Shorthand for db.execute(); returns lastrowid."""
        return db.execute(sql, args)

    

    @classmethod
    def _allowed_file(cls, filename: str) -> bool:
        """Return True if the file extension is permitted."""
        return (
            '.' in filename
            and filename.rsplit('.', 1)[1].lower() in cls._ALLOWED_EXTENSIONS
        )

    @classmethod
    def _save_file(cls, file_obj, folder: str = 'uploads') -> str | None:
        """
        Save an uploaded file to UPLOAD_FOLDER/<folder>/.
        Returns the relative path 'uploads/<folder>/<uuid>.<ext>'
        or None if the file is missing / not allowed.

        Encapsulation: callers never deal with paths or UUIDs.
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

    

    @staticmethod
    def _log(action: str, entity_type: str = None, entity_id: int = None):
        """Write an activity_log row for the current user."""
        log_action(session.get('user_id'), action, entity_type, entity_id)

    @staticmethod
    def _notify(user_id: int, title: str, message: str,
                 ntype: str = 'system', link: str = None):
        """Send an in-app notification."""
        _notify(user_id, title, message, ntype, link)

    

    def handle(self, *args, **kwargs):
        """
        Optional dispatch hook.
        Concrete controllers don't have to implement this;
        they expose named methods instead (login, register, …).
        """
        raise NotImplementedError

  

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
