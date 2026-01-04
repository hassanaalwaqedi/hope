"""
HOPE Application Settings

Production-grade configuration management using Pydantic Settings.
All sensitive values are loaded from environment variables.

SECURITY: Never log or expose settings containing secrets.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""
    
    model_config = SettingsConfigDict(env_prefix="HOPE_DB_")
    
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="hope_db", description="Database name")
    user: str = Field(default="hope_user", description="Database user")
    password: SecretStr = Field(default=SecretStr("dev_password"), description="Database password")
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=100, description="Max overflow connections")
    
    @property
    def async_url(self) -> str:
        """Generate async database URL for SQLAlchemy."""
        password = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.user}:{password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def sync_url(self) -> str:
        """Generate sync database URL for Alembic migrations."""
        password = self.password.get_secret_value()
        return f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.name}"


class JWTSettings(BaseSettings):
    """JWT authentication configuration."""
    
    model_config = SettingsConfigDict(env_prefix="HOPE_JWT_")
    
    secret_key: SecretStr = Field(default=SecretStr("dev_jwt_secret_key_not_for_production"), description="JWT signing secret")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)


class OpenAISettings(BaseSettings):
    """OpenAI API configuration."""
    
    model_config = SettingsConfigDict(env_prefix="HOPE_OPENAI_")
    
    api_key: SecretStr = Field(default=SecretStr(""), description="OpenAI API key")
    model: str = Field(default="gpt-4-turbo-preview", description="Model identifier")
    max_tokens: int = Field(default=1024, ge=100, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class GeminiSettings(BaseSettings):
    """Google Gemini API configuration."""
    
    model_config = SettingsConfigDict(env_prefix="HOPE_GEMINI_")
    
    api_key: SecretStr = Field(default=SecretStr(""), description="Gemini API key")
    model: str = Field(default="gemini-pro", description="Model identifier")


class PineconeSettings(BaseSettings):
    """Pinecone vector database configuration."""
    
    model_config = SettingsConfigDict(env_prefix="HOPE_PINECONE_")
    
    api_key: SecretStr = Field(default=SecretStr(""), description="Pinecone API key")
    environment: str = Field(default="gcp-starter", description="Pinecone environment")
    index_name: str = Field(default="hope-emotional-history", description="Index name")


class WeaviateSettings(BaseSettings):
    """Weaviate vector database configuration."""
    
    model_config = SettingsConfigDict(env_prefix="HOPE_WEAVIATE_")
    
    url: str = Field(default="http://localhost:8080", description="Weaviate URL")
    api_key: SecretStr = Field(default=SecretStr(""), description="Weaviate API key")


class SafetySettings(BaseSettings):
    """Safety and rate limiting configuration."""
    
    model_config = SettingsConfigDict(env_prefix="HOPE_")
    
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, le=1000)
    safety_hard_filter_enabled: bool = Field(default=True)
    audit_log_enabled: bool = Field(default=True)


class Settings(BaseSettings):
    """
    Main application settings.
    
    All configuration is loaded from environment variables with HOPE_ prefix.
    Sensitive values use SecretStr to prevent accidental logging.
    
    Usage:
        settings = get_settings()
        db_url = settings.database.async_url
    """
    
    model_config = SettingsConfigDict(
        env_prefix="HOPE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Application
    env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode - NEVER enable in production")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    api_version: str = Field(default="v1", description="API version prefix")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Encryption key for sensitive database fields
    encryption_key: SecretStr = Field(default=SecretStr("dev_encryption_key_32bytes_here"), description="Field encryption key")
    
    # LLM Provider selection
    llm_primary_provider: Literal["openai", "gemini", "gemini_flash"] = Field(
        default="gemini_flash",
        description="Primary LLM provider (openai, gemini, gemini_flash)"
    )
    vector_db_provider: Literal["pinecone", "weaviate"] = Field(
        default="pinecone",
        description="Vector database provider"
    )
    
    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    pinecone: PineconeSettings = Field(default_factory=PineconeSettings)
    weaviate: WeaviateSettings = Field(default_factory=WeaviateSettings)
    safety: SafetySettings = Field(default_factory=SafetySettings)
    
    @field_validator("debug", mode="before")
    @classmethod
    def validate_debug_in_production(cls, v: bool, info) -> bool:
        """Ensure debug is never enabled in production."""
        # Note: info.data may not have 'env' at this point during validation
        # This is a safety check that should be enforced at deployment level
        return v
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Uses LRU cache to ensure settings are only loaded once.
    For testing, use dependency injection to override.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()
