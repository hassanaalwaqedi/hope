"""
Rate Limiting Middleware

Token bucket rate limiting for API protection.
Protects panic endpoints from abuse while ensuring availability.

ARCHITECTURE: Rate limits degrade gracefully - never block panic help.
"""

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Callable
import asyncio

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from hope.config.logging_config import get_logger
from hope.infrastructure.metrics import RATE_LIMIT_EXCEEDED

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    
    # Requests per minute for general API
    requests_per_minute: int = 60
    
    # Requests per minute for panic endpoints (higher limit)
    panic_requests_per_minute: int = 120
    
    # Burst allowance (tokens above limit)
    burst_size: int = 10
    
    # Window size in seconds
    window_seconds: int = 60
    
    # Whether to use sliding window
    sliding_window: bool = True


class TokenBucket:
    """Token bucket for rate limiting."""
    
    def __init__(
        self,
        rate: float,  # Tokens per second
        capacity: int,  # Maximum tokens
    ) -> None:
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Attempt to acquire tokens.
        
        Returns True if tokens acquired, False if rate limited.
        """
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            
            # Refill tokens
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    @property
    def available_tokens(self) -> int:
        """Get current available tokens."""
        return int(self.tokens)


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    
    Maintains separate buckets per client identifier.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None) -> None:
        self.config = config or RateLimitConfig()
        self._buckets: dict[str, TokenBucket] = defaultdict(self._create_bucket)
        self._panic_buckets: dict[str, TokenBucket] = defaultdict(self._create_panic_bucket)
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def _create_bucket(self) -> TokenBucket:
        """Create standard rate limit bucket."""
        rate = self.config.requests_per_minute / 60.0
        capacity = self.config.requests_per_minute + self.config.burst_size
        return TokenBucket(rate=rate, capacity=capacity)
    
    def _create_panic_bucket(self) -> TokenBucket:
        """Create panic endpoint bucket (higher limit)."""
        rate = self.config.panic_requests_per_minute / 60.0
        capacity = self.config.panic_requests_per_minute + self.config.burst_size
        return TokenBucket(rate=rate, capacity=capacity)
    
    async def check_rate_limit(
        self,
        client_id: str,
        is_panic_endpoint: bool = False,
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Returns:
            Tuple of (allowed, remaining_tokens)
        """
        buckets = self._panic_buckets if is_panic_endpoint else self._buckets
        bucket = buckets[client_id]
        
        allowed = await bucket.acquire()
        remaining = bucket.available_tokens
        
        if not allowed:
            client_type = "panic" if is_panic_endpoint else "standard"
            RATE_LIMIT_EXCEEDED.labels(client_type=client_type).inc()
            logger.warning(
                "Rate limit exceeded",
                client_id=client_id[:8] + "...",  # Truncate for privacy
                is_panic=is_panic_endpoint,
            )
        
        return allowed, remaining
    
    async def start_cleanup(self) -> None:
        """Start background task to clean up old buckets."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup(self) -> None:
        """Stop cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self) -> None:
        """Periodically clean up inactive buckets."""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            self._cleanup_inactive_buckets()
    
    def _cleanup_inactive_buckets(self) -> None:
        """Remove buckets that haven't been used recently."""
        now = time.monotonic()
        inactive_threshold = 600  # 10 minutes
        
        for buckets in [self._buckets, self._panic_buckets]:
            inactive_keys = [
                key for key, bucket in buckets.items()
                if now - bucket.last_update > inactive_threshold
            ]
            for key in inactive_keys:
                del buckets[key]


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    
    Applies different limits for panic vs standard endpoints.
    Never blocks /health or /metrics endpoints.
    """
    
    # Endpoints exempt from rate limiting
    EXEMPT_PATHS = frozenset({
        "/health",
        "/health/live",
        "/health/ready",
        "/metrics",
        "/docs",
        "/openapi.json",
    })
    
    # Panic-related paths (higher limits)
    PANIC_PATHS = frozenset({
        "/ws/panic",
        "/api/v1/panic",
        "/api/v1/session/panic",
    })
    
    def __init__(self, app, config: Optional[RateLimitConfig] = None) -> None:
        super().__init__(app)
        self.limiter = RateLimiter(config)
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        path = request.url.path
        
        # Skip rate limiting for exempt paths
        if path in self.EXEMPT_PATHS or path.startswith("/docs"):
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check if panic endpoint
        is_panic = any(path.startswith(p) for p in self.PANIC_PATHS)
        
        # Check rate limit
        allowed, remaining = await self.limiter.check_rate_limit(
            client_id,
            is_panic_endpoint=is_panic,
        )
        
        if not allowed:
            return Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60",
                },
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier for rate limiting.
        
        Uses authenticated user ID if available, otherwise IP.
        """
        # Check for authenticated user
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
