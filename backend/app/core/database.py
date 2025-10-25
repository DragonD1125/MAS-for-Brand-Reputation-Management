"""
Database configuration and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# Base class for models
Base = declarative_base()

# Lazy initialization of database engines
_engine = None
_async_engine = None
_SessionLocal = None
_AsyncSessionLocal = None

def get_engine():
    """Get or create synchronous database engine"""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
    return _engine

def get_async_engine():
    """Get or create asynchronous database engine"""
    global _async_engine
    if _async_engine is None:
        _async_engine = create_async_engine(
            settings.DATABASE_URL_ASYNC,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
    return _async_engine

def get_session_local():
    """Get or create session maker"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_async_session_local():
    """Get or create async session maker"""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _AsyncSessionLocal

# For backward compatibility
engine = property(lambda self: get_engine())
async_engine = property(lambda self: get_async_engine())
SessionLocal = property(lambda self: get_session_local())
AsyncSessionLocal = property(lambda self: get_async_session_local())


# Dependency for getting database session
def get_db():
    """Get database session (synchronous)"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Get async database session"""
    AsyncSessionLocal = get_async_session_local()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    async_engine = get_async_engine()
    async with async_engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.models.brand import Brand
        from app.models.mention import Mention
        from app.models.sentiment import SentimentAnalysis
        from app.models.alert import Alert
        from app.models.user import User
        
        await conn.run_sync(Base.metadata.create_all)
