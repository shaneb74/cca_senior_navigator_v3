"""
Core Domain Models for Senior Navigator

Defines structured data models for:
- Household: Group of people sharing living arrangements
- Person: Individual with care needs
- CarePlan: Assessment outcome and care recommendation for a person
- CostPlan: Financial projection associated with a CarePlan

These models provide explicit structure for multi-person flows
and enable dual cost planning scenarios (e.g., both spouses).
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict
import uuid
import time


def _uid(prefix: str) -> str:
    """Generate unique ID with prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Household(BaseModel):
    """Represents a household that may contain multiple people."""
    
    uid: str = Field(default_factory=lambda: _uid("hh"))
    zip: Optional[str] = None
    has_partner: bool = False
    home_owner_type: Optional[Literal["owner", "tenant", "unknown"]] = "unknown"
    keep_home_default: Optional[bool] = None
    members: List[str] = Field(default_factory=list)  # person_ids
    created_at: int = Field(default_factory=lambda: int(time.time()))


class Person(BaseModel):
    """Represents an individual within a household."""
    
    uid: str = Field(default_factory=lambda: _uid("p"))
    household_id: str
    role: Literal["primary", "partner"] = "primary"
    name: Optional[str] = None
    age: Optional[int] = None
    demographics: Dict = Field(default_factory=dict)
    status: Literal["active", "archived"] = "active"
    created_at: int = Field(default_factory=lambda: int(time.time()))


class CarePlan(BaseModel):
    """Care assessment and recommendation for a person."""
    
    uid: str = Field(default_factory=lambda: _uid("cp"))
    person_id: str
    det_tier: Optional[str] = None
    llm_tier: Optional[str] = None
    final_tier: Optional[str] = None
    confidence: float = 0.0
    allowed_tiers: List[str] = Field(default_factory=list)
    bands: Dict[str, str] = Field(default_factory=dict)  # {"cog": ..., "sup": ...}
    risky_behaviors: bool = False
    hours_suggested: Optional[str] = None
    hours_user: Optional[str] = None
    under_selected: Optional[bool] = None
    provenance: Dict = Field(default_factory=dict)  # {"mode": "replace", "reason": "..."}
    created_at: int = Field(default_factory=lambda: int(time.time()))
    
    # Optional adjudication metadata (non-breaking)
    source: Optional[str] = None  # "llm" | "deterministic" | "fallback"
    alt_tier: Optional[str] = None  # The non-chosen tier, if any
    llm_confidence: Optional[float] = None
    adjudication_reason: Optional[str] = None  # "llm_valid", "llm_invalid_guard", "llm_timeout", etc.


class CostPlan(BaseModel):
    """Financial projection associated with a CarePlan."""
    
    uid: str = Field(default_factory=lambda: _uid("cost"))
    person_id: str
    care_plan_id: str  # Association back to CarePlan
    scenario: Literal["facility", "in_home"] = "facility"
    zip: Optional[str] = None
    keep_home: Optional[bool] = None
    home_carry: Optional[float] = 0.0
    hours_band: Optional[str] = None
    owner_tenant: Optional[Literal["owner", "tenant", "unknown"]] = "unknown"
    total_monthly: Optional[float] = 0.0
    breakdown: Dict = Field(default_factory=dict)  # {"facility": 4500, "hours": 0}
    assumptions: Dict = Field(default_factory=dict)  # For later audit
