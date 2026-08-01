from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

engine = create_async_engine(get_settings().database_url, pool_pre_ping=True) #pool_pre_ping -> checks if this connection still alive before using, if it's dead creates a new one
SessionLocal = async_sessionmaker(engine=engine, expire_on_commit=False) # expire_on_commit allows the object to keep its values

async def get_db_session() -> AsyncIterator(AsyncSession):
    async with SessionLocal() as session:
        yield session
