"""
HOPE API Rate Limiting Middleware

Protects API endpoints from abuse while ensuring genuine users
in distress can always access help.

SAFETY PRIORITY:
- Crisis endpoints are never rate limited
- Panic triggers bypass normal limits
- Rate limits are per-user, not global
"""

import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

import structlog

logger = structlog.get_logger(__name__)


# =============================================================================
# RATE LIMIT CONFIGURATION
# =============================================================================

@dataclass
class RateLimitConfig:
    """Rate limit configuration per endpoint type."""
    
    # General API endpoints
    default_requests_per_minute: int = 60
    default_burst: int = 10
    
    # Chat endpoints (more restrictive to prevent abuse)
    chat_requests_per_minute: int = 30
    chat_burst: int = 5
    
    # Voice endpoints (moderate - real-time needed)
    voice_requests_per_minute: int = 20
    voice_burst: int = 3
    
    # Auth endpoints (strict - prevent brute force)
    auth_requests_per_minute: int = 10
    auth_burst: int = 3
    
    # Endpoints that are NEVER rate limited
    exempt_paths: Tuple[str, ...] = (
        "/health",
        "/metrics",
        "/api/v1/crisis",  # Crisis endpoints always accessible
    )
    
    # Endpoints with relaxed limits during panic
    panic_mode_paths: Tuple[str, ...] = (
        "/api/v1/chat",
        "/api/v1/voice",
        "/api/v1/session",
    )


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    
    tokens: float
    max_tokens: int
    refill_rate: float  # tokens per second
    last_update: float = field(default_factory=time.time)
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens. Returns True if successful.
        """
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        
        # Refill tokens
        self.tokens = min(
            self.max_tokens,
            self.tokens + elapsed * self.refill_rate
        )
        
        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def time_until_available(self) -> float:
        """Seconds until a token will be available."""
        if self.tokens >= 1:
            return 0
        
        return (1 - self.tokens) / self.refill_rate


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    In-memory rate limiter using token bucket algorithm.
    
    For production at scale, replace with Redis-based implementation.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self._buckets: Dict[str, TokenBucket] = {}
        self._panic_mode_users: set = set()
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
    
    def _get_bucket_key(self, identifier: str, endpoint_type: str) -> str:
        """Generate unique bucket key."""
        return f"{identifier}:{endpoint_type}"
    
    def _get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type from path."""
        if path.startswith("/api/v1/chat"):
            return "chat"
        elif path.startswith("/api/v1/voice"):
            return "voice"
        elif path.startswith("/api/v1/auth"):
            return "auth"
        else:
            return "default"
    
    def _get_limits(self, endpoint_type: str) -> Tuple[int, int]:
        """Get rate limit and burst for endpoint type."""
        if endpoint_type == "chat":
            return self.config.chat_requests_per_minute, self.config.chat_burst
        elif endpoint_type == "voice":
            return self.config.voice_requests_per_minute, self.config.voice_burst
        elif endpoint_type == "auth":
            return self.config.auth_requests_per_minute, self.config.auth_burst
        else:
            return self.config.default_requests_per_minute, self.config.default_burst
    
    def _get_or_create_bucket(
        self,
        identifier: str,
        endpoint_type: str,
    ) -> TokenBucket:
        """Get or create token bucket for identifier."""
        key = self._get_bucket_key(identifier, endpoint_type)
        
        if key not in self._buckets:
            requests_per_minute, burst = self._get_limits(endpoint_type)
            self._buckets[key] = TokenBucket(
                tokens=float(burst),
                max_tokens=burst,
                refill_rate=requests_per_minute / 60.0,
            )
        
        return self._buckets[key]
    
    def is_exempt(self, path: str) -> bool:
        """Check if path is exempt from rate limiting."""
        return any(path.startswith(exempt) for exempt in self.config.exempt_paths)
    
    def set_panic_mode(self, identifier: str, enabled: bool = True) -> None:
        """
        Enable/disable panic mode for a user.
        
        In panic mode, rate limits are significantly relaxed
        to ensure the user can access help.
        """
        if enabled:
            self._panic_mode_users.add(identifier)
            logger.info("Panic mode enabled for user", user_id=identifier[:8])
        else:
            self._panic_mode_users.discard(identifier)
    
    def check_rate_limit(
        self,
        identifier: str,
        path: str,
    ) -> Tuple[bool, Optional[float]]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            identifier: User/token identifier
            path: Request path
            
        Returns:
            (allowed, retry_after_seconds)
        """
        # Cleanup old buckets periodically
        self._maybe_cleanup()
        
        # Exempt paths always allowed
        if self.is_exempt(path):
            return True, None
        
        # Panic mode users get relaxed limits on panic paths
        if identifier in self._panic_mode_users:
            if any(path.startswith(p) for p in self.config.panic_mode_paths):
                # Double the normal limits for panic mode
                endpoint_type = self._get_endpoint_type(path)
                bucket = self._get_or_create_bucket(identifier, f"{endpoint_type}_panic")
                if bucket.consume():
                    return True, None
                # Even in panic mode, still track but always allow
                return True, None
        
        # Normal rate limiting
        endpoint_type = self._get_endpoint_type(path)
        bucket = self._get_or_create_bucket(identifier, endpoint_type)
        
        if bucket.consume():
            return True, None
        
        retry_after = bucket.time_until_available()
        
        logger.warning(
            "Rate limit exceeded",
            identifier=identifier[:8] if len(identifier) > 8 else identifier,
            endpoint_type=endpoint_type,
            retry_after=round(retry_after, 2),
        )
        
        return False, retry_after
    
    def _maybe_cleanup(self) -> None:
        """Clean up old buckets to prevent memory growth."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = now
        
        # Remove buckets that haven't been used in 10 minutes
        stale_threshold = now - 600
        stale_keys = [
            key for key, bucket in self._buckets.items()
            if bucket.last_update < stale_threshold
        ]
        
        for key in stale_keys:
            del self._buckets[key]
        
        if stale_keys:
            logger.debug("Cleaned up stale rate limit buckets", count=len(stale_keys))


