import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

load_dotenv()

db_url = os.getenv("DB_URL")

# Async setup (существующий код)
engine = create_async_engine(db_url, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Sync setup (новый код для multiprocessing)
# Конвертируем async URL в sync URL
sync_db_url = db_url.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
sync_engine = create_engine(sync_db_url, echo=True)
sync_session = sessionmaker(bind=sync_engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session


@contextmanager
def get_sync_session():
    """Синхронная сессия для multiprocessing"""
    session = sync_session()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()