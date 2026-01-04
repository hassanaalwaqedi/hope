"""
HOPE Production Logging Configuration

Structured JSON logging for production environments with:
- Correlation ID tracking for request tracing
- Sensitive data redaction
- Configurable log levels per environment
- Human-readable format for development

SECURITY: All log processors include sensitive data filtering.
"""

import logging
import sys
from typing import Any

import structlog

from hope.config.settings import Settings


# Patterns to redact from logs
SENSITIVE_PATTERNS: frozenset[str] = frozenset({
    "password",
    "token",
    "secret",
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "private_key",
    "encryption_key",
})


def _redact_sensitive_data(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """
    Redact sensitive data from log entries.
    
    Scans all keys in the event dictionary and redacts values
    for any key containing sensitive patterns.
    
    Args:
        logger: Logger instance (unused but required by structlog)
        method_name: Log method name (unused but required by structlog)
        event_dict: Log event dictionary
        
    Returns:
        Sanitized event dictionary
    """
    def redact_value(key: str, value: Any) -> Any:
        key_lower = key.lower()
        for pattern in SENSITIVE_PATTERNS:
            if pattern in key_lower:
                return "[REDACTED]"
        
        if isinstance(value, dict):
            return {k: redact_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [redact_value(key, item) for item in value]
        
        return value
    
    return {key: redact_value(key, value) for key, value in event_dict.items()}


def _add_service_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Add service-level context to all log entries."""
    event_dict["service"] = "hope-backend"
    event_dict["version"] = "0.1.0"
    return event_dict


def get_processors(is_development: bool) -> list[Any]:
    """
    Get structlog processors based on environment.
    
    Args:
        is_development: Whether running in development mode
        
    Returns:
        List of log processors
    """
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        _redact_sensitive_data,
        _add_service_context,
    ]
    
    if is_development:
        # Human-readable console output for development
        shared_processors.extend([
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    else:
        # JSON output for production (log aggregation systems)
        shared_processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ])
    
    return shared_processors


def configure_logging(settings: Settings) -> None:
    """
    Configure application logging.
    
    Sets up structlog with appropriate processors for the environment.
    Should be called once during application startup.
    
    Args:
        settings: Application settings
    """
    is_development = settings.env == "development"
    log_level = getattr(logging, settings.log_level.upper())
    
    # Configure structlog
    structlog.configure(
        processors=get_processors(is_development),
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Set levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Context variable binding for request correlation
def bind_correlation_id(correlation_id: str) -> None:
    """
    Bind correlation ID to current context.
    
    All subsequent log entries in this context will include
    the correlation ID for request tracing.
    
    Args:
        correlation_id: Unique request identifier
    """
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def clear_context() -> None:
    """Clear all context variables (call at end of request)."""
    structlog.contextvars.clear_contextvars()
