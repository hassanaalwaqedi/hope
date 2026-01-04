"""
Database Connection Management

Production-ready async PostgreSQL connection with:
- Connection pooling
- Health checks
- Graceful shutdown
- Transaction management

SECURITY: Connection strings contain credentials and must
never be logged.
"""

from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from hope.config import get_settings
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base for all ORM models.
    
    All database models should inherit from this base.
    """
    pass


class DatabaseManager:
    """
    Manages database connections and sessions.
    
    Provides connection pooling, health checks, and
    lifecycle management for the database layer.
    
    Usage:
        db = DatabaseManager()
        await db.initialize()
        async with db.session() as session:
            # use session
        await db.close()
    """
    
    def __init__(self) -> None:
        """Initialize database manager (connection not established)."""
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Initialize database engine and session factory.
        
        Should be called once during application startup.
        """
        if self._initialized:
            logger.warning("Database already initialized")
            return
        
        settings = get_settings()
        
        # Create async engine with connection pooling
        self._engine = create_async_engine(
            settings.database.async_url,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=settings.debug,  # SQL logging in debug mode only
        )
        
        # Create session factory
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        self._initialized = True
        logger.info("Database connection pool initialized")
    
    async def close(self) -> None:
        """
        Close database connections.
        
        Should be called during application shutdown.
        """
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._initialized = False
            logger.info("Database connections closed")
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session with automatic cleanup.
        
        Usage:
            async with db.session() as session:
                result = await session.execute(...)
                
        Yields:
            AsyncSession: Database session
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def health_check(self) -> bool:
        """
        Check database connectivity.
        
        Returns:
            True if database is reachable, False otherwise
        """
        if not self._engine:
            return False
        
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False
    
    @property
    def engine(self) -> AsyncEngine | None:
        """Get the SQLAlchemy async engine."""
        return self._engine
    
    @property
    def is_initialized(self) -> bool:
        """Check if database is initialized."""
        return self._initialized


# Global database manager instance
_db_manager: DatabaseManager | None = None


@lru_cache()
def get_db_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager: Singleton database manager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting a database session.
    
    Usage in endpoint:
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_async_session)):
            ...
            
    Yields:
        AsyncSession: Database session
    """
    db = get_db_manager()
    async with db.session() as session:
        yield session
