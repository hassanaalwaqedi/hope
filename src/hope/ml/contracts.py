"""
Clinical Intelligence Layer - Data Contracts

This module defines the core Pydantic models and enums used throughout
the clinical intelligence layer for state management and type safety.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ClientState(str, Enum):
    """
    Represents the current clinical state of the client.
    
    States:
        PANIC_MODE: Client is experiencing acute panic/anxiety (intensity >= 6)
        REGULATION_MODE: Client needs grounding/regulation exercises (intensity 4-5)
        DANGER_MODE: Safety concern detected, requires immediate intervention
        CHECK_IN_MODE: Client is calm, ready for reflective conversation (intensity <= 3)
    """
    PANIC_MODE = "PANIC_MODE"
    REGULATION_MODE = "REGULATION_MODE"
    DANGER_MODE = "DANGER_MODE"
    CHECK_IN_MODE = "CHECK_IN_MODE"


class InterventionTool(str, Enum):
    """
    Represents the therapeutic intervention tool to render for the client.
    
    Tools:
        BREATHING_CIRCLE: Animated breathing exercise for panic reduction
        GROUNDING_54321: 5-4-3-2-1 grounding technique for regulation
        SAFETY_SCREEN: Emergency contact and safety resources screen
        NONE: No specific tool needed, text-based interaction
    """
    BREATHING_CIRCLE = "BREATHING_CIRCLE"
    GROUNDING_54321 = "GROUNDING_54321"
    SAFETY_SCREEN = "SAFETY_SCREEN"
    NONE = "NONE"


class ClinicalInput(BaseModel):
    """
    Input model for clinical processing.
    
    Attributes:
        text: The client's message or input text
        current_intensity: Self-reported distress level from 1 (calm) to 10 (extreme)
        language: ISO language code for response localization (default: "en")
    """
    text: str = Field(
        ...,
        description="The client's message or input text",
        min_length=1,
        max_length=5000
    )
    current_intensity: int = Field(
        ...,
        ge=1,
        le=10,
        description="Self-reported distress intensity from 1 (calm) to 10 (extreme panic)"
    )
    language: str = Field(
        default="en",
        description="ISO language code for response localization",
        pattern=r"^[a-z]{2}$"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "I can't breathe, my heart is racing",
                    "current_intensity": 8,
                    "language": "en"
                },
                {
                    "text": "مش قادر اتنفس، قلبي بيدق بسرعة",
                    "current_intensity": 8,
                    "language": "ar"
                }
            ]
        }
    }


class ClinicalResponse(BaseModel):
    """
    Response model from the regulation engine.
    
    Attributes:
        next_state: The clinical state to transition the client to
        tool_to_render: The intervention tool to display
        scripted_text: The therapeutic response text
        safety_flags: List of detected safety concerns (empty if none)
    """
    next_state: ClientState = Field(
        ...,
        description="The clinical state to transition the client to"
    )
    tool_to_render: InterventionTool = Field(
        ...,
        description="The intervention tool to render for the client"
    )
    scripted_text: str = Field(
        ...,
        description="The therapeutic response text to display",
        min_length=1
    )
    safety_flags: List[str] = Field(
        default_factory=list,
        description="List of detected safety concerns, empty if none detected"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "next_state": "PANIC_MODE",
                    "tool_to_render": "BREATHING_CIRCLE",
                    "scripted_text": "I am here. You are safe. Let's focus on your breathing right now. Follow the circle.",
                    "safety_flags": []
                }
            ]
        }
    }
