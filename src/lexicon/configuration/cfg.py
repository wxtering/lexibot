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


class DatabaseConfig(ConfigBase):
    db_url: str
    db_echo: bool
