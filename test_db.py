from app.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = result.fetchall()

print("Tables:", tables)
