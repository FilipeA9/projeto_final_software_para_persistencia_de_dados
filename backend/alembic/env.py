"""
Alembic environment configuration.

Handles database migrations for PostgreSQL with async support.
"""

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool, engine_from_config
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Load application settings
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from src.config.settings import settings
from src.config.postgres import Base

# Import all models to ensure they're registered with Base.metadata
from src.models.usuario import Usuario
from src.models.ponto_turistico import PontoTuristico
from src.models.hospedagem import Hospedagem
from src.models.avaliacao import Avaliacao
from src.models.favorito import Favorito

# Alembic Config object
config = context.config

# Set database URL from settings - use psycopg2 for migrations (sync)
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata object for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode with sync engine.
    
    Create a sync Engine and associate a connection with the context.
    This is more reliable for migrations, especially on Windows.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
