import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from game_service.repo.sql.models import Base

target_metadata = Base.metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

ALEMBIC_DATABASE_URL = os.getenv("ALEMBIC_DATABASE_URL")
ASYNC_URL = os.getenv("DATABASE_URL")

# Build URL from separate parameters if DATABASE_URL is not set
if not ASYNC_URL:
    DB_HOST = os.getenv("DATABASE_HOST", "localhost")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")
    DB_USER = os.getenv("DATABASE_USER", os.getenv("POSTGRES_USER", "postgres"))
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD", os.getenv("POSTGRES_PASSWORD", "password"))
    DB_NAME = os.getenv("DATABASE_NAME", os.getenv("POSTGRES_DB", "games"))
    from urllib.parse import quote_plus
    encoded_password = quote_plus(DB_PASSWORD)
    ASYNC_URL = f"postgresql+asyncpg://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Build Alembic URL from separate parameters if ALEMBIC_DATABASE_URL is not set
if not ALEMBIC_DATABASE_URL:
    DB_HOST = os.getenv("DATABASE_HOST", "localhost")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")
    DB_USER = os.getenv("DATABASE_USER", os.getenv("POSTGRES_USER", "postgres"))
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD", os.getenv("POSTGRES_PASSWORD", "password"))
    DB_NAME = os.getenv("DATABASE_NAME", os.getenv("POSTGRES_DB", "games"))
    from urllib.parse import quote_plus
    encoded_password = quote_plus(DB_PASSWORD)
    ALEMBIC_DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def run_migrations_offline() -> None:
    url = ALEMBIC_DATABASE_URL or (ASYNC_URL and ASYNC_URL.replace("+asyncpg", ""))
    if not url:
        raise RuntimeError("Set ALEMBIC_DATABASE_URL or DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    if not ASYNC_URL:
        raise RuntimeError("Set DATABASE_URL for async migrations")
    connectable = create_async_engine(ASYNC_URL, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    if ALEMBIC_DATABASE_URL:
        synchronous_engine = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            url=ALEMBIC_DATABASE_URL,
        )
        with synchronous_engine.connect() as connection:
            do_run_migrations(connection)
        synchronous_engine.dispose()
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
