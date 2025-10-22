"""
Pydantic v2 schemas for LLM-assisted GCP (Guided Care Planning).

Defines strict data models for GCP context and LLM advice responses.
Enforces canonical tier values and filters forbidden terms.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ====================================================================
# TIER CANONICALIZATION (GCP-specific)
# ====================================================================

# Canonical tier values - ONLY these 5 are allowed
CANONICAL_TIERS = {"none", "in_home", "assisted_living", "memory_care", "memory_care_high_acuity"}

# Cognitive high-risk flags that gate memory care access
COGNITIVE_HIGH_RISK = {
    "wandering",
    "elopement",
    "aggression",
    "severe_sundowning",
    "severe_cognitive_risk",
    "memory_support",
}

# Aliases for common tier name variations
ALIASES = {
    "in_home_care": "in_home",
    "home_care": "in_home",
    "no_care": "none",
    "no_care_needed": "none",
}

# Forbidden terms that should never appear in recommendations
FORBIDDEN_TERMS = {"skilled nursing", "independent living"}

# Type alias for canonical tier values
Tier = Literal["none", "in_home", "assisted_living", "memory_care", "memory_care_high_acuity"]


def normalize_tier(v: Optional[str]) -> Optional[str]:
    """Normalize tier value to canonical form.
    
    Handles common aliases and variations, ensuring only canonical
    tier values are used in GCP recommendations.
    
    Args:
        v: Raw tier string
    
    Returns:
        Canonical tier value or None if invalid
    """
    if not v:
        return None
    
    x = v.strip().lower()
    x = ALIASES.get(x, x)
    
    return x if x in CANONICAL_TIERS else None


# ====================================================================
# SCHEMAS
# ====================================================================


class GCPContext(BaseModel):
    """Context for GCP recommendation generation.
    
    Contains minimal facts needed to justify and guard a care recommendation.
    All fields are derived from GCP module answers and session state.
    """
    
    age_range: str = Field(..., description="Age bracket (e.g., '65-74', '75-84', '85+')")
    living_situation: str = Field(..., description="Current living arrangement")
    has_partner: bool = Field(..., description="Has spouse/partner")
    meds_complexity: str = Field(..., description="Medication management complexity")
    mobility: str = Field(..., description="Mobility status")
    falls: str = Field(..., description="Fall risk assessment")
    badls: List[str] = Field(default_factory=list, description="Basic ADL challenges")
    iadls: List[str] = Field(default_factory=list, description="Instrumental ADL challenges")
    memory_changes: str = Field(..., description="Memory/cognitive changes")
    behaviors: List[str] = Field(default_factory=list, description="Behavioral concerns")
    isolation: str = Field(..., description="Social isolation level")
    move_preference: Optional[int] = Field(None, description="Move timeline (months)")
    flags: List[str] = Field(default_factory=list, description="User context flags")
    
    class Config:
        """Pydantic v2 config."""
        extra = "forbid"
        validate_assignment = True


class GCPAdvice(BaseModel):
    """LLM-generated GCP advice (strictly validated).
    
    All fields are strictly validated and filtered for canonical tiers
    and forbidden terms before being displayed to users.
    """
    
    tier: Tier = Field(..., description="Recommended care tier (canonical only)")
    reasons: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Short factual reasons for recommendation",
    )
    risks: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Key risks to consider",
    )
    navi_messages: List[str] = Field(
        default_factory=list,
        max_length=4,
        description="Brief Navi messages (1-2 sentences each)",
    )
    questions_next: List[str] = Field(
        default_factory=list,
        max_length=3,
        description="Clarifying questions to ask",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in recommendation (0.0-1.0)",
    )
    
    @field_validator("reasons", "risks", "navi_messages", "questions_next", mode="before")
    @classmethod
    def strip_forbidden_terms(cls, v):
        """Remove or replace forbidden terms from text fields.
        
        Ensures LLM output never contains "skilled nursing" or
        "independent living" terminology.
        """
        if not v:
            return v
        
        clean = []
        for s in v:
            text = (s or "").strip()
            if not text:
                continue
            
            # Replace forbidden terms with generic "specialized care"
            text_lower = text.lower()
            for bad in FORBIDDEN_TERMS:
                if bad in text_lower:
                    # Case-insensitive replacement
                    import re
                    text = re.sub(bad, "specialized care", text, flags=re.IGNORECASE)
            
            clean.append(text)
        
        return clean
    
    class Config:
        """Pydantic v2 config."""
        extra = "ignore"  # Ignore extra fields from LLM
        validate_assignment = True
