"""
Error Handler Middleware

Provides consistent error handling and response formatting.
Logs errors with correlation IDs for debugging.
"""

import traceback
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from hope.config.logging_config import get_logger, bind_correlation_id, clear_context

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware.
    
    Provides:
    - Correlation ID tracking for all requests
    - Consistent error response format
    - Error logging with context
    - Sensitive data protection in errors
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process request with error handling."""
        
        # Generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        bind_correlation_id(correlation_id)
        
        try:
            response = await call_next(request)
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Log error with full context
            logger.error(
                "Unhandled exception",
                path=request.url.path,
                method=request.method,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=traceback.format_exc(),
            )
            
            # Return sanitized error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "correlation_id": correlation_id,
                    "message": "An unexpected error occurred. Please try again.",
                },
                headers={"X-Correlation-ID": correlation_id},
            )
            
        finally:
            clear_context()
