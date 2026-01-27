"""
HOPE Production Observability

Monitoring, metrics, and error tracking for production deployment.
Integrates with Sentry for error tracking and provides custom metrics
for AI latency, panic triggers, and safety events.

CRITICAL: This is a mental health application. All monitoring
prioritizes user safety and privacy over diagnostic detail.
"""

import time
import functools
from typing import Any, Callable, Optional
from datetime import datetime
from contextlib import contextmanager

import structlog

from hope.config.settings import get_settings

logger = structlog.get_logger(__name__)

# =============================================================================
# SENTRY INTEGRATION
# =============================================================================

_sentry_initialized = False

def init_sentry() -> bool:
    """
    Initialize Sentry error tracking if configured.
    
    Returns:
        True if Sentry was initialized, False otherwise
    """
    global _sentry_initialized
    
    if _sentry_initialized:
        return True
    
    settings = get_settings()
    sentry_dsn = getattr(settings, 'sentry_dsn', None)
    
    if not sentry_dsn:
        logger.info("Sentry DSN not configured, error tracking disabled")
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=getattr(settings, 'sentry_environment', settings.env),
            traces_sample_rate=getattr(settings, 'sentry_traces_sample_rate', 0.1),
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
            ],
            # Privacy: Don't send user PII
            send_default_pii=False,
            # Safety: Tag mental health context
            before_send=_before_send_filter,
        )
        
        _sentry_initialized = True
        logger.info("Sentry error tracking initialized", environment=settings.env)
        return True
        
    except ImportError:
        logger.warning("sentry-sdk not installed, error tracking disabled")
        return False
    except Exception as e:
        logger.error("Failed to initialize Sentry", error=str(e))
        return False


def _before_send_filter(event: dict, hint: dict) -> Optional[dict]:
    """
    Filter events before sending to Sentry.
    
    PRIVACY: Removes any potentially sensitive user content
    while preserving error context for debugging.
    """
    # Remove user message content from breadcrumbs
    if 'breadcrumbs' in event:
        for crumb in event.get('breadcrumbs', {}).get('values', []):
            if 'data' in crumb:
                # Redact any message content
                if 'message' in crumb['data']:
                    crumb['data']['message'] = '[REDACTED]'
                if 'transcript' in crumb['data']:
                    crumb['data']['transcript'] = '[REDACTED]'
    
    # Tag as mental health app for special handling
    event.setdefault('tags', {})['app_type'] = 'mental_health'
    
    return event


def capture_exception(
    error: Exception,
    context: Optional[dict] = None,
    level: str = "error",
) -> None:
    """
    Capture exception to Sentry with context.
    
    Args:
        error: Exception to capture
        context: Additional context (will be sanitized)
        level: Sentry level (error, warning, info)
    """
    if not _sentry_initialized:
        logger.error("Exception occurred", error=str(error), exc_info=True)
        return
    
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            if context:
                # Sanitize context before sending
                safe_context = _sanitize_context(context)
                for key, value in safe_context.items():
                    scope.set_extra(key, value)
            
            scope.set_level(level)
            sentry_sdk.capture_exception(error)
            
    except Exception as e:
        logger.error("Failed to capture exception to Sentry", error=str(e))


def _sanitize_context(context: dict) -> dict:
    """Remove sensitive data from context before sending to Sentry."""
    sensitive_keys = {'message', 'transcript', 'content', 'user_input', 'response'}
    
    return {
        k: '[REDACTED]' if k.lower() in sensitive_keys else v
        for k, v in context.items()
    }


# =============================================================================
# METRICS COLLECTION
# =============================================================================

