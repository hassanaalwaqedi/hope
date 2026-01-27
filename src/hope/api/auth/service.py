"""
Authentication Service

JWT token management and password hashing for HOPE.
Supports both authenticated users and anonymous panic sessions.

SECURITY: All tokens are signed with HS256.
Passwords are hashed with bcrypt (12 rounds).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from hope.config import get_settings
from hope.config.logging_config import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Decoded JWT token data."""
    
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    is_anonymous: bool = False
    token_type: str = "access"  # access, refresh, panic
    exp: Optional[datetime] = None
    

@dataclass
class AuthTokens:
    """Pair of access and refresh tokens."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Bcrypt hash string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hash
        
    Returns:
        True if password matches
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(
    user_id: UUID,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token for a user.
    
    Args:
        user_id: User's UUID
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT string
    """
    settings = get_settings()
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt.access_token_expire_minutes)
    
    expire = datetime.now(timezone.utc) + expires_delta
    
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "jti": str(uuid4()),  # Unique token ID
    }
    
    token = jwt.encode(
        payload,
        settings.jwt.secret_key.get_secret_value(),
        algorithm=settings.jwt.algorithm,
    )
    
    return token


def create_refresh_token(
    user_id: UUID,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token for a user.
    
    Args:
        user_id: User's UUID
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT string
    """
    settings = get_settings()
    
    if expires_delta is None:
        expires_delta = timedelta(days=settings.jwt.refresh_token_expire_days)
    
    expire = datetime.now(timezone.utc) + expires_delta
    
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "jti": str(uuid4()),
    }
    
    token = jwt.encode(
        payload,
        settings.jwt.secret_key.get_secret_value(),
        algorithm=settings.jwt.algorithm,
    )
    
    return token


def create_panic_token(session_id: UUID) -> str:
    """
    Create a temporary token for anonymous panic sessions.
    
    These tokens have limited scope and shorter expiry.
    No user_id required - allows crisis access without login.
    
    Args:
        session_id: Panic session UUID
        
    Returns:
        Encoded JWT string
    """
    settings = get_settings()
    
    # Panic tokens expire in 2 hours
    expire = datetime.now(timezone.utc) + timedelta(hours=2)
    
    payload = {
        "sub": str(session_id),
        "type": "panic",
        "is_anonymous": True,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "jti": str(uuid4()),
    }
    
    token = jwt.encode(
        payload,
        settings.jwt.secret_key.get_secret_value(),
        algorithm=settings.jwt.algorithm,
    )
    
    return token


def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: Encoded JWT string
        
    Returns:
        TokenData if valid, None if invalid/expired
    """
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt.secret_key.get_secret_value(),
            algorithms=[settings.jwt.algorithm],
        )
        
        token_type = payload.get("type", "access")
        is_anonymous = payload.get("is_anonymous", False)
        
        if is_anonymous:
            # Panic session token
            return TokenData(
                session_id=UUID(payload["sub"]),
                is_anonymous=True,
                token_type=token_type,
                exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            )
        else:
            # User token
            return TokenData(
                user_id=UUID(payload["sub"]),
                is_anonymous=False,
                token_type=token_type,
                exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            )
            
    except JWTError as e:
        logger.debug(f"JWT error: {e}")
        return None
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        return None


class AuthService:
    """
    Authentication service for HOPE.
    
    Handles user authentication, token management,
    and anonymous panic session creation.
    
    Usage:
        auth = AuthService()
        tokens = await auth.login(email, password)
        user = await auth.get_user_from_token(token)
    """
    
    def __init__(self) -> None:
        """Initialize auth service."""
        self._settings = get_settings()
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
        session,  # AsyncSession
    ) -> Optional[UUID]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email
            password: Plain text password
            session: Database session
            
        Returns:
            User UUID if authenticated, None otherwise
        """
        from sqlalchemy import select
        from hope.infrastructure.database.models.user_model import UserModel
        
        result = await session.execute(
            select(UserModel).where(
                UserModel.email == email,
                UserModel.is_active == True,
                UserModel.deleted_at == None,
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.info("Login failed: user not found", email=email[:3] + "***")
            return None
        
        if not user.password_hash:
            logger.info("Login failed: no password set", user_id=str(user.id))
            return None
        
        if not verify_password(password, user.password_hash):
            logger.info("Login failed: invalid password", user_id=str(user.id))
            return None
        
        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await session.commit()
        
        logger.info("User authenticated", user_id=str(user.id))
        return user.id
    
    def create_tokens(self, user_id: UUID) -> AuthTokens:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user_id: User's UUID
            
        Returns:
            AuthTokens with access and refresh tokens
        """
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        
        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self._settings.jwt.access_token_expire_minutes * 60,
        )
    
    def create_panic_session_token(self, session_id: UUID) -> str:
        """
        Create a token for anonymous panic sessions.
        
        Allows users to access panic support without login.
        
        Args:
            session_id: Panic session UUID
            
        Returns:
            JWT token string
        """
        return create_panic_token(session_id)
    
    async def refresh_tokens(
        self,
        refresh_token: str,
        session,  # AsyncSession
    ) -> Optional[AuthTokens]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            session: Database session
            
        Returns:
            New AuthTokens if valid, None otherwise
        """
        token_data = decode_token(refresh_token)
        
        if not token_data:
            return None
        
        if token_data.token_type != "refresh":
            logger.warning("Token refresh attempted with non-refresh token")
            return None
        
        if not token_data.user_id:
            return None
        
        # Verify user still exists and is active
        from sqlalchemy import select
        from hope.infrastructure.database.models.user_model import UserModel
        
        result = await session.execute(
            select(UserModel).where(
                UserModel.id == token_data.user_id,
                UserModel.is_active == True,
                UserModel.deleted_at == None,
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning("Token refresh for inactive/deleted user")
            return None
        
        return self.create_tokens(token_data.user_id)
    
    def decode_token(self, token: str) -> Optional[TokenData]:
        """
        Decode and validate a token.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenData if valid
        """
        return decode_token(token)
