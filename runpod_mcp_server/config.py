"""Configuration management for Runpod MCP Server."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunpodConfig(BaseSettings):
    """Configuration loaded from environment variables."""

    api_key: str = Field(..., description="Runpod API key")

    model_config = SettingsConfigDict(
        env_prefix='RUNPOD_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or len(v.strip()) < 10:
            raise ValueError(
                "Invalid RUNPOD_API_KEY. "
                "Get your API key from https://runpod.io/console/user/settings"
            )
        return v.strip()
