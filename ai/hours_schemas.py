"""
Hours/day suggestion schemas for GCP.

Defines:
- HoursBand: 4 allowed hour ranges only
- HoursContext: Input signals for baseline + LLM
- HoursAdvice: Validated LLM output (band + reasons + confidence)
"""
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Canonical 4 bands (no other values allowed)
HoursBand = Literal["<1h", "1-3h", "4-8h", "24h"]


class HoursContext(BaseModel):
    """
    Minimal context for hours/day suggestion.
    Built from GCP answers/flags after Daily Living section.
    """
    badls_count: int = Field(ge=0, le=12)  # Basic ADLs (relaxed from 6 to 12)
    iadls_count: int = Field(ge=0, le=20)  # Instrumental ADLs (relaxed from 8 to 20)
    
    # NEW: Actual ADL/IADL lists for weighted scoring
    badls_list: list[str] = Field(default_factory=list)  # e.g., ["bathing", "dressing", "toileting"]
    iadls_list: list[str] = Field(default_factory=list)  # e.g., ["medication_management", "meal_preparation"]
    
    falls: str | None = None  # "none", "once", "multiple"
    mobility: str | None = None  # "independent", "cane", "walker", "wheelchair"
    risky_behaviors: bool = False  # wandering, elopement, aggression, etc.
    meds_complexity: str | None = None  # "none", "simple", "moderate", "complex"
    primary_support: str | None = None  # "spouse", "adult_child", "paid", "none"
    overnight_needed: bool = False  # True if safety/medical needs require overnight
    current_hours: HoursBand | None = None  # User's current arrangement (if any)
    
    # NEW: Detailed cognitive and behavior flags for multipliers
    cognitive_level: str | None = None  # "none", "mild", "moderate", "severe", "advanced"
    wandering: bool = False  # Elopement risk
    aggression: bool = False  # Aggressive behaviors
    sundowning: bool = False  # Evening confusion/agitation
    repetitive_questions: bool = False  # Memory/cognitive symptom


class HoursAdvice(BaseModel):
    """
    Validated LLM output for hours/day suggestion.
    Only valid if band is one of 4 allowed values.
    
    Optional nudge fields are set when user under-selects (picks lower band than suggested).
    """
    band: HoursBand
    reasons: list[str]  # Will be clipped to 3 by validator
    confidence: float = Field(ge=0.0, le=1.0)

    # Optional nudge payload (only set when user under-selects)
    nudge_text: str | None = None
    severity: Literal["info", "strong"] | None = None

    @field_validator("reasons")
    @classmethod
    def validate_reasons(cls, v: list[str]) -> list[str]:
        """Clip to max 3 reasons; reject empty strings."""
        filtered = [r.strip() for r in v if r.strip()]
        return filtered[:3]  # Take first 3 only

    @field_validator("band")
    @classmethod
    def validate_band(cls, v: str) -> str:
        """Ensure band is exactly one of the 4 allowed values."""
        allowed = ["<1h", "1-3h", "4-8h", "24h"]
        if v not in allowed:
            raise ValueError(f"Invalid band '{v}'; must be one of {allowed}")
        return v
