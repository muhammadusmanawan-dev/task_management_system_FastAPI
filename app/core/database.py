from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import DATABASE_URL
from sqlmodel import SQLModel

class Base(DeclarativeBase):
    pass

engine=create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def get_session():
    async with async_session_maker() as session:
        yield session

async def create_db_and_tables():
    from app.users.models import User
    from app.tasks.models import Task

    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )
        await conn.run_sync(
            SQLModel.metadata.create_all
        )
