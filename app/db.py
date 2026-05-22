import pymysql
import os
from flask import g, current_app


def get_db():
    if 'db' not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg['MYSQL_HOST'],
            user=cfg['MYSQL_USER'],
            password=cfg['MYSQL_PASSWORD'],
            database=cfg['MYSQL_DB'],
            port=cfg['MYSQL_PORT'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()


def query(sql, args=(), one=False):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, args)
        rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def execute(sql, args=()):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, args)
        lid = cur.lastrowid
    db.commit()
    return lid


def init_db():
    conn = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', ''),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cur:
            db_name = os.environ.get('MYSQL_DB', 'pasalify2_db')
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cur.execute(f"USE {db_name}")
            schema = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
            with open(schema) as f:
                for stmt in f.read().split(';'):
                    s = stmt.strip()
                    if s:
                        cur.execute(s)
        conn.commit()
        print("[Pasalify] DB ready.")
    finally:
        conn.close()
