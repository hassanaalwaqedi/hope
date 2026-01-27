"""
Authentication Dependencies

FastAPI dependencies for authentication and authorization.
Supports both required and optional authentication.

ARCHITECTURE: Panic endpoints use optional auth to allow
anonymous crisis access with minimal friction.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hope.api.auth.service import decode_token, TokenData
from hope.infrastructure.database import get_async_session
from hope.infrastructure.database.models.user_model import UserModel
from hope.config.logging_config import get_logger

logger = get_logger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserModel:
    """
    Get the current authenticated user.
    
    Raises 401 if not authenticated.
    
    Args:
        credentials: Bearer token from request
        session: Database session
        
    Returns:
        UserModel of authenticated user
        
    Raises:
        HTTPException: 401 if not authenticated
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token_data = decode_token(credentials.credentials)
    
    if not token_data:
        raise credentials_exception
    
    if not token_data.user_id:
        raise credentials_exception
    
    # Get user from database
    result = await session.execute(
        select(UserModel).where(
            UserModel.id == token_data.user_id,
            UserModel.deleted_at == None,
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise credentials_exception
    
    return user


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Optional[UserModel]:
    """
    Get the current user if authenticated, None otherwise.
    
    Used for endpoints that support both authenticated and
    anonymous access (e.g., panic flow).
    
    Args:
        credentials: Optional bearer token
        session: Database session
        
    Returns:
        UserModel if authenticated, None if anonymous
    """
    if not credentials:
        return None
    
    token_data = decode_token(credentials.credentials)
    
    if not token_data:
        return None
    
    if not token_data.user_id:
        return None
    
    result = await session.execute(
        select(UserModel).where(
            UserModel.id == token_data.user_id,
            UserModel.deleted_at == None,
        )
    )
    return result.scalar_one_or_none()


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserModel:
    """
    Get the current active user.
    
    Raises 403 if user is inactive.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Active UserModel
        
    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


async def get_token_data(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> TokenData:
    """
    Get decoded token data from request.
    
    Useful for panic endpoints that need session info
    without full user lookup.
    
    Args:
        credentials: Bearer token
        
    Returns:
        TokenData from token
        
    Raises:
        HTTPException: 401 if invalid token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = decode_token(credentials.credentials)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


async def get_token_data_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
) -> Optional[TokenData]:
    """
    Get token data if present, None otherwise.
    
    For endpoints that work with or without authentication.
    
    Args:
        credentials: Optional bearer token
        
    Returns:
        TokenData if valid token, None otherwise
    """
    if not credentials:
        return None
    
    return decode_token(credentials.credentials)


# Alias for backward compatibility
get_current_user_required = get_current_user
