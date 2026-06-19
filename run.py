"""
run.py
================================================================
Entry point for local development.

This is the file you execute directly:
    python run.py

It builds the Flask app using the factory function and starts
the built-in development server. In production this file is
not used — a WSGI server (gunicorn, waitress, etc.) imports
create_app() from app/app.py instead.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True enables the auto-reloader and the interactive
    # debugger in the browser — turn this off in production.
    app.run(debug=True)
