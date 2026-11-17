"""Конфигурация API. Читает переменные окружения и файл .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "TrainRideGIS API"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg://rail:rail@localhost:5432/railgis"
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    token_ttl_days: int = 7

    snap_radius: float = 0.01
    simplify_tolerance: float = 0.0005

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()