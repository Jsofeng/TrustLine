import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

"""
async with session_factory as session:
Open connection

↓

Use it

↓

Automatically close it
- The async with ensures cleanup even if the test fails.
"""


@pytest.fixture
async def db() -> AsyncSession:
    """Connect tests only to the isolated test database after migrations are applied."""
    test_url = os.environ("TEST_DATABASE_URL")
    engine = create_async_engine(test_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory as session:
        yield session
        await session.rollback() #rolled back to guarantee no database changes persist.
    await engine.dispose() #This shuts down the engine's connection pool.

#ensures removal of old tables after every test
@pytest.fixture
async def clean_db(db: AsyncSession) -> AsyncSession:
    """Remove test rows without creating schema in the application database."""
    for table in (
        "human_overrides",
        "review_cases",
        "agent_decisions",
        "decision_trace_events",
        "evidence_snapshots",
        "investigation_runs",
        "disputes",
        "device_events",
        "transactions",
        "accounts",
    ):
        await db.execute(text(f"DELETE FROM {table}")) # Tells SQLAlchemy to Treat this as raw SQL"
    await db.commit()
    return db

