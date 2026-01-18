from functools import lru_cache

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from ..custom_types import AppEnvironment
from .env import DevSettings, EnvironmentSettings, ProdSettings
from .logging_settings import LoggerSettings
from .toml import Logs, Network, Parsing, Retries, Selectors, Timeouts


class Config(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")
    environment: EnvironmentSettings = Field(
        default_factory=EnvironmentSettings
    )
    logs: Logs = Field(default_factory=Logs)
    selectors: Selectors = Field(default_factory=Selectors)  # type:ignore
    timeouts: Timeouts = Field(default_factory=Timeouts)
    network: Network = Field(default_factory=Network)
    retries: Retries = Field(default_factory=Retries)
    parsing: Parsing = Field(default_factory=Parsing)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


config = Config()


@lru_cache
def load() -> Config:
    """Load configuration with all values

    Returns:
        Config: Config Object
    """
    env = config.environment
    logs = config.logs
    _ = LoggerSettings(logs, env)
    if env == AppEnvironment.PROD:
        config.environment = ProdSettings()
    elif env == AppEnvironment.DEV:
        config.environment = DevSettings()
    return config
