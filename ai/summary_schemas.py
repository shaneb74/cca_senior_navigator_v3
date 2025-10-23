"""Pydantic schemas for GCP summary advice generation."""

from pydantic import BaseModel, Field
from typing import Optional, List


class SummaryAdvice(BaseModel):
    """LLM-generated summary advice for GCP recommendation page.
    
    Provides concise explanation of care recommendation with next steps.
    All fields are LLM-generated except confidence score.
    """
    
    headline: str = Field(..., max_length=180, description="Main recommendation headline (1 sentence)")
    why: List[str] = Field(..., min_length=2, max_length=4, description="2-4 brief reasons for recommendation")
    what_it_means: Optional[str] = Field(None, max_length=240, description="Plain language explanation (1-2 sentences)")
    next_steps: List[str] = Field(..., min_length=1, max_length=3, description="1-3 actionable next steps")
    next_line: Optional[str] = Field(None, max_length=140, description="Transition to cost view (1 sentence)")
    confidence: float = Field(0.0, ge=0, le=1, description="LLM confidence in recommendation (0-1)")
