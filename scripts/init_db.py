import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "mydb.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
SEED_PATH = BASE_DIR / "database" / "seed.sql"


def run_sql_file(db_path, file_path):
    with sqlite3.connect(db_path) as conn:
        with open(file_path, "r") as f:
            conn.executescript(f.read())


if __name__ == "__main__":
    run_sql_file(DB_PATH, SCHEMA_PATH)
    run_sql_file(DB_PATH, SEED_PATH)
    print("Database initialized successfully.")
