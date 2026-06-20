"""
app/db.py
================================================================
Low-level MySQL access layer.

This is the ONLY file in the project that talks to pymysql
directly. Everything else — including app/models/database.py and
every model class — goes through the four functions below. That
single choke point means: if Pasalify ever switched databases,
this is the only file that would need to change.

Connections are stored on Flask's request-scoped `g` object, so
each HTTP request gets exactly one connection that is reused for
every query during that request and closed automatically when
the request ends (see close_db, wired up in app/app.py's
teardown_appcontext hook).
"""

import pymysql
import os
from flask import g, current_app


def get_db():
    """
    Return the MySQL connection for the current request,
    opening a new one on first use and caching it on `g`.
    """
    if 'db' not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg['MYSQL_HOST'],
            user=cfg['MYSQL_USER'],
            password=cfg['MYSQL_PASSWORD'],
            database=cfg['MYSQL_DB'],
            port=cfg['MYSQL_PORT'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,  # rows come back as dicts, not tuples
            autocommit=False
        )
    return g.db


def close_db(e=None):
    """Close the request's connection, if one was opened.
    Registered as a Flask teardown_appcontext callback."""
    db = g.pop('db', None)
    if db:
        db.close()


def query(sql, args=(), one=False):
    """
    Run a SELECT and return the results.

    :param sql:  SQL string with %s placeholders (never use f-strings
                 for user input — pymysql escapes the `args` tuple
                 safely, which is what prevents SQL injection here).
    :param args: Values to bind to the placeholders.
    :param one:  If True, return only the first row (or None);
                 otherwise return the full list of rows.
    """
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, args)
        rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def execute(sql, args=()):
    """
    Run an INSERT / UPDATE / DELETE and commit it.
    Returns lastrowid, which is useful right after an INSERT.
    """
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, args)
        lid = cur.lastrowid
    db.commit()
    return lid


def init_db():
    """
    One-off setup helper (not used on every request).

    Creates the database if it doesn't exist yet, then replays
    every statement in schema.sql to build all the tables and
    seed data. Meant to be run manually once, e.g. from a Python
    shell, before the app is used for the first time.
    """
    conn = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'aashuNEXTdoor2007_'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cur:
            db_name = os.environ.get('MYSQL_DB', 'pasalify3_db')
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cur.execute(f"USE {db_name}")
            schema = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
            with open(schema) as f:
                # schema.sql has multiple statements separated by ';' —
                # split and run them one at a time since pymysql's
                # execute() only accepts a single statement.
                for stmt in f.read().split(';'):
                    s = stmt.strip()
                    if s:
                        cur.execute(s)
        conn.commit()
        print("[Pasalify] DB ready.")
    finally:
        conn.close()
