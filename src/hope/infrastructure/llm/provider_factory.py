"""
LLM Provider Factory

Factory for creating LLM providers based on configuration.
Enables switching between providers via environment variable.

CONFIGURATION:
    HOPE_LLM_PRIMARY_PROVIDER=gemini_flash  # or: openai, gemini
"""

from enum import StrEnum
from typing import Optional

from hope.config import get_settings
from hope.config.logging_config import get_logger
from hope.infrastructure.llm.provider import LLMProvider

logger = get_logger(__name__)


class LLMProviderType(StrEnum):
    """Supported LLM provider types."""
    
    OPENAI = "openai"
    GEMINI = "gemini"
    GEMINI_FLASH = "gemini_flash"


# Singleton instances for reuse
_provider_instances: dict[LLMProviderType, LLMProvider] = {}


def get_llm_provider(
    provider_type: Optional[LLMProviderType] = None,
    force_new: bool = False,
) -> LLMProvider:
    """
    Get LLM provider instance.
    
    Uses singleton pattern for efficiency. Provider type defaults
    to HOPE_LLM_PRIMARY_PROVIDER environment variable.
    
    Args:
        provider_type: Override provider type
        force_new: Create new instance instead of cached
        
    Returns:
        Configured LLM provider
        
    Raises:
        ValueError: If unknown provider type
        
    Example:
        # Use default from config
        provider = get_llm_provider()
        
        # Explicitly request Gemini Flash
        provider = get_llm_provider(LLMProviderType.GEMINI_FLASH)
    """
    # Determine provider type
    if provider_type is None:
        settings = get_settings()
        provider_str = settings.llm_primary_provider
        try:
            provider_type = LLMProviderType(provider_str)
        except ValueError:
            logger.warning(
                f"Unknown provider '{provider_str}', defaulting to gemini_flash"
            )
            provider_type = LLMProviderType.GEMINI_FLASH
    
    # Return cached instance if available
    if not force_new and provider_type in _provider_instances:
        return _provider_instances[provider_type]
    
    # Create new instance
    provider = _create_provider(provider_type)
    
    # Cache it
    if not force_new:
        _provider_instances[provider_type] = provider
    
    logger.info(
        "LLM provider initialized",
        provider=provider_type.value,
        configured=provider.is_configured(),
    )
    
    return provider


def _create_provider(provider_type: LLMProviderType) -> LLMProvider:
    """Create provider instance by type."""
    if provider_type == LLMProviderType.OPENAI:
        from hope.infrastructure.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    
    elif provider_type == LLMProviderType.GEMINI:
        from hope.infrastructure.llm.gemini_provider import GeminiProvider
        return GeminiProvider()
    
    elif provider_type == LLMProviderType.GEMINI_FLASH:
        from hope.infrastructure.llm.gemini_flash_provider import GeminiFlashProvider
        return GeminiFlashProvider()
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def clear_provider_cache() -> None:
    """Clear cached provider instances (for testing)."""
    global _provider_instances
    _provider_instances = {}
