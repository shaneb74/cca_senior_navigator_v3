"""Pydantic schemas for GCP summary advice generation."""

from typing import Literal

from pydantic import BaseModel, Field


class SummaryAdvice(BaseModel):
    """LLM-generated summary advice for GCP recommendation page.
    
    Provides concise explanation of care recommendation with next steps.
    All fields are LLM-generated except confidence score.
    """

    tier: Literal["none", "in_home", "assisted_living", "memory_care", "memory_care_high_acuity"] | None = Field(
        None, description="Care tier (optional, can be set by caller)"
    )
    headline: str = Field(..., max_length=180, description="Main recommendation headline (1 sentence)")
    what_it_means: str = Field(..., max_length=300, description="Plain language explanation (1-2 sentences)")
    why: list[str] = Field(default_factory=list, max_length=4, description="Up to 4 brief reasons for recommendation")
    next_line: str | None = Field(None, max_length=140, description="Transition to cost view (1 sentence)")
    confidence: float = Field(0.0, ge=0, le=1, description="LLM confidence in recommendation (0-1)")
