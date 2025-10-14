from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    EVENT_TOKEN_SECRET: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    HASH_SECRET_KEY: str

    DATABASE_URL: str
    REDIS_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
