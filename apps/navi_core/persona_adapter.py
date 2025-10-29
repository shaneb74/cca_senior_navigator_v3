"""
Persona Adapter - Role detection from conversation text.

Identifies user role (persona) based on keyword matching against personas.yaml.
Uses aliases and context to determine whether user is an AdultChild, Spouse,
SelfSenior, Veteran, Advisor, or Unknown.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from .paths import get_config_path


# Mapping from UI-friendly labels to internal persona IDs
# Used for explicit persona selection in onboarding flow
# Note: "Veteran" and "Self" are handled in dedicated flows
PERSONA_CHOICES = {
    "Adult Child (Son or Daughter)": "AdultChild",
    "Spouse / Partner": "Spouse",
    "Friend or Neighbor": "SelfSenior",  # fallback neutral role
    "Advisor / Professional": "Advisor",
    "Other / Unsure": "Unknown",
}


@dataclass
class RoleDetection:
    """Result of role detection analysis."""
    role: str
    confidence: float
    matched_keywords: List[str]
    context: str


class PersonaAdapter:
    """Detects user persona/role from conversation text."""
    
    def __init__(self, personas_path: Optional[Path] = None, defaults_path: Optional[Path] = None):
        """
        Initialize PersonaAdapter with configuration.
        
        Args:
            personas_path: Path to personas.yaml (defaults to config/personas.yaml)
            defaults_path: Path to defaults.yaml (defaults to config/defaults.yaml)
        """
        self.personas_path = personas_path or get_config_path("personas.yaml")
        self.defaults_path = defaults_path or get_config_path("defaults.yaml")
        
        # Load configurations
        self.personas = self._load_personas()
        self.defaults = self._load_defaults()
        
        # Build keyword index for fast lookup
        self.keyword_index = self._build_keyword_index()
        
    def _load_personas(self) -> Dict:
        """Load personas configuration from YAML."""
        with open(self.personas_path) as f:
            return yaml.safe_load(f)
    
    def _load_defaults(self) -> Dict:
        """Load defaults configuration from YAML."""
        with open(self.defaults_path) as f:
            return yaml.safe_load(f)
    
    def _build_keyword_index(self) -> Dict[str, str]:
        """
        Build reverse index: keyword -> role.
        
        Returns:
            Dict mapping each alias keyword to its role name.
        """
        index = {}
        for role, config in self.personas.items():
            aliases = config.get("aliases", [])
            for alias in aliases:
                # Store lowercase for case-insensitive matching
                index[alias.lower()] = role
        return index
    
    def detect_role(
        self,
        text: str,
        current_role: Optional[str] = None,
        confidence_threshold: Optional[float] = None
    ) -> RoleDetection:
        """
        Detect user role from conversation text.
        
        Args:
            text: User's message text
            current_role: User's current role (for persistence check)
            confidence_threshold: Min confidence to change role (defaults to config)
        
        Returns:
            RoleDetection with role, confidence, matched keywords, and context
        """
        if confidence_threshold is None:
            confidence_threshold = self.defaults["detection"]["role"]["confidence_threshold"]
        
        # Normalize text for matching
        text_lower = text.lower()
        
        # Find all matching keywords
        role_matches: Dict[str, List[str]] = {}  # role -> [matched_keywords]
        
        for keyword, role in self.keyword_index.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                if role not in role_matches:
                    role_matches[role] = []
                role_matches[role].append(keyword)
        
        # If no matches, return default or current
        if not role_matches:
            default_role = current_role or self.defaults["default_profile"]["role"]
            return RoleDetection(
                role=default_role,
                confidence=0.0,
                matched_keywords=[],
                context="No keywords matched; using default"
            )
        
        # Calculate confidence for each role
        role_scores = []
        for role, keywords in role_matches.items():
            # Confidence based on:
            # 1. Number of keyword matches (0.5 per match, max 1.0)
            # 2. Role specificity (Veteran/Advisor higher weight than AdultChild)
            base_confidence = min(1.0, len(keywords) * 0.5)
            
            # Apply specificity boost
            specificity_boost = 0.0
            if role in ["Veteran", "Advisor"]:
                specificity_boost = 0.2
            elif role == "SelfSenior":
                specificity_boost = 0.1
            
            confidence = min(1.0, base_confidence + specificity_boost)
            role_scores.append((role, confidence, keywords))
        
        # Select role with highest confidence
        role_scores.sort(key=lambda x: x[1], reverse=True)
        best_role, best_confidence, best_keywords = role_scores[0]
        
        # Check if confidence meets threshold
        if best_confidence < confidence_threshold:
            # Not confident enough to override current role
            default_role = current_role or self.defaults["default_profile"]["role"]
            return RoleDetection(
                role=default_role,
                confidence=best_confidence,
                matched_keywords=best_keywords,
                context=f"Confidence {best_confidence:.2f} below threshold {confidence_threshold}"
            )
        
        # Return best match
        return RoleDetection(
            role=best_role,
            confidence=best_confidence,
            matched_keywords=best_keywords,
            context=f"Detected from keywords: {', '.join(best_keywords)}"
        )
    
    def get_persona_config(self, role: str) -> Dict:
        """
        Get full persona configuration for a role.
        
        Args:
            role: Role name (e.g., "AdultChild")
        
        Returns:
            Persona configuration dict from personas.yaml
        """
        return self.personas.get(role, self.personas["Unknown"])
    
    def get_default_role(self) -> str:
        """Get default role from configuration."""
        return self.defaults["default_profile"]["role"]
    
    def reload(self):
        """Reload personas and defaults configuration from disk."""
        self.personas = self._load_personas()
        self.defaults = self._load_defaults()
        self.keyword_index = self._build_keyword_index()
