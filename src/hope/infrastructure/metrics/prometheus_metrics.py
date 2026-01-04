"""
Prometheus Metrics

Production-grade metrics for HOPE system observability.
Exposes metrics at /metrics endpoint for Prometheus scraping.

ARCHITECTURE: Metrics are decoupled from business logic.
Only increment/observe; never block on metrics operations.
"""

import time
from functools import wraps
from typing import Callable, Optional

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)
from fastapi import APIRouter, Response

from hope.config.logging_config import get_logger

logger = get_logger(__name__)

# =============================================================================
# PANIC SESSION METRICS
# =============================================================================

PANIC_SESSIONS_TOTAL = Counter(
    "hope_panic_sessions_total",
    "Total number of panic sessions started",
    ["outcome"],  # resolved, escalated, abandoned
)

PANIC_SESSION_DURATION = Histogram(
    "hope_panic_session_duration_seconds",
    "Duration of panic sessions",
    ["outcome"],
    buckets=[30, 60, 120, 300, 600, 1800, 3600],  # 30s to 1h
)

ACTIVE_PANIC_SESSIONS = Gauge(
    "hope_active_panic_sessions",
    "Number of currently active panic sessions",
)

# =============================================================================
# ESCALATION METRICS
# =============================================================================

ESCALATION_EVENTS_TOTAL = Counter(
    "hope_escalation_events_total",
    "Total escalation events by level",
    ["from_level", "to_level"],
)

CRISIS_SIGNALS_DETECTED = Counter(
    "hope_crisis_signals_detected_total",
    "Crisis signals detected by type",
    ["signal_type"],  # emotional, behavioral, linguistic
)

RESOURCES_PROVIDED = Counter(
    "hope_emergency_resources_provided_total",
    "Emergency resources provided to users",
    ["country_code"],
)

# =============================================================================
# LLM METRICS
# =============================================================================

LLM_REQUESTS_TOTAL = Counter(
    "hope_llm_requests_total",
    "Total LLM requests by provider",
    ["provider", "status"],  # success, error, rate_limited
)

LLM_LATENCY = Histogram(
    "hope_llm_latency_seconds",
    "LLM response latency",
    ["provider"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
)

LLM_TOKENS_USED = Counter(
    "hope_llm_tokens_total",
    "Total tokens used by LLM",
    ["provider", "type"],  # input, output
)

# =============================================================================
# SAFETY PIPELINE METRICS
# =============================================================================

SAFETY_VALIDATIONS_TOTAL = Counter(
    "hope_safety_validations_total",
    "Safety validations performed",
    ["result"],  # passed, blocked, modified
)

RISK_ASSESSMENTS_TOTAL = Counter(
    "hope_risk_assessments_total",
    "Risk assessments by level",
    ["risk_level"],  # low, elevated, high, critical
)

RESPONSE_MODIFICATIONS = Counter(
    "hope_response_modifications_total",
    "Responses modified by safety pipeline",
    ["modification_type"],  # prefix_added, suffix_added, blocked
)

# =============================================================================
# API METRICS
# =============================================================================

HTTP_REQUESTS_TOTAL = Counter(
    "hope_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION = Histogram(
    "hope_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

WEBSOCKET_CONNECTIONS = Gauge(
    "hope_websocket_connections",
    "Active WebSocket connections",
)

RATE_LIMIT_EXCEEDED = Counter(
    "hope_rate_limit_exceeded_total",
    "Rate limit exceeded events",
    ["client_type"],  # ip, user
)

# =============================================================================
# SYSTEM INFO
# =============================================================================

SYSTEM_INFO = Info(
    "hope_system",
    "HOPE system information",
)

# Initialize system info
SYSTEM_INFO.info({
    "version": "0.1.0",
    "environment": "development",  # Updated at runtime
})


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def track_llm_request(provider: str) -> Callable:
    """Decorator to track LLM request metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                LLM_REQUESTS_TOTAL.labels(provider=provider, status="success").inc()
                
                # Track tokens if available
                if hasattr(result, 'usage'):
                    LLM_TOKENS_USED.labels(provider=provider, type="input").inc(
                        result.usage.get("prompt_tokens", 0)
                    )
                    LLM_TOKENS_USED.labels(provider=provider, type="output").inc(
                        result.usage.get("completion_tokens", 0)
                    )
                
                return result
            except Exception as e:
                error_type = "rate_limited" if "rate" in str(e).lower() else "error"
                LLM_REQUESTS_TOTAL.labels(provider=provider, status=error_type).inc()
                raise
            finally:
                duration = time.time() - start_time
                LLM_LATENCY.labels(provider=provider).observe(duration)
        return wrapper
    return decorator


def track_panic_session(session_id: str, outcome: str, duration_seconds: float) -> None:
    """Record panic session completion metrics."""
    PANIC_SESSIONS_TOTAL.labels(outcome=outcome).inc()
    PANIC_SESSION_DURATION.labels(outcome=outcome).observe(duration_seconds)


def track_escalation(from_level: str, to_level: str) -> None:
    """Record escalation event."""
    ESCALATION_EVENTS_TOTAL.labels(from_level=from_level, to_level=to_level).inc()


def track_safety_validation(result: str) -> None:
    """Record safety validation result."""
    SAFETY_VALIDATIONS_TOTAL.labels(result=result).inc()


def track_risk_assessment(risk_level: str) -> None:
    """Record risk assessment level."""
    RISK_ASSESSMENTS_TOTAL.labels(risk_level=risk_level).inc()


# =============================================================================
# METRICS ENDPOINT
# =============================================================================

metrics_router = APIRouter(tags=["metrics"])


@metrics_router.get("/metrics")
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus text format for scraping.
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )


def update_system_info(environment: str, version: str = "0.1.0") -> None:
    """Update system info metric with current environment."""
    SYSTEM_INFO.info({
        "version": version,
        "environment": environment,
    })
