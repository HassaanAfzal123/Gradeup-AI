"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database (create tables) and migrate missing columns."""
    import database.models  # noqa: F401 — register models
    Base.metadata.create_all(bind=engine)

    # Lightweight migration: add columns that may be missing on existing SQLite DBs
    from sqlalchemy import text, inspect
    insp = inspect(engine)
    if "quizzes" in insp.get_table_names():
        existing = {c["name"] for c in insp.get_columns("quizzes")}
        with engine.begin() as conn:
            if "model_used" not in existing:
                conn.execute(text("ALTER TABLE quizzes ADD COLUMN model_used VARCHAR(100)"))
            if "is_adaptive" not in existing:
                conn.execute(text("ALTER TABLE quizzes ADD COLUMN is_adaptive INTEGER DEFAULT 0"))

    print("[OK] Database initialized successfully")
