import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stats_models import Base

BASE_DIR = r"C:\telegram-gym-bot\main\feature\dev3_progress_stats"
DB_PATH = os.path.join(BASE_DIR, "stats.db")


engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables recreated!")