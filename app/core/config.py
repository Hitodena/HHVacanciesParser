from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from app.core.env import DevSettings, EnvironmentSettings, ProdSettings
from app.core.toml import Logs, Network, Parsing, Retries, Selectors, Timeouts


class Config(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")
    environment: EnvironmentSettings = Field(
        default_factory=EnvironmentSettings
    )
    logs: Logs = Field(default_factory=Logs)
    selectors: Selectors = Field(default_factory=Selectors)
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

    @classmethod
    def load(cls) -> "Config":
        env = EnvironmentSettings().app_environment
        if env == "prod":
            cls.environment = ProdSettings()
        elif env == "dev":
            cls.environment = DevSettings()
        return cls()
