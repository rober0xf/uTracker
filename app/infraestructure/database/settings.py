from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )  # extra ignore for the api connection


settings_database = DatabaseSettings()


class APISettings(BaseSettings):
    rapidapi_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings_api = APISettings()
