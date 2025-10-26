from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_TASK_DB_URL: str
    POSTGRES_TASK_USER: str
    POSTGRES_TASK_PASSWORD: str
    POSTGRES_TASK_DB: str
    RABBITMQ_URL: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reload_settings() -> Settings:
    """Очищает кэш и возвращает обновлённые настройки."""
    get_settings.cache_clear()
    return get_settings()


settings = reload_settings()
