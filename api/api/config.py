"""This module provides functions for managing the configuration."""

import functools

import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    """This class represents the app configuration."""

    NL_VERSION: str = '0.1.0'

    NL_API_URL: str = ''
    NL_API_SECRET_KEY: str = ''
    NL_API_ALGORITHM: str = 'HS256'
    NL_API_ACCESS_TOKEN_EXPIRE_MINUTES: int = 240
    NL_API_POSTGRES_URI: str = (
        'postgresql+asyncpg://netolight:netolight@localhost:5432/nl'
    )
    NL_REDIS_URL: str = 'redis://localhost:6379'

    NL_DIMMER_HOST: str = 'dimmer'
    NL_DIMMER_PORT: int = 4000

    CHIRPSTACK_SERVER_URL: str = 'chripstack:3000'
    CHIRPSTACK_SERVER_JWT_TOKEN: str = ''

    model_config = pydantic_settings.SettingsConfigDict(
        env_file='.env', extra='ignore'
    )


@functools.lru_cache
def get_settings() -> Settings:
    """Get the settings."""
    return Settings()
