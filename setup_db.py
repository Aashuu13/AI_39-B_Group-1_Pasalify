"""
Run this once to initialize the database and create all tables + demo users.
Usage: python setup_db.py
"""
from dotenv import load_dotenv
load_dotenv()
from app.db import init_db
init_db()
print("\n✅ Database ready!")
print("Demo accounts:")
print("  Admin    → admin@pasalify.com    / admin123")
print("  Customer → customer@pasalify.com / customer123")
print("  Seller   → seller@pasalify.com   / seller123")
