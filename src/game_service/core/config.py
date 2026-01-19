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

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Database connection parameters (can be overridden by DATABASE_URL)
    database_host: str = Field(default="localhost")
    database_port: int = Field(default=5432)
    database_user: str = Field(default="postgres")
    database_password: str = Field(default="password")
    database_name: str = Field(default="games")

    # Full database URL (optional, will be built from parameters if not provided)
    database_url: str = Field(default="")
    sql_echo: bool = Field(default=False)

    def get_alembic_database_url(self) -> str:
        """Build Alembic database URL from parameters"""
        if self.alembic_database_url:
            return self.alembic_database_url
        # URL encode password to handle special characters
        from urllib.parse import quote_plus

        encoded_password = quote_plus(self.database_password)
        host_port = f"{self.database_host}:{self.database_port}"
        return f"postgresql://{self.database_user}:{encoded_password}@{host_port}/{self.database_name}"

    def model_post_init(self, __context) -> None:
        """Build database_url from parameters if not provided"""
        if not self.database_url:
            # URL encode password to handle special characters
            from urllib.parse import quote_plus

            encoded_password = quote_plus(self.database_password)
            host_port = f"{self.database_host}:{self.database_port}"
            self.database_url = (
                f"postgresql+asyncpg://{self.database_user}:{encoded_password}@"
                f"{host_port}/{self.database_name}"
            )
            # Log for debugging (password hidden)
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                "Built DATABASE_URL from parameters",
                extra={
                    "database_host": self.database_host,
                    "database_port": self.database_port,
                    "database_user": self.database_user,
                    "database_name": self.database_name,
                    "database_password_length": len(self.database_password),
                    "database_url": self.database_url.replace(
                        f":{encoded_password}@", ":***@"
                    ),
                },
            )

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


@lru_cache
def load_settings() -> Settings:
    config_file = os.getenv("CONFIG_FILE") or os.getenv("APP_CONFIG")
    defaults = Settings()
    if config_file and os.path.exists(config_file):
        file_settings = Settings.from_toml(config_file)
        merged = file_settings.model_copy(update=defaults.model_dump(exclude_unset=True))
        return merged

    return defaults
