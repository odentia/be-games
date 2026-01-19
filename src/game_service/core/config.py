from __future__ import annotations

import os
import socket
from functools import lru_cache
from typing import Literal, Optional

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


EnvName = Literal["dev", "test", "prod"]


class Settings(BaseSettings):
    app_name: str = Field(default="game-service")
    app_version: str = Field(default="0.1.0")
    env: EnvName = Field(default="dev")
    enable_docs: bool = True
    alembic_database_url: str | None = None

    http_host: str = Field(default="0.0.0.0")
    http_port: int = Field(default=8010)
    reload: bool = Field(default=False)

    _cors_allow_origins: str | None = Field(default=None, alias="CORS_ALLOW_ORIGINS", exclude=True)

    @property
    def cors_allow_origins(self) -> list[str]:
        """Парсит CORS origins из строки в список"""
        return _parse_origins(self._cors_allow_origins)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    database_url: str = Field(
        default="postgresql+asyncpg://games_user:password@localhost:5432/games"
    )
    sql_echo: bool = Field(default=False)

    rawg_base_url: AnyHttpUrl = Field(default="https://api.rawg.io/api")
    rawg_api_key: str = Field(default="CHANGE_ME")

    # --- RabbitMQ ---
    rabbitmq_url: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="RabbitMQ connection URL",
    )

    public_base_url: Optional[AnyHttpUrl] = None
    hostname: str = Field(default_factory=socket.gethostname)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        populate_by_name=True,
    )

    @classmethod
    def from_toml(cls, path: str) -> "Settings":
        with open(path, "rb") as fp:
            data = tomllib.load(fp)
        flat: dict[str, object] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat[sub_key] = sub_value
            else:
                flat[key] = value
        return cls(**flat)


def _parse_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["*"]
    if raw == "*":
        return ["*"]
    return [item.strip() for item in raw.split(",") if item.strip()]


@lru_cache
def load_settings() -> Settings:
    config_file = os.getenv("CONFIG_FILE") or os.getenv("APP_CONFIG")
    defaults = Settings()
    if config_file and os.path.exists(config_file):
        file_settings = Settings.from_toml(config_file)
        merged = file_settings.model_copy(update=defaults.model_dump(exclude_unset=True))
        return merged

    return defaults
