"""
app package
================================================================
Marks the 'app' folder as a Python package and re-exports the
application factory so the rest of the project (and run.py) can
simply do:

    from app import create_app
"""

from app.app import create_app
