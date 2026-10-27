import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ThreatView"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/threatview"

    SECRET_KEY: str = "threatview_dev_insecure_secret_key_change_me_9381028401"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    OTX_API_KEY: str = ""
    URLHAUS_API_KEY: str = ""

    INGESTION_INTERVAL_MINUTES: int = 60
    MAX_INDICATORS_PER_FETCH: int = 500

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
