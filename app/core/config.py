from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql://hospital:hospital@postgres:5432/hospital_directory"
    api_key: str = "change_me"


@lru_cache
def get_settings() -> Settings:
    return Settings()
