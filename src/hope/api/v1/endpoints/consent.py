"""
Consent Management Endpoints

GDPR-compliant consent flow with version tracking.
Age gate enforcement for user safety.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hope.api.auth.dependencies import get_current_user
from hope.infrastructure.database import get_async_session
from hope.infrastructure.database.models.user_model import UserModel
from hope.infrastructure.database.models.consent_model import ConsentModel
from hope.config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Current consent versions (update when terms change)
CURRENT_CONSENT_VERSION = "1.0.0"
MINIMUM_AGE = 13  # Configurable: 13 for US COPPA, 16 for GDPR, 18 for some jurisdictions


class ConsentRequest(BaseModel):
    """Request to accept consent."""
    
    terms_accepted: bool = Field(..., description="Accept terms of service")
    privacy_accepted: bool = Field(..., description="Accept privacy policy")
    data_processing_accepted: bool = Field(..., description="Accept data processing")
    age_confirmed: bool = Field(..., description="Confirm minimum age requirement")
    emotional_history_consent: bool = Field(default=False, description="Optional: Allow storing emotional history")
    analytics_consent: bool = Field(default=False, description="Optional: Allow anonymous analytics")


class ConsentResponse(BaseModel):
    """Consent acceptance response."""
    
    consent_version: str
    accepted_at: str
    required_consents_granted: bool
    message: str


class ConsentStatusResponse(BaseModel):
    """Current consent status."""
    
    has_valid_consent: bool
    consent_version: Optional[str]
    needs_update: bool
    required_version: str
    age_confirmed: bool


@router.post(
    "/accept",
    response_model=ConsentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accept consent terms",
)
async def accept_consent(
    request: ConsentRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ConsentResponse:
    """
    Accept consent for data processing, terms, and privacy policy.
    
    All required consents must be accepted to use HOPE.
    Age confirmation is mandatory.
    """
    # Validate required consents
    if not request.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms of service must be accepted",
        )
    
    if not request.privacy_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Privacy policy must be accepted",
        )
    
    if not request.data_processing_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data processing consent is required",
        )
    
    if not request.age_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You must confirm you are {MINIMUM_AGE} years or older",
        )
    
    # Create consent records
    now = datetime.now(timezone.utc)
    
    # Store consent details in user profile
    current_user.consent_version = CURRENT_CONSENT_VERSION
    current_user.profile = current_user.profile or {}
    current_user.profile["consent"] = {
        "terms_accepted": request.terms_accepted,
        "privacy_accepted": request.privacy_accepted,
        "data_processing_accepted": request.data_processing_accepted,
        "age_confirmed": request.age_confirmed,
        "emotional_history_consent": request.emotional_history_consent,
        "analytics_consent": request.analytics_consent,
        "accepted_at": now.isoformat(),
        "consent_version": CURRENT_CONSENT_VERSION,
    }
    
    await db.commit()
    
    logger.info(
        "Consent accepted",
        user_id=str(current_user.id),
        consent_version=CURRENT_CONSENT_VERSION,
    )
    
    return ConsentResponse(
        consent_version=CURRENT_CONSENT_VERSION,
        accepted_at=now.isoformat(),
        required_consents_granted=True,
        message="Consent recorded successfully. You may now use HOPE.",
    )


@router.get(
    "/status",
    response_model=ConsentStatusResponse,
    summary="Check consent status",
)
async def get_consent_status(
    current_user: UserModel = Depends(get_current_user),
) -> ConsentStatusResponse:
    """
    Check if user has valid consent for using HOPE.
    
    Returns whether consent is current or needs update.
    """
    has_consent = current_user.consent_version is not None
    needs_update = (
        not has_consent or 
        current_user.consent_version != CURRENT_CONSENT_VERSION
    )
    
    profile = current_user.profile or {}
    consent_data = profile.get("consent", {})
    
    return ConsentStatusResponse(
        has_valid_consent=has_consent and not needs_update,
        consent_version=current_user.consent_version,
        needs_update=needs_update,
        required_version=CURRENT_CONSENT_VERSION,
        age_confirmed=consent_data.get("age_confirmed", False),
    )


@router.post(
    "/withdraw",
    summary="Withdraw consent",
)
async def withdraw_consent(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Withdraw consent and request data deletion.
    
    This will disable the account and trigger data retention policies.
    """
    # Clear consent
    current_user.consent_version = None
    current_user.is_active = False
    
    # Update profile
    current_user.profile = current_user.profile or {}
    current_user.profile["consent_withdrawn"] = {
        "withdrawn_at": datetime.now(timezone.utc).isoformat(),
        "reason": "User requested consent withdrawal",
    }
    
    await db.commit()
    
    logger.warning(
        "Consent withdrawn",
        user_id=str(current_user.id),
    )
    
    return {
        "message": "Consent withdrawn. Your account has been deactivated.",
        "data_deletion": "Your data will be deleted within 30 days per our retention policy.",
    }


@router.get(
    "/requirements",
    summary="Get consent requirements",
)
async def get_consent_requirements() -> dict:
    """
    Get current consent requirements.
    
    Returns information about required and optional consents.
    """
    return {
        "current_version": CURRENT_CONSENT_VERSION,
        "minimum_age": MINIMUM_AGE,
        "required_consents": [
            {
                "id": "terms_of_service",
                "name": "Terms of Service",
                "description": "Agreement to HOPE's terms and conditions",
                "required": True,
            },
            {
                "id": "privacy_policy",
                "name": "Privacy Policy",
                "description": "Acknowledgment of data collection and use practices",
                "required": True,
            },
            {
                "id": "data_processing",
                "name": "Data Processing",
                "description": "Consent for processing personal and emotional data",
                "required": True,
            },
            {
                "id": "age_confirmation",
                "name": "Age Confirmation",
                "description": f"Confirmation that user is {MINIMUM_AGE} years or older",
                "required": True,
            },
        ],
        "optional_consents": [
            {
                "id": "emotional_history",
                "name": "Emotional History",
                "description": "Allow storing emotional state history for personalized support",
                "required": False,
            },
            {
                "id": "analytics",
                "name": "Analytics",
                "description": "Allow anonymous usage analytics to improve HOPE",
                "required": False,
            },
        ],
    }
