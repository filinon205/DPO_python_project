from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False}) # По умолчанию SQLite разрешает работать с соединением только из одного потока, а FastAPI использует несколько. Этот аргумент снимает ограничение
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Base class for all database models. Need for metadata"""
    pass

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

