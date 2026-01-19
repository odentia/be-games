from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from game_service.core.logging import get_logger

log = get_logger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _sanitize_db_url(url: str) -> str:
    """Убирает пароль из URL для безопасного логирования"""
    try:
        # Формат: postgresql+asyncpg://user:password@host:port/db
        if "@" in url:
            parts = url.split("@")
            if "://" in parts[0]:
                scheme_user_pass = parts[0]
                host_db = parts[1] if len(parts) > 1 else ""
                if ":" in scheme_user_pass:
                    scheme_user = scheme_user_pass.rsplit(":", 1)[0]
                    return f"{scheme_user}:***@{host_db}"
        return url
    except Exception:
        return "***"


async def init_engine(url: str, echo: bool = False) -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(url, echo=echo, pool_pre_ping=True)
        sanitized_url = _sanitize_db_url(url)
        
        # Извлекаем имя базы данных для логирования
        db_name = "unknown"
        try:
            if "/" in url:
                db_part = url.split("/")[-1]
                db_name = db_part.split("?")[0].split("#")[0]
        except Exception:
            pass
        
        log.info(
            "database engine initialized",
            extra={
                "url": sanitized_url,
                "database": db_name,
                "pool_pre_ping": True,
            },
        )
        
        # Проверяем подключение и получаем информацию о БД
        try:
            async with _engine.connect() as conn:
                # Простой тест подключения
                await conn.execute(text("SELECT 1"))
                await conn.commit()
                log.info("database connection test successful", extra={"database": db_name})
                
                # Получаем информацию о версии PostgreSQL
                version_result = await conn.execute(text("SELECT version()"))
                pg_version = version_result.scalar()
                if pg_version:
                    version_short = str(pg_version).split(",")[0]
                    log.info(
                        "database connection established",
                        extra={
                            "database": db_name,
                            "postgres_version": version_short,
                        },
                    )
                
                # Получаем текущее имя базы данных
                db_result = await conn.execute(text("SELECT current_database()"))
                current_db = db_result.scalar()
                if current_db:
                    log.info("connected to database", extra={"database": current_db})
        except Exception as e:
            log.error(f"database connection test failed: {e}", extra={"database": db_name})
            raise
    return _engine


def init_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(engine, expire_on_commit=False)
        log.info("session factory ready")
    return _session_factory


async def close_engine(engine: AsyncEngine | None = None) -> None:
    global _engine, _session_factory
    target = engine or _engine
    if target is not None:
        # Логируем статистику пула перед закрытием
        try:
            pool = target.pool
            log.info(
                "closing database engine",
                extra={
                    "pool_size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                },
            )
        except Exception:
            pass
        
        await target.dispose()
        _engine = None
        _session_factory = None
        log.info("database engine closed")


def get_session_factory() -> async_sessionmaker[AsyncSession] | None:
    return _session_factory
