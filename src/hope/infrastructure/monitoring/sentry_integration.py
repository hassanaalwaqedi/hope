"""
Sentry Error Tracking Integration

Production error tracking with sensitive data scrubbing.
Correlates errors with session IDs for debugging.

SECURITY: All sensitive fields are stripped before sending to Sentry.
"""

import re
from typing import Any, Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from hope.config.logging_config import get_logger

logger = get_logger(__name__)

# Patterns for sensitive data scrubbing
SENSITIVE_PATTERNS = [
    r"password[\"']?\s*[:=]\s*[\"']?[^\"'\s,}]+",
    r"api[_-]?key[\"']?\s*[:=]\s*[\"']?[^\"'\s,}]+",
    r"token[\"']?\s*[:=]\s*[\"']?[^\"'\s,}]+",
    r"secret[\"']?\s*[:=]\s*[\"']?[^\"'\s,}]+",
    r"bearer\s+[a-zA-Z0-9\-._~+/]+=*",
    r"authorization[\"']?\s*[:=]\s*[\"']?[^\"'\s,}]+",
]

SENSITIVE_KEYS = frozenset({
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
    "jwt",
    "session_token",
})


def _scrub_string(value: str) -> str:
    """Scrub sensitive patterns from string."""
    result = value
    for pattern in SENSITIVE_PATTERNS:
        result = re.sub(pattern, "[REDACTED]", result, flags=re.IGNORECASE)
    return result


def _scrub_dict(data: dict) -> dict:
    """Recursively scrub sensitive data from dictionary."""
    result = {}
    for key, value in data.items():
        key_lower = key.lower().replace("-", "_")
        
        if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = _scrub_dict(value)
        elif isinstance(value, list):
            result[key] = [
                _scrub_dict(item) if isinstance(item, dict)
                else _scrub_string(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, str):
            result[key] = _scrub_string(value)
        else:
            result[key] = value
    
    return result


def before_send(event: dict, hint: dict) -> Optional[dict]:
    """
    Process event before sending to Sentry.
    
    - Scrubs sensitive data
    - Adds context
    - Filters unwanted events
    """
    # Scrub request data
    if "request" in event:
        if "data" in event["request"]:
            event["request"]["data"] = _scrub_dict(event["request"]["data"])
        if "headers" in event["request"]:
            event["request"]["headers"] = _scrub_dict(event["request"]["headers"])
    
    # Scrub breadcrumbs
    if "breadcrumbs" in event:
        for breadcrumb in event.get("breadcrumbs", {}).get("values", []):
            if "data" in breadcrumb and isinstance(breadcrumb["data"], dict):
                breadcrumb["data"] = _scrub_dict(breadcrumb["data"])
    
    # Scrub extra context
    if "extra" in event:
        event["extra"] = _scrub_dict(event["extra"])
    
    return event


def before_breadcrumb(breadcrumb: dict, hint: dict) -> Optional[dict]:
    """Filter and sanitize breadcrumbs."""
    # Skip logging breadcrumbs that might contain sensitive data
    if breadcrumb.get("category") == "sql":
        # Keep SQL breadcrumbs but sanitize
        if "message" in breadcrumb:
            breadcrumb["message"] = _scrub_string(breadcrumb["message"])
    
    return breadcrumb


def init_sentry(
    dsn: str,
    environment: str = "development",
    release: str = "hope@0.1.0",
    sample_rate: float = 1.0,
    traces_sample_rate: float = 0.1,
) -> None:
    """
    Initialize Sentry error tracking.
    
    Args:
        dsn: Sentry DSN
        environment: Environment name
        release: Release version
        sample_rate: Error sample rate (1.0 = all errors)
        traces_sample_rate: Performance tracing rate
    """
    if not dsn:
        logger.warning("Sentry DSN not configured, error tracking disabled")
        return
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        sample_rate=sample_rate,
        traces_sample_rate=traces_sample_rate,
        before_send=before_send,
        before_breadcrumb=before_breadcrumb,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            AsyncioIntegration(),
            LoggingIntegration(
                level=None,  # Don't capture logs as breadcrumbs
                event_level=None,  # Don't capture logs as events
            ),
        ],
        # Don't send PII
        send_default_pii=False,
        # Attach stack trace to all messages
        attach_stacktrace=True,
        # Maximum breadcrumb count
        max_breadcrumbs=50,
    )
    
    logger.info(
        "Sentry initialized",
        environment=environment,
        release=release,
    )


def set_user_context(user_id: str, session_id: Optional[str] = None) -> None:
    """
    Set user context for error correlation.
    
    Uses anonymized IDs only - no PII.
    """
    sentry_sdk.set_user({
        "id": user_id,
        "session_id": session_id,
    })


def set_panic_context(
    session_id: str,
    severity: Optional[str] = None,
    risk_level: Optional[str] = None,
) -> None:
    """Set panic session context for debugging."""
    sentry_sdk.set_context("panic_session", {
        "session_id": session_id,
        "severity": severity,
        "risk_level": risk_level,
    })


def capture_safety_event(
    message: str,
    level: str = "warning",
    extra: Optional[dict] = None,
) -> None:
    """
    Capture safety-related event for monitoring.
    
    Used for tracking escalations, crisis signals, etc.
    """
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("category", "safety")
        if extra:
            for key, value in extra.items():
                scope.set_extra(key, value)
        
        if level == "error":
            sentry_sdk.capture_message(message, level="error")
        else:
            sentry_sdk.capture_message(message, level="warning")


def capture_exception_with_context(
    exception: Exception,
    session_id: Optional[str] = None,
    extra: Optional[dict] = None,
) -> str:
    """
    Capture exception with additional context.
    
    Returns: Sentry event ID
    """
    with sentry_sdk.push_scope() as scope:
        if session_id:
            scope.set_tag("session_id", session_id)
        if extra:
            for key, value in _scrub_dict(extra).items():
                scope.set_extra(key, value)
        
        return sentry_sdk.capture_exception(exception)