# =============================================================================
# FASTAPI MIDDLEWARE
# =============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    
    Identifies users by:
    1. JWT token (if authenticated)
    2. IP address (fallback)
    """
    
    def __init__(self, app, config: Optional[RateLimitConfig] = None):
        super().__init__(app)
        self.limiter = RateLimiter(config)
    
    def _get_identifier(self, request: Request) -> str:
        """Extract user identifier from request."""
        # Try to get user ID from auth header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Use token hash as identifier (don't log actual token)
            token = auth_header[7:]
            return f"token:{hash(token) % 1000000:06d}"
        
        # Fallback to client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # First IP in chain is original client
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        identifier = self._get_identifier(request)
        path = request.url.path
        
        allowed, retry_after = self.limiter.check_rate_limit(identifier, path)
        
        if not allowed:
            return Response(
                content='{"detail": "Too many requests. Please wait before trying again."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": str(int(retry_after or 60)),
                    "Content-Type": "application/json",
                },
            )
        
        response = await call_next(request)
        
        # Add rate limit headers (optional, for client awareness)
        # response.headers["X-RateLimit-Remaining"] = str(...)
        
        return response


# =============================================================================
# DEPENDENCY FOR ROUTE-LEVEL LIMITING
# =============================================================================

_global_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = RateLimiter()
    return _global_limiter


async def check_rate_limit(request: Request) -> None:
    """
    Dependency for checking rate limit on specific routes.
    
    Usage:
        @router.post("/chat", dependencies=[Depends(check_rate_limit)])
        async def chat():
            ...
    """
    limiter = get_rate_limiter()
    
    # Extract identifier
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        identifier = f"token:{hash(auth_header[7:]) % 1000000:06d}"
    else:
        client_ip = request.client.host if request.client else "unknown"
        identifier = f"ip:{client_ip}"
    
    allowed, retry_after = limiter.check_rate_limit(identifier, request.url.path)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Please wait {int(retry_after or 60)} seconds.",
            headers={"Retry-After": str(int(retry_after or 60))},
        )
