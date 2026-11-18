"""Конфигурация render-worker. Читает переменные окружения и файл .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    render_mode: str = "mock"
    render_output_dir: str = "/app/renders"

    database_url: str = "postgresql+psycopg://rail:rail@localhost:5432/railgis"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()