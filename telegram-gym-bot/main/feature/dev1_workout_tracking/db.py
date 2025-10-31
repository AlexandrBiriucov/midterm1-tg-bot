from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from pathlib import Path
import os

# Отладочная информация
print(f"Текущая рабочая директория: {os.getcwd()}")
print(f"Путь к db.py: {Path(__file__).absolute()}")

# Получаем путь к БД
base_dir = Path(__file__).parent.parent.parent.parent
db_path = base_dir / "src" / "models" / "gymbot.db"

print(f"Путь к БД: {db_path}")
print(f"Папка существует: {db_path.parent.exists()}")

# Создаем папку если ее нет
db_path.parent.mkdir(parents=True, exist_ok=True)
print(f"Папка создана: {db_path.parent.exists()}")

engine = create_engine(f"sqlite:///{db_path}", echo=True, future=True)  # echo=True для отладк
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
