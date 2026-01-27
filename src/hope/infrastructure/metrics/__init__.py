"""Metrics infrastructure package.

Provides Prometheus metrics with graceful fallback when prometheus_client
is not installed.
"""

# Try to import prometheus metrics, provide no-ops if not available
try:
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
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Prometheus client not installed - provide no-op fallbacks
    PROMETHEUS_AVAILABLE = False
    
    PANIC_SESSIONS_TOTAL = None
    PANIC_SESSION_DURATION = None
    ACTIVE_PANIC_SESSIONS = None
    ESCALATION_EVENTS_TOTAL = None
    CRISIS_SIGNALS_DETECTED = None
    RESOURCES_PROVIDED = None
    LLM_REQUESTS_TOTAL = None
    LLM_LATENCY = None
    LLM_TOKENS_USED = None
    SAFETY_VALIDATIONS_TOTAL = None
    RISK_ASSESSMENTS_TOTAL = None
    RESPONSE_MODIFICATIONS = None
    HTTP_REQUESTS_TOTAL = None
    HTTP_REQUEST_DURATION = None
    WEBSOCKET_CONNECTIONS = None
    RATE_LIMIT_EXCEEDED = None
    
    # No-op helper functions
    def track_llm_request(*args, **kwargs): pass
    def track_panic_session(*args, **kwargs): pass
    def track_escalation(*args, **kwargs): pass
    def track_safety_validation(*args, **kwargs): pass
    def track_risk_assessment(*args, **kwargs): pass
    def update_system_info(*args, **kwargs): pass
    
    metrics_router = None

__all__ = [
    "PROMETHEUS_AVAILABLE",
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
