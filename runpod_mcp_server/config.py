"""Configuration management for Runpod MCP Server."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunpodConfig(BaseSettings):
    """Configuration loaded from environment variables."""

    api_key: str = Field(..., description="Runpod API key")
    seedream_endpoint_id: str = Field(..., description="Seedream V4 T2I endpoint ID")
    nano_banana_endpoint_id: str = Field(..., description="Nano Banana Pro Edit endpoint ID")

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

    @field_validator('seedream_endpoint_id', 'nano_banana_endpoint_id')
    @classmethod
    def validate_endpoint_id(cls, v: str) -> str:
        """Validate endpoint ID format."""
        if not v or len(v.strip()) < 5:
            raise ValueError(
                "Invalid endpoint ID. "
                "Get your endpoint IDs from https://runpod.io/console/serverless"
            )
        return v.strip()
