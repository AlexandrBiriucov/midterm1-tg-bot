"""
Centralized database management.
Single entry point for all features.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from pathlib import Path
from .models import Base

# Path to unified database
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "data" / "gymbot.db"

# Create database folder if it doesn't exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create database engine
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,  # Disable SQL logs
    future=True,
    connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


def init_db():
    """Initialize database (create all tables)"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {DB_PATH}")


@contextmanager
def get_session() -> Session:
    """
    Context manager for safe session handling.
    
    Usage:
        with get_session() as session:
            user = session.query(User).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ Database error: {e}")
        raise
    finally:
        session.close()