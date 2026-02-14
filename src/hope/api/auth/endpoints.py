"""
Authentication Endpoints

User registration, login, and token management.
Supports anonymous panic session creation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hope.api.auth.service import AuthService, AuthTokens, hash_password
from hope.api.auth.dependencies import get_current_user, get_token_data
from hope.infrastructure.database import get_async_session
from hope.infrastructure.database.models.user_model import UserModel
from hope.config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models

class RegisterRequest(BaseModel):
    """User registration request."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")
    age_confirmed: bool = Field(..., description="User confirms they are 13+ years old")
    consent_accepted: bool = Field(..., description="User accepts terms and privacy policy")


class RegisterResponse(BaseModel):
    """Registration response with tokens."""
    
    user_id: UUID
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    message: str = "Account created successfully"


class LoginRequest(BaseModel):
    """Login request."""
    
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with tokens."""
    
    user_id: UUID
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """Token refresh request."""
    
    refresh_token: str


class PanicSessionRequest(BaseModel):
    """Request for anonymous panic session."""
    
    device_id: Optional[str] = Field(None, description="Optional device identifier")
    country_code: Optional[str] = Field(None, description="User's country code for resources")
    language: str = Field(default="en", description="Preferred language")


class PanicSessionResponse(BaseModel):
    """Anonymous panic session response."""
    
    session_id: UUID
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 7200  # 2 hours
    message: str = "You're in a safe space. I'm here with you."


class UserInfoResponse(BaseModel):
    """Current user info."""
    
    user_id: UUID
    email: str
    is_active: bool
    consent_version: Optional[str]


# Endpoints

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_async_session),
) -> RegisterResponse:
    """
    Register a new user account.
    
    Requires age confirmation (13+) and consent acceptance.
    Returns JWT tokens for immediate authentication.
    """
    # Validate age and consent
    if not request.age_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm you are 13 years or older",
        )
    
    if not request.consent_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the terms and privacy policy",
        )
    
    # Check if email already exists
    result = await session.execute(
        select(UserModel).where(UserModel.email == request.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    
    # Create user
    user = UserModel(
        id=uuid4(),
        email=request.email,
        password_hash=hash_password(request.password),
        is_active=True,
        consent_version="1.0.0",  # Track consent version
        profile={
            "age_confirmed": True,
            "consent_accepted_at": datetime.utcnow().isoformat(),
        },
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Generate tokens
    auth_service = AuthService()
    tokens = auth_service.create_tokens(user.id)
    
    logger.info("User registered", user_id=str(user.id))
    
    return RegisterResponse(
        user_id=user.id,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login with email and password",
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponse:
    """
    Authenticate user and return JWT tokens.
    """
    auth_service = AuthService()
    
    user_id = await auth_service.authenticate_user(
        email=request.email,
        password=request.password,
        session=session,
    )
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = auth_service.create_tokens(user_id)
    
    return LoginResponse(
        user_id=user_id,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh access token",
)
async def refresh_token(
    request: RefreshRequest,
    session: AsyncSession = Depends(get_async_session),
) -> LoginResponse:
    """
    Get new access token using refresh token.
    """
    auth_service = AuthService()
    
    tokens = await auth_service.refresh_tokens(
        refresh_token=request.refresh_token,
        session=session,
    )
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user_id from token
    token_data = auth_service.decode_token(tokens.access_token)
    
    return LoginResponse(
        user_id=token_data.user_id,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


@router.post(
    "/panic-session",
    response_model=PanicSessionResponse,
    summary="Create anonymous panic session",
)
async def create_panic_session(
    request: PanicSessionRequest,
) -> PanicSessionResponse:
    """
    Create an anonymous panic session.
    
    No registration or login required.
    Allows immediate access to crisis support.
    
    This endpoint prioritizes crisis access over security.
    Limited functionality compared to authenticated sessions.
    """
    session_id = uuid4()
    
    auth_service = AuthService()
    token = auth_service.create_panic_session_token(session_id)
    
    logger.info(
        "Anonymous panic session created",
        session_id=str(session_id),
        country_code=request.country_code,
        language=request.language,
    )
    
    # Localized welcome message
    messages = {
        "en": "You're in a safe space. I'm here with you.",
        "fr": "Tu es dans un espace sûr. Je suis là avec toi.",
        "ar": "أنت في مكان آمن. أنا هنا معك.",
        "de": "Du bist an einem sicheren Ort. Ich bin bei dir.",
        "es": "Estás en un lugar seguro. Estoy aquí contigo.",
    }
    
    message = messages.get(request.language, messages["en"])
    
    return PanicSessionResponse(
        session_id=session_id,
        access_token=token,
        token_type="bearer",
        expires_in=7200,
        message=message,
    )


@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="Get current user info",
)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user),
) -> UserInfoResponse:
    """
    Get information about the currently authenticated user.
    """
    return UserInfoResponse(
        user_id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        consent_version=current_user.consent_version,
    )
