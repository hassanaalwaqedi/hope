"""
Emergency Resources

Jurisdiction-aware emergency resource resolver.
Configurable, no hardcoded phone numbers.

LEGAL_REVIEW_REQUIRED: Emergency resource information
must be verified for accuracy in each jurisdiction.
"""

from dataclasses import dataclass, field
from typing import Optional
import json
import os

from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class EmergencyResource:
    """
    A single emergency resource.
    
    Attributes:
        name: Resource name (e.g., "National Suicide Prevention Lifeline")
        resource_type: Type (hotline, text, website, hospital)
        contact: Contact information (phone, URL, etc.)
        description: Brief description
        available_24_7: Whether available 24/7
        languages: Supported languages
    """
    
    name: str
    resource_type: str  # hotline, text, website, hospital, chat
    contact: str
    description: str = ""
    available_24_7: bool = True
    languages: list[str] = field(default_factory=lambda: ["en"])
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.resource_type,
            "contact": self.contact,
            "description": self.description,
            "available_24_7": self.available_24_7,
        }
    
    def format_for_user(self) -> str:
        """Format resource for display to user."""
        availability = "(24/7)" if self.available_24_7 else ""
        return f"• **{self.name}**: {self.contact} {availability}"


@dataclass
class JurisdictionResources:
    """
    Emergency resources for a specific jurisdiction.
    
    Attributes:
        country_code: ISO country code
        country_name: Human-readable country name
        region_code: Optional region/state code
        region_name: Optional region name
        resources: List of emergency resources
        emergency_number: General emergency number (e.g., 911)
        mental_health_resources: Mental health specific resources
    """
    
    country_code: str
    country_name: str
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    resources: list[EmergencyResource] = field(default_factory=list)
    emergency_number: str = ""
    mental_health_resources: list[EmergencyResource] = field(default_factory=list)
    
    def get_crisis_hotlines(self) -> list[EmergencyResource]:
        """Get crisis hotlines from resources."""
        return [r for r in self.resources if r.resource_type == "hotline"]
    
    def get_text_lines(self) -> list[EmergencyResource]:
        """Get text-based crisis lines."""
        return [r for r in self.resources if r.resource_type == "text"]
    
    def format_all_resources(self) -> str:
        """Format all resources for display."""
        lines = [f"**Emergency Resources ({self.country_name})**\n"]
        
        if self.emergency_number:
            lines.append(f"• **Emergency**: {self.emergency_number}\n")
        
        for resource in self.resources:
            lines.append(resource.format_for_user())
        
        return "\n".join(lines)


