"""Monitoring infrastructure package."""

# Optional: Sentry integration (requires sentry-sdk)
try:
    from hope.infrastructure.monitoring.sentry_integration import (
        init_sentry,
        set_user_context,
        set_panic_context,
        capture_safety_event,
        capture_exception_with_context,
    )
    SENTRY_AVAILABLE = True
except ImportError:
    # Provide no-op stubs when Sentry is not installed
    SENTRY_AVAILABLE = False
    
    def init_sentry(*args, **kwargs) -> None:
        pass
    
    def set_user_context(*args, **kwargs) -> None:
        pass
    
    def set_panic_context(*args, **kwargs) -> None:
        pass
    
    def capture_safety_event(*args, **kwargs) -> None:
        pass
    
    def capture_exception_with_context(*args, **kwargs) -> str:
        return ""

__all__ = [
    "init_sentry",
    "set_user_context",
    "set_panic_context",
    "capture_safety_event",
    "capture_exception_with_context",
    "SENTRY_AVAILABLE",
]
