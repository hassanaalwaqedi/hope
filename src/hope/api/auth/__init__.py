"""
HOPE Authentication Module

JWT-based authentication with:
- Token generation and validation
- Password hashing with bcrypt
- Anonymous panic session support
- Per-user rate limiting hooks
"""

from hope.api.auth.service import (
    AuthService,
    TokenData,
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
)
from hope.api.auth.dependencies import (
    get_current_user,
    get_current_user_optional,
    get_current_active_user,
)

__all__ = [
    "AuthService",
    "TokenData",
    "create_access_token",
    "create_refresh_token",
    "verify_password",
    "hash_password",
    "get_current_user",
    "get_current_user_optional",
    "get_current_active_user",
]