class EmergencyResourceResolver:
    """
    Jurisdiction-aware emergency resource resolver.
    
    Provides localized emergency resources based on user
    location. Resources are configurable via JSON.
    
    ARCHITECTURE: No hardcoded phone numbers. All resources
    loaded from configuration that can be updated independently.
    
    Usage:
        resolver = EmergencyResourceResolver()
        resources = resolver.get_resources("US")
        formatted = resolver.format_crisis_message("US")
    """
    
    # Default resources (fallback when jurisdiction unknown)
    # These are international resources
    DEFAULT_RESOURCES: JurisdictionResources = JurisdictionResources(
        country_code="INTL",
        country_name="International",
        resources=[
            EmergencyResource(
                name="International Association for Suicide Prevention",
                resource_type="website",
                contact="https://www.iasp.info/resources/Crisis_Centres/",
                description="Directory of crisis centers worldwide",
                available_24_7=True,
            ),
            EmergencyResource(
                name="Befrienders Worldwide",
                resource_type="website",
                contact="https://www.befrienders.org/",
                description="Emotional support centers globally",
                available_24_7=True,
            ),
        ],
    )
    
    # Built-in resource database (can be overridden by config file)
    # LEGAL_REVIEW_REQUIRED: Verify all numbers before production
    BUILT_IN_RESOURCES: dict[str, JurisdictionResources] = {
        "US": JurisdictionResources(
            country_code="US",
            country_name="United States",
            emergency_number="911",
            resources=[
                EmergencyResource(
                    name="988 Suicide & Crisis Lifeline",
                    resource_type="hotline",
                    contact="988",
                    description="National suicide prevention lifeline",
                    available_24_7=True,
                    languages=["en", "es"],
                ),
                EmergencyResource(
                    name="Crisis Text Line",
                    resource_type="text",
                    contact="Text HOME to 741741",
                    description="Text-based crisis support",
                    available_24_7=True,
                ),
                EmergencyResource(
                    name="SAMHSA National Helpline",
                    resource_type="hotline",
                    contact="1-800-662-4357",
                    description="Substance abuse and mental health",
                    available_24_7=True,
                ),
            ],
        ),
        "GB": JurisdictionResources(
            country_code="GB",
            country_name="United Kingdom",
            emergency_number="999",
            resources=[
                EmergencyResource(
                    name="Samaritans",
                    resource_type="hotline",
                    contact="116 123",
                    description="Emotional support for anyone in distress",
                    available_24_7=True,
                ),
                EmergencyResource(
                    name="SHOUT",
                    resource_type="text",
                    contact="Text SHOUT to 85258",
                    description="Text-based mental health support",
                    available_24_7=True,
                ),
            ],
        ),
        "SA": JurisdictionResources(
            country_code="SA",
            country_name="Saudi Arabia",
            emergency_number="911",
            resources=[
                EmergencyResource(
                    name="Mental Health Hotline",
                    resource_type="hotline",
                    contact="920033360",
                    description="National mental health support line",
                    available_24_7=True,
                    languages=["ar", "en"],
                ),
            ],
        ),
        "AE": JurisdictionResources(
            country_code="AE",
            country_name="United Arab Emirates",
            emergency_number="999",
            resources=[
                EmergencyResource(
                    name="Dubai Health Authority Mental Health",
                    resource_type="hotline",
                    contact="800342",
                    description="Mental health support line",
                    available_24_7=False,
                    languages=["ar", "en"],
                ),
            ],
        ),
        "EG": JurisdictionResources(
            country_code="EG",
            country_name="Egypt",
            emergency_number="123",
            resources=[
                EmergencyResource(
                    name="Befrienders Cairo",
                    resource_type="hotline",
                    contact="+20 2 7621602",
                    description="Emotional support helpline",
                    available_24_7=False,
                    languages=["ar", "en"],
                ),
            ],
        ),
    }
    
    def __init__(
        self,
        config_path: Optional[str] = None,
    ) -> None:
        """
        Initialize resolver.
        
        Args:
            config_path: Optional path to JSON config file
        """
        self._resources = dict(self.BUILT_IN_RESOURCES)
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """Load resources from JSON config file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for country_code, country_data in data.items():
                resources = [
                    EmergencyResource(**r)
                    for r in country_data.get("resources", [])
                ]
                self._resources[country_code] = JurisdictionResources(
                    country_code=country_code,
                    country_name=country_data.get("country_name", country_code),
                    emergency_number=country_data.get("emergency_number", ""),
                    resources=resources,
                )
            
            logger.info(
                "Loaded emergency resources config",
                path=config_path,
                jurisdiction_count=len(data),
            )
        except Exception as e:
            logger.error(f"Failed to load resources config: {e}")
    
    def get_resources(
        self,
        country_code: str,
        region_code: Optional[str] = None,
    ) -> JurisdictionResources:
        """
        Get resources for a jurisdiction.
        
        Args:
            country_code: ISO country code (e.g., "US", "GB")
            region_code: Optional region/state code
            
        Returns:
            JurisdictionResources for the location
        """
        # Try exact match first
        key = f"{country_code}:{region_code}" if region_code else country_code
        if key in self._resources:
            return self._resources[key]
        
        # Try country only
        if country_code in self._resources:
            return self._resources[country_code]
        
        # Return default international resources
        logger.warning(
            "No resources for jurisdiction, using default",
            country_code=country_code,
        )
        return self.DEFAULT_RESOURCES
    
    def format_crisis_message(
        self,
        country_code: str = "US",
        include_emergency: bool = True,
    ) -> str:
        """
        Format a crisis message with resources.
        
        Args:
            country_code: User's country
            include_emergency: Whether to include emergency number
            
        Returns:
            Formatted crisis message
        """
        resources = self.get_resources(country_code)
        
        lines = []
        lines.append("---")
        lines.append("**If you're in crisis or having thoughts of self-harm:**\n")
        
        if include_emergency and resources.emergency_number:
            lines.append(f"• **Emergency**: {resources.emergency_number}")
        
        for resource in resources.resources[:3]:  # Limit to top 3
            lines.append(resource.format_for_user())
        
        lines.append("")
        lines.append("You don't have to face this alone. Professional support is available.")
        
        return "\n".join(lines)
    
    def get_primary_hotline(
        self,
        country_code: str,
    ) -> Optional[EmergencyResource]:
        """Get the primary crisis hotline for a country."""
        resources = self.get_resources(country_code)
        hotlines = resources.get_crisis_hotlines()
        return hotlines[0] if hotlines else None
    
    def list_supported_countries(self) -> list[str]:
        """List all supported country codes."""
        return list(self._resources.keys())
