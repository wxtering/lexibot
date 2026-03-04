from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / "cfg.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class BotConfig(ConfigBase):
    bot_token: SecretStr


def get_bot_config() -> BotConfig:
    return BotConfig()  # type:ignore


class DatabaseConfig(ConfigBase):
    db_url: str
    db_echo: bool = False


def get_database_config() -> DatabaseConfig:
    return DatabaseConfig()  # type:ignore
