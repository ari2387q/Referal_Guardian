"""
Database Connection & Session
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./referral_guardian.db",
)

# SQLite fallback for local dev without Postgres
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,   # survive Supabase idle connection drops
        pool_recycle=300,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_sqlite_columns():
    """Ensure missing columns are safely added to existing SQLite tables."""
    if DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                res = conn.exec_driver_sql("PRAGMA table_info(cases)")
                cols = [row[1] for row in res.fetchall()]
                if "educator_summary" not in cols:
                    conn.exec_driver_sql("ALTER TABLE cases ADD COLUMN educator_summary TEXT")
        except Exception:
            pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
