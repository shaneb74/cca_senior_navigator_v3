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

import time
import uuid
from typing import Literal

from pydantic import BaseModel, Field


def _uid(prefix: str) -> str:
    """Generate unique ID with prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Household(BaseModel):
    """Represents a household that may contain multiple people."""

    uid: str = Field(default_factory=lambda: _uid("hh"))
    zip: str | None = None
    has_partner: bool = False
    home_owner_type: Literal["owner", "tenant", "unknown"] | None = "unknown"
    keep_home_default: bool | None = None
    members: list[str] = Field(default_factory=list)  # person_ids
    created_at: int = Field(default_factory=lambda: int(time.time()))


class Person(BaseModel):
    """Represents an individual within a household."""

    uid: str = Field(default_factory=lambda: _uid("p"))
    household_id: str
    role: Literal["primary", "partner"] = "primary"
    name: str | None = None
    age: int | None = None
    demographics: dict = Field(default_factory=dict)
    status: Literal["active", "archived"] = "active"
    created_at: int = Field(default_factory=lambda: int(time.time()))


class CarePlan(BaseModel):
    """Care assessment and recommendation for a person."""

    uid: str = Field(default_factory=lambda: _uid("cp"))
    person_id: str
    det_tier: str | None = None
    llm_tier: str | None = None
    final_tier: str | None = None
    confidence: float = 0.0
    allowed_tiers: list[str] = Field(default_factory=list)
    bands: dict[str, str] = Field(default_factory=dict)  # {"cog": ..., "sup": ...}
    risky_behaviors: bool = False
    hours_suggested: str | None = None
    hours_user: str | None = None
    under_selected: bool | None = None
    provenance: dict = Field(default_factory=dict)  # {"mode": "replace", "reason": "..."}
    created_at: int = Field(default_factory=lambda: int(time.time()))

    # Optional adjudication metadata (non-breaking)
    source: str | None = None  # "llm" | "deterministic" | "fallback"
    alt_tier: str | None = None  # The non-chosen tier, if any
    llm_confidence: float | None = None
    adjudication_reason: str | None = None  # "llm_valid", "llm_invalid_guard", "llm_timeout", etc.


class CostPlan(BaseModel):
    """Financial projection associated with a CarePlan."""

    uid: str = Field(default_factory=lambda: _uid("cost"))
    person_id: str
    care_plan_id: str  # Association back to CarePlan
    scenario: Literal["facility", "in_home"] = "facility"
    zip: str | None = None
    keep_home: bool | None = None
    home_carry: float | None = 0.0
    hours_band: str | None = None
    owner_tenant: Literal["owner", "tenant", "unknown"] | None = "unknown"
    total_monthly: float | None = 0.0
    breakdown: dict = Field(default_factory=dict)  # {"facility": 4500, "hours": 0}
    assumptions: dict = Field(default_factory=dict)  # For later audit