class BetaMetrics:
    """
    Metrics collector for beta monitoring.
    
    Tracks critical metrics for safety and performance:
    - AI response latency
    - Panic trigger events
    - False positive rates
    - Crisis escalation counts
    """
    
    def __init__(self):
        self._metrics = {
            'ai_requests_total': 0,
            'ai_latency_sum_ms': 0,
            'ai_errors_total': 0,
            'panic_triggers_total': 0,
            'panic_triggers_verbal': 0,
            'panic_triggers_non_verbal': 0,
            'panic_false_positives': 0,
            'crisis_escalations_total': 0,
            'safety_filters_triggered': 0,
            'sessions_active': 0,
            'sessions_total': 0,
        }
        self._start_time = datetime.utcnow()
    
    def record_ai_request(self, latency_ms: float, success: bool = True) -> None:
        """Record an AI request with latency."""
        self._metrics['ai_requests_total'] += 1
        self._metrics['ai_latency_sum_ms'] += latency_ms
        
        if not success:
            self._metrics['ai_errors_total'] += 1
        
        logger.info(
            "AI request completed",
            latency_ms=round(latency_ms, 2),
            success=success,
            metric_type="ai_latency",
        )
    
    def record_panic_trigger(
        self,
        trigger_type: str,  # 'verbal', 'non_verbal', 'button'
        false_positive: bool = False,
    ) -> None:
        """Record a panic trigger event."""
        self._metrics['panic_triggers_total'] += 1
        
        if trigger_type == 'verbal':
            self._metrics['panic_triggers_verbal'] += 1
        elif trigger_type == 'non_verbal':
            self._metrics['panic_triggers_non_verbal'] += 1
        
        if false_positive:
            self._metrics['panic_false_positives'] += 1
        
        logger.info(
            "Panic trigger recorded",
            trigger_type=trigger_type,
            false_positive=false_positive,
            metric_type="panic_trigger",
        )
    
    def record_crisis_escalation(self, severity: str) -> None:
        """Record a crisis escalation event."""
        self._metrics['crisis_escalations_total'] += 1
        
        logger.warning(
            "Crisis escalation recorded",
            severity=severity,
            metric_type="crisis_escalation",
        )
    
    def record_safety_filter(self, filter_type: str, language: str) -> None:
        """Record a safety filter trigger."""
        self._metrics['safety_filters_triggered'] += 1
        
        logger.info(
            "Safety filter triggered",
            filter_type=filter_type,
            language=language,
            metric_type="safety_filter",
        )
    
    def record_session_start(self) -> None:
        """Record session start."""
        self._metrics['sessions_active'] += 1
        self._metrics['sessions_total'] += 1
    
    def record_session_end(self) -> None:
        """Record session end."""
        self._metrics['sessions_active'] = max(0, self._metrics['sessions_active'] - 1)
    
    def get_metrics(self) -> dict:
        """Get current metrics snapshot."""
        metrics = dict(self._metrics)
        
        # Calculate derived metrics
        if metrics['ai_requests_total'] > 0:
            metrics['ai_latency_avg_ms'] = round(
                metrics['ai_latency_sum_ms'] / metrics['ai_requests_total'], 2
            )
        else:
            metrics['ai_latency_avg_ms'] = 0
        
        if metrics['panic_triggers_total'] > 0:
            metrics['false_positive_rate'] = round(
                metrics['panic_false_positives'] / metrics['panic_triggers_total'], 4
            )
        else:
            metrics['false_positive_rate'] = 0
        
        metrics['uptime_seconds'] = (datetime.utcnow() - self._start_time).total_seconds()
        
        return metrics
    
    def get_health_status(self) -> dict:
        """Get health status for monitoring."""
        metrics = self.get_metrics()
        
        # Define health thresholds
        is_healthy = (
            metrics['ai_latency_avg_ms'] < 5000 and  # <5s average
            metrics['false_positive_rate'] < 0.2     # <20% false positives
        )
        
        return {
            'status': 'healthy' if is_healthy else 'degraded',
            'ai_latency_avg_ms': metrics['ai_latency_avg_ms'],
            'false_positive_rate': metrics['false_positive_rate'],
            'active_sessions': metrics['sessions_active'],
            'crisis_escalations': metrics['crisis_escalations_total'],
            'uptime_seconds': metrics['uptime_seconds'],
        }


# Global metrics instance
_metrics = BetaMetrics()


def get_metrics() -> BetaMetrics:
    """Get global metrics instance."""
    return _metrics


# =============================================================================
# TIMING UTILITIES
# =============================================================================

@contextmanager
def timed_operation(operation_name: str):
    """
    Context manager for timing operations.
    
    Usage:
        with timed_operation("ai_response"):
            result = await generate_response(...)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug(
            f"{operation_name} completed",
            operation=operation_name,
            duration_ms=round(elapsed_ms, 2),
        )


def timed(func: Callable) -> Callable:
    """
    Decorator for timing functions.
    
    Usage:
        @timed
        async def my_function():
            ...
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.debug(
                f"{func.__name__} completed",
                function=func.__name__,
                duration_ms=round(elapsed_ms, 2),
            )
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(
                f"{func.__name__} failed",
                function=func.__name__,
                duration_ms=round(elapsed_ms, 2),
                error=str(e),
            )
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.debug(
                f"{func.__name__} completed",
                function=func.__name__,
                duration_ms=round(elapsed_ms, 2),
            )
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(
                f"{func.__name__} failed",
                function=func.__name__,
                duration_ms=round(elapsed_ms, 2),
                error=str(e),
            )
            raise
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
