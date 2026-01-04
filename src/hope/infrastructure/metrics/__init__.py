"""Metrics infrastructure package."""

from hope.infrastructure.metrics.prometheus_metrics import (
    # Panic metrics
    PANIC_SESSIONS_TOTAL,
    PANIC_SESSION_DURATION,
    ACTIVE_PANIC_SESSIONS,
    # Escalation metrics
    ESCALATION_EVENTS_TOTAL,
    CRISIS_SIGNALS_DETECTED,
    RESOURCES_PROVIDED,
    # LLM metrics
    LLM_REQUESTS_TOTAL,
    LLM_LATENCY,
    LLM_TOKENS_USED,
    # Safety metrics
    SAFETY_VALIDATIONS_TOTAL,
    RISK_ASSESSMENTS_TOTAL,
    RESPONSE_MODIFICATIONS,
    # API metrics
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION,
    WEBSOCKET_CONNECTIONS,
    RATE_LIMIT_EXCEEDED,
    # Helpers
    track_llm_request,
    track_panic_session,
    track_escalation,
    track_safety_validation,
    track_risk_assessment,
    update_system_info,
    # Router
    metrics_router,
)

__all__ = [
    "PANIC_SESSIONS_TOTAL",
    "PANIC_SESSION_DURATION",
    "ACTIVE_PANIC_SESSIONS",
    "ESCALATION_EVENTS_TOTAL",
    "CRISIS_SIGNALS_DETECTED",
    "RESOURCES_PROVIDED",
    "LLM_REQUESTS_TOTAL",
    "LLM_LATENCY",
    "LLM_TOKENS_USED",
    "SAFETY_VALIDATIONS_TOTAL",
    "RISK_ASSESSMENTS_TOTAL",
    "RESPONSE_MODIFICATIONS",
    "HTTP_REQUESTS_TOTAL",
    "HTTP_REQUEST_DURATION",
    "WEBSOCKET_CONNECTIONS",
    "RATE_LIMIT_EXCEEDED",
    "track_llm_request",
    "track_panic_session",
    "track_escalation",
    "track_safety_validation",
    "track_risk_assessment",
    "update_system_info",
    "metrics_router",
]
