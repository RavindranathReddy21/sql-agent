import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')

if not DB_URL:
    raise ValueError("DATABASE_URL not set in environment")

engine = create_engine(DB_URL, echo=False)