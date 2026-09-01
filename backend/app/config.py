from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AirData AI Assistant"
    environment: str = "development"
    storage_backend: str = "memory"
    ai_backend: str = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    openai_max_output_tokens: int = Field(default=500, ge=100, le=2000)
    firebase_service_account_json: str | None = None
    firebase_service_account_path: str | None = None
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    seed_csv_path: str = str(Path(__file__).resolve().parents[1] / "data" / "air_passengers.csv")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        values = [item.strip() for item in self.allowed_origins.split(",") if item.strip()]
        return values or ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
