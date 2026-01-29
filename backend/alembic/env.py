from __future__ import annotations

import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models.session import Base
from app.models import models

target_metadata = Base.metadata


def get_db_url() -> str:
    # 1) пріоритет — ALEMBIC_DATABASE_URL
    url = os.getenv("ALEMBIC_DATABASE_URL")
    if url:
        return url
    # 2) fallback — DATABASE_URL (async -> sync конвертація для alembic)
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Set ALEMBIC_DATABASE_URL or DATABASE_URL env var for Alembic.")
    return url.replace("+asyncpg", "")


def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": get_db_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
