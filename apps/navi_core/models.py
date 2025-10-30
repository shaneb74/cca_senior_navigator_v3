"""
NAVI Core Data Models

Pydantic v2 models for structured AI responses, validation, metadata, and user profiles.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ChunkMetadata(BaseModel):
    """Metadata for a retrieved knowledge chunk."""
    
    id: str = Field(..., description="Unique identifier for the chunk")
    source: str = Field(..., description="Source document or file")
    text: str = Field(..., description="Retrieved text content")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")


class ValidationResult(BaseModel):
    """Result of answer validation."""
    
    passed: bool = Field(..., description="Whether validation passed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Validation confidence score")
    reason: Optional[str] = Field(None, description="Explanation if validation failed")


class NaviAnswer(BaseModel):
    """Complete NAVI answer with metadata and validation."""
    
    question: str = Field(..., description="Original user question")
    answer: str = Field(..., description="Generated answer text")
    tier: Optional[int] = Field(None, description="Tier used (1=FAQ, 2=RAG, 3=LLM)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Answer confidence score")
    validated: ValidationResult = Field(..., description="Validation result")
    sources: List[ChunkMetadata] = Field(default_factory=list, description="Source chunks used")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "What is assisted living?",
                "answer": "Assisted living provides...",
                "tier": 1,
                "confidence": 1.0,
                "validated": {"passed": True, "confidence": 1.0},
                "sources": []
            }
        }
    )


# ---- Phase 3: Profile-Driven Personalization Models ----

class UserProfile(BaseModel):
    """User profile for persona and journey tracking."""
    
    id: str = Field(..., description="Unique user identifier")
    name: Optional[str] = Field(None, description="User's name")
    role: str = Field(default="AdultChild", description="User role/persona")
    relationship: Optional[str] = Field(None, description="Relationship to care recipient")
    stage: str = Field(default="Awareness", description="Current journey stage")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    created_at: datetime = Field(default_factory=datetime.now, description="Profile creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "user_123",
                "name": "Sarah",
                "role": "AdultChild",
                "relationship": "daughter",
                "stage": "Assessment",
                "preferences": {"tone_preference": "Empathetic", "detail_level": "moderate"},
                "created_at": "2025-10-29T10:00:00",
                "updated_at": "2025-10-29T14:30:00"
            }
        }
    )


class JourneyEvent(BaseModel):
    """Event tracking journey stage transitions."""
    
    stage: str = Field(..., description="Journey stage reached")
    trigger: str = Field(..., description="What triggered the stage transition")
    timestamp: datetime = Field(default_factory=datetime.now, description="When transition occurred")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in stage detection")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event context")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stage": "Assessment",
                "trigger": "User asked to compare options",
                "timestamp": "2025-10-29T14:30:00",
                "confidence": 0.9,
                "metadata": {"keywords": ["compare", "options"], "question_count": 5}
            }
        }
    )
