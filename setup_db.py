"""Run once to initialise the database and create all tables."""
from dotenv import load_dotenv
load_dotenv()
from app.db import init_db
init_db()
print("Database setup complete.")
