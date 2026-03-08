from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

load_dotenv(".env")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models.session import Base
from app.models import models  # noqa: F401

target_metadata = Base.metadata


def get_db_url() -> str:
    url = os.getenv("ALEMBIC_DATABASE_URL")
    if url:
        return url

    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Set ALEMBIC_DATABASE_URL or DATABASE_URL env var for Alembic.")

    return url.replace("+asyncpg", "")


def run_migrations_online() -> None:
    config.set_main_option("sqlalchemy.url", get_db_url())

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
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()