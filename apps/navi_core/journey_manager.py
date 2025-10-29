"""
Journey Manager - Stage detection and progression tracking.

Identifies where user is in their care decision journey (Awareness, Assessment,
Decision, Placement, FollowUp) based on keyword matching and tracks stage
transitions over time.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .models import JourneyEvent
from .paths import get_config_path


class JourneyManager:
    """Manages user journey stage detection and progression."""
    
    def __init__(self, journeys_path: Optional[Path] = None, defaults_path: Optional[Path] = None):
        """
        Initialize JourneyManager with configuration.
        
        Args:
            journeys_path: Path to journeys.yaml (defaults to config/journeys.yaml)
            defaults_path: Path to defaults.yaml (defaults to config/defaults.yaml)
        """
        self.journeys_path = journeys_path or get_config_path("journeys.yaml")
        self.defaults_path = defaults_path or get_config_path("defaults.yaml")
        
        # Load configurations
        self.journeys = self._load_journeys()
        self.defaults = self._load_defaults()
        
        # Build keyword index for fast lookup
        self.keyword_index = self._build_keyword_index()
        
        # Stage ordering for progression logic
        self.stage_order = {
            "Awareness": 1,
            "Assessment": 2,
            "Decision": 3,
            "Placement": 4,
            "FollowUp": 5
        }
    
    def _load_journeys(self) -> Dict:
        """Load journeys configuration from YAML."""
        with open(self.journeys_path) as f:
            return yaml.safe_load(f)
    
    def _load_defaults(self) -> Dict:
        """Load defaults configuration from YAML."""
        with open(self.defaults_path) as f:
            return yaml.safe_load(f)
    
    def _build_keyword_index(self) -> Dict[str, str]:
        """
        Build reverse index: keyword -> stage.
        
        Returns:
            Dict mapping each keyword to its stage name.
        """
        index = {}
        for stage, config in self.journeys.items():
            keywords = config.get("keywords", [])
            for keyword in keywords:
                # Store lowercase for case-insensitive matching
                if keyword.lower() not in index:
                    index[keyword.lower()] = []
                index[keyword.lower()].append(stage)
        return index
    
    def detect_stage(
        self,
        text: str,
        current_stage: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        keyword_match_min: Optional[int] = None
    ) -> JourneyEvent:
        """
        Detect user's journey stage from conversation text.
        
        Args:
            text: User's message text
            current_stage: User's current stage (for progression validation)
            confidence_threshold: Min confidence to change stage (defaults to config)
            keyword_match_min: Min keyword matches required (defaults to config)
        
        Returns:
            JourneyEvent with stage, trigger, confidence, and metadata
        """
        if confidence_threshold is None:
            confidence_threshold = self.defaults["detection"]["stage"]["confidence_threshold"]
        if keyword_match_min is None:
            keyword_match_min = self.defaults["detection"]["stage"]["keyword_match_min"]
        
        # Normalize text for matching
        text_lower = text.lower()
        
        # Find all matching keywords
        stage_matches: Dict[str, List[str]] = {}  # stage -> [matched_keywords]
        
        for keyword, stages in self.keyword_index.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                for stage in stages:
                    if stage not in stage_matches:
                        stage_matches[stage] = []
                    stage_matches[stage].append(keyword)
        
        # If no matches, keep current stage
        if not stage_matches:
            default_stage = current_stage or self.defaults["default_profile"]["stage"]
            return JourneyEvent(
                stage=default_stage,
                trigger="No keywords matched",
                timestamp=datetime.now(),
                confidence=0.0,
                metadata={"matched_keywords": [], "reason": "No stage indicators found"}
            )
        
        # Calculate confidence for each stage
        stage_scores = []
        for stage, keywords in stage_matches.items():
            # Remove duplicates
            unique_keywords = list(set(keywords))
            
            # Check minimum keyword requirement
            if len(unique_keywords) < keyword_match_min:
                continue
            
            # Confidence based on:
            # 1. Number of keyword matches (0.3 per match, max 1.0)
            # 2. Progression logic (boost if moving forward)
            base_confidence = min(1.0, len(unique_keywords) * 0.3)
            
            # Apply progression boost
            progression_boost = 0.0
            if current_stage:
                current_order = self.stage_order.get(current_stage, 0)
                detected_order = self.stage_order.get(stage, 0)
                
                # Boost if moving forward naturally
                if detected_order == current_order + 1:
                    progression_boost = 0.2
                # Slight boost if moving forward at all
                elif detected_order > current_order:
                    progression_boost = 0.1
                # Small penalty if moving backward (but allow it)
                elif detected_order < current_order:
                    progression_boost = -0.1
            
            confidence = max(0.0, min(1.0, base_confidence + progression_boost))
            stage_scores.append((stage, confidence, unique_keywords))
        
        # If no stages meet minimum keyword requirement
        if not stage_scores:
            default_stage = current_stage or self.defaults["default_profile"]["stage"]
            all_keywords = [kw for kws in stage_matches.values() for kw in kws]
            return JourneyEvent(
                stage=default_stage,
                trigger=f"Only {len(set(all_keywords))} keyword(s), need {keyword_match_min}",
                timestamp=datetime.now(),
                confidence=0.0,
                metadata={"matched_keywords": list(set(all_keywords)), "reason": "Below minimum threshold"}
            )
        
        # Select stage with highest confidence
        stage_scores.sort(key=lambda x: x[1], reverse=True)
        best_stage, best_confidence, best_keywords = stage_scores[0]
        
        # Check if confidence meets threshold
        if best_confidence < confidence_threshold:
            # Not confident enough to change stage
            default_stage = current_stage or self.defaults["default_profile"]["stage"]
            return JourneyEvent(
                stage=default_stage,
                trigger=f"Confidence {best_confidence:.2f} below {confidence_threshold}",
                timestamp=datetime.now(),
                confidence=best_confidence,
                metadata={
                    "matched_keywords": best_keywords,
                    "detected_stage": best_stage,
                    "reason": "Confidence too low to transition"
                }
            )
        
        # Validate stage progression (if enabled)
        if current_stage and not self._is_valid_transition(current_stage, best_stage):
            progression_only = self.defaults["detection"]["stage"].get("progression_only", False)
            if progression_only:
                # Reject invalid transition
                return JourneyEvent(
                    stage=current_stage,
                    trigger=f"Invalid transition {current_stage} -> {best_stage}",
                    timestamp=datetime.now(),
                    confidence=best_confidence,
                    metadata={
                        "matched_keywords": best_keywords,
                        "detected_stage": best_stage,
                        "reason": "Progression-only mode enabled"
                    }
                )
        
        # Return best match
        return JourneyEvent(
            stage=best_stage,
            trigger=f"Detected from keywords: {', '.join(best_keywords[:3])}",
            timestamp=datetime.now(),
            confidence=best_confidence,
            metadata={"matched_keywords": best_keywords, "previous_stage": current_stage}
        )
    
    def _is_valid_transition(self, from_stage: str, to_stage: str) -> bool:
        """
        Check if stage transition is valid based on next_stages config.
        
        Args:
            from_stage: Current stage
            to_stage: Proposed new stage
        
        Returns:
            True if transition is allowed
        """
        stage_config = self.journeys.get(from_stage, {})
        next_stages = stage_config.get("next_stages", [])
        
        # Always allow staying in same stage
        if from_stage == to_stage:
            return True
        
        # Check if to_stage is in allowed next_stages
        return to_stage in next_stages
    
    def get_stage_config(self, stage: str) -> Dict:
        """
        Get full stage configuration.
        
        Args:
            stage: Stage name (e.g., "Assessment")
        
        Returns:
            Stage configuration dict from journeys.yaml
        """
        return self.journeys.get(stage, self.journeys["Awareness"])
    
    def get_default_stage(self) -> str:
        """Get default stage from configuration."""
        return self.defaults["default_profile"]["stage"]
    
    def get_stage_order(self, stage: str) -> int:
        """
        Get numeric order of a stage (1-5).
        
        Args:
            stage: Stage name
        
        Returns:
            Stage order number
        """
        return self.stage_order.get(stage, 1)
    
    def get_next_stages(self, current_stage: str) -> List[str]:
        """
        Get list of valid next stages from current stage.
        
        Args:
            current_stage: Current stage name
        
        Returns:
            List of valid next stage names
        """
        stage_config = self.get_stage_config(current_stage)
        return stage_config.get("next_stages", [])
    
    def reload(self):
        """Reload journeys and defaults configuration from disk."""
        self.journeys = self._load_journeys()
        self.defaults = self._load_defaults()
        self.keyword_index = self._build_keyword_index()
