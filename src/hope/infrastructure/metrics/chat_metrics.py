"""
Chat Metrics

Prometheus metrics for AI chat observability:
- gemini_chat_requests_total: Total chat API requests
- gemini_image_requests_total: Total image analysis requests
- gemini_request_latency_seconds: Response latency histogram
"""

from typing import Optional

# Try to import prometheus_client, fall back to no-op if not available
try:
    from prometheus_client import Counter, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


# Define metrics
if PROMETHEUS_AVAILABLE:
    CHAT_REQUESTS_TOTAL = Counter(
        "gemini_chat_requests_total",
        "Total number of Gemini chat API requests",
        ["status"],
    )
    
    IMAGE_REQUESTS_TOTAL = Counter(
        "gemini_image_requests_total", 
        "Total number of Gemini image analysis requests",
        ["status"],
    )
    
    CHAT_LATENCY = Histogram(
        "gemini_request_latency_seconds",
        "Gemini API request latency in seconds",
        buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )
else:
    CHAT_REQUESTS_TOTAL = None
    IMAGE_REQUESTS_TOTAL = None
    CHAT_LATENCY = None


def increment_chat_requests(status: str = "success") -> None:
    """Increment chat requests counter."""
    if CHAT_REQUESTS_TOTAL:
        CHAT_REQUESTS_TOTAL.labels(status=status).inc()


def increment_image_requests(status: str = "success") -> None:
    """Increment image requests counter."""
    if IMAGE_REQUESTS_TOTAL:
        IMAGE_REQUESTS_TOTAL.labels(status=status).inc()


def observe_chat_latency(latency_seconds: float) -> None:
    """Observe chat request latency."""
    if CHAT_LATENCY:
        CHAT_LATENCY.observe(latency_seconds)


def get_metrics_summary() -> dict:
    """Get current metrics summary for debugging."""
    return {
        "prometheus_available": PROMETHEUS_AVAILABLE,
        "metrics_defined": CHAT_REQUESTS_TOTAL is not None,
    }
