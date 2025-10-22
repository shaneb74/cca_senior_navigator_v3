"""
Pydantic v2 schemas for LLM Navi integration.

Defines strict data models for Cost Planner context and LLM advice responses.
All models use strict validation to prevent injection or malformed data.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CPContext(BaseModel):
    """Cost Planner context for LLM Navi advice generation.
    
    Contains all deterministic factors the LLM should consider when
    generating contextual advice for the user's care planning journey.
    
    Attributes:
        tier: Care tier (independent_living, assisted_living, memory_care, etc.)
        has_partner: Whether user has a partner/spouse
        move_preference: User's move timeline preference
        keep_home: Whether user wants to keep their home
        monthly_adjusted: Estimated monthly care cost (after adjustments)
        region: Geographic region for cost context
        flags: List of user flags (medicaid_likely, veteran, homeowner, etc.)
        top_reasons: Top 3 reasons for seeking care (mobility, memory, etc.)
    """
    
    tier: str = Field(..., description="Care tier recommendation")
    has_partner: bool = Field(..., description="Has spouse/partner")
    move_preference: Optional[str] = Field(None, description="Move timeline preference")
    keep_home: bool = Field(default=False, description="Wants to keep home")
    monthly_adjusted: float = Field(..., ge=0, description="Monthly care cost estimate")
    region: str = Field(..., description="Geographic region")
    flags: list[str] = Field(default_factory=list, description="User context flags")
    top_reasons: list[str] = Field(default_factory=list, description="Top care reasons")
    
    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        """Ensure tier is a known care level."""
        valid_tiers = {
            "independent_living",
            "assisted_living",
            "memory_care",
            "memory_care_high_acuity",
            "skilled_nursing",
            "home_care",
        }
        if v not in valid_tiers:
            raise ValueError(f"Invalid tier: {v}. Must be one of {valid_tiers}")
        return v
    
    @field_validator("monthly_adjusted")
    @classmethod
    def validate_cost(cls, v: float) -> float:
        """Ensure cost is reasonable (0 to $50k/month)."""
        if not 0 <= v <= 50000:
            raise ValueError(f"Monthly cost {v} outside valid range [0, 50000]")
        return v
    
    @field_validator("top_reasons")
    @classmethod
    def validate_top_reasons(cls, v: list[str]) -> list[str]:
        """Limit to max 5 reasons."""
        if len(v) > 5:
            return v[:5]  # Truncate to top 5
        return v
    
    class Config:
        """Pydantic v2 config."""
        # Strict validation - no extra fields allowed
        extra = "forbid"
        # Enable validation on assignment
        validate_assignment = True


class CPAdvice(BaseModel):
    """LLM-generated advice for Cost Planner Navi.
    
    Contains contextual guidance, insights, and optional adjustments
    that the LLM suggests based on the user's CPContext.
    
    Attributes:
        messages: Short conversational messages for Navi to display
        insights: Longer-form insights about user's situation
        questions_next: Suggested follow-up questions to ask user
        proposed_adjustments: Optional parameter adjustments (assist/adjust modes)
        confidence: LLM's confidence in advice (0.0 to 1.0)
    """
    
    messages: list[str] = Field(
        default_factory=list,
        description="Short Navi messages (1-2 sentences each)",
        max_length=5,
    )
    insights: list[str] = Field(
        default_factory=list,
        description="Deeper insights about user's situation",
        max_length=3,
    )
    questions_next: list[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions",
        max_length=5,
    )
    proposed_adjustments: Optional[dict[str, float]] = Field(
        None,
        description="Optional parameter adjustments (adjust mode only)",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence score for advice quality",
    )
    
    @field_validator("messages", "insights", "questions_next")
    @classmethod
    def validate_text_lists(cls, v: list[str]) -> list[str]:
        """Ensure text items are non-empty and reasonable length."""
        cleaned = []
        for item in v:
            if not isinstance(item, str):
                continue
            item = item.strip()
            if item and len(item) <= 500:  # Max 500 chars per item
                cleaned.append(item)
        return cleaned
    
    @field_validator("proposed_adjustments")
    @classmethod
    def validate_adjustments(cls, v: Optional[dict[str, float]]) -> Optional[dict[str, float]]:
        """Ensure adjustments are valid numeric values."""
        if v is None:
            return None
        
        # Only allow known adjustment keys
        valid_keys = {"monthly_cost", "move_timeline_months", "savings_rate"}
        cleaned = {}
        for key, value in v.items():
            if key in valid_keys and isinstance(value, (int, float)):
                cleaned[key] = float(value)
        
        return cleaned if cleaned else None
    
    class Config:
        """Pydantic v2 config."""
        extra = "ignore"  # Ignore extra fields from LLM response
        validate_assignment = True
