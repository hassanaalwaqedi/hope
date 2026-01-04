"""
HOPE Configuration Module

Provides centralized configuration management with:
- Environment-based settings loading
- Validation of required values
- Secure handling of secrets
"""

from hope.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
