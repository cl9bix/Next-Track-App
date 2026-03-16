from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]  # backend/

class Settings(BaseSettings):
    DATABASE_URL: str
    ALEMBIC_DATABASE_URL: str
    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    HASH_SECRET_KEY: str

    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None

    BOT_TOKEN: str | None = None
    EVENT_TOKEN_SECRET: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()