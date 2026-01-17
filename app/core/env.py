from typing import Sequence

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import ENV_FILE
from app.types import AppEnvironment, LogLevel


class EnvironmentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_environment: AppEnvironment = Field(default=AppEnvironment.DEV)
    debug: bool = Field(default=True)
    log_level: LogLevel = Field(default=LogLevel.DEBUG)
    file_log_level: LogLevel = Field(default=LogLevel.INFO)

    redis_url: str = Field(default="redis://localhost:6379")
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")
    celery_cache: str = Field(default="redis://localhost:6379/3")

    cors_allow_origins: Sequence[str] = Field(default=["*"])

    log_console_formatter: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level> |"
        "<yellow>({extra})</yellow>"
    )
    log_file_formatter: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | "
        "{level} | "
        "{name}:{function}:{line} | "
        "{message} | {extra}"
    )


class ProdSettings(EnvironmentSettings):
    debug: bool = Field(default=False)
    log_level: LogLevel = Field(default=LogLevel.INFO)
    cors_allow_origins: Sequence[str] = Field(default=["*"])
    cors_allow_credentials: bool = Field(default=True)


class DevSettings(EnvironmentSettings):
    debug: bool = Field(default=True)
    log_level: LogLevel = Field(default=LogLevel.DEBUG)
    cors_allow_origins: Sequence[str] = Field(default=["*"])
    cors_allow_credentials: bool = Field(default=True)
