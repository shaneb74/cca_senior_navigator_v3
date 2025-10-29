"""
Profile Manager - User profile storage and retrieval.

Manages UserProfile objects with role, stage, and preferences. Integrates
PersonaAdapter and JourneyManager for automatic profile updates based on
conversation text.
"""

import uuid
from typing import Dict, Optional
from datetime import datetime

from .models import UserProfile, JourneyEvent
from .persona_adapter import PersonaAdapter, RoleDetection
from .journey_manager import JourneyManager


class ProfileManager:
    """Manages user profiles with role and stage detection."""
    
    def __init__(
        self,
        persona_adapter: Optional[PersonaAdapter] = None,
        journey_manager: Optional[JourneyManager] = None
    ):
        """
        Initialize ProfileManager.
        
        Args:
            persona_adapter: PersonaAdapter instance (creates new if None)
            journey_manager: JourneyManager instance (creates new if None)
        """
        self.persona_adapter = persona_adapter or PersonaAdapter()
        self.journey_manager = journey_manager or JourneyManager()
        
        # In-memory storage (upgrade to DB in future)
        self._profiles: Dict[str, UserProfile] = {}
        
        # Track stage history
        self._stage_history: Dict[str, list[JourneyEvent]] = {}
    
    def get_profile(self, user_id: str, create_if_missing: bool = True, session_state: Optional[Dict] = None) -> Optional[UserProfile]:
        """
        Retrieve user profile by ID.
        
        Args:
            user_id: User identifier
            create_if_missing: Create new profile with defaults if not found
            session_state: Optional session state dict to check for pre-existing profile
        
        Returns:
            UserProfile or None if not found and create_if_missing=False
        """
        # Check if profile exists in storage
        if user_id in self._profiles:
            return self._profiles[user_id]
        
        # Check if profile exists in session_state (from onboarding)
        if session_state and "user_profile" in session_state:
            try:
                profile = UserProfile(**session_state["user_profile"])
                self._profiles[user_id] = profile
                self._stage_history[user_id] = []
                return profile
            except Exception:
                # If profile data is invalid, continue to create new
                pass
        
        if create_if_missing:
            # Create new profile with defaults
            profile = UserProfile(
                id=user_id,
                name=None,
                role=self.persona_adapter.get_default_role(),
                relationship=None,
                stage=self.journey_manager.get_default_stage(),
                preferences={},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self._profiles[user_id] = profile
            self._stage_history[user_id] = []
            return profile
        
        return None
    
    def update_profile(self, profile: UserProfile) -> UserProfile:
        """
        Update existing profile.
        
        Args:
            profile: UserProfile with updated fields
        
        Returns:
            Updated UserProfile
        """
        profile.updated_at = datetime.now()
        self._profiles[profile.id] = profile
        return profile
    
    def detect_and_update(
        self,
        user_id: str,
        text: str,
        force_detection: bool = False
    ) -> tuple[UserProfile, RoleDetection, JourneyEvent]:
        """
        Detect role and stage from text and update profile.
        
        Args:
            user_id: User identifier
            text: Conversation text to analyze
            force_detection: Force detection even if confidence low
        
        Returns:
            Tuple of (updated_profile, role_detection, journey_event)
        """
        # Get or create profile
        profile = self.get_profile(user_id)
        
        # Detect role
        role_detection = self.persona_adapter.detect_role(
            text=text,
            current_role=profile.role,
            confidence_threshold=None if force_detection else None  # Use default
        )
        
        # Detect stage
        journey_event = self.journey_manager.detect_stage(
            text=text,
            current_stage=profile.stage,
            confidence_threshold=None if force_detection else None  # Use default
        )
        
        # Update profile if role changed
        if role_detection.role != profile.role:
            profile.role = role_detection.role
            profile.updated_at = datetime.now()
        
        # Update profile if stage changed
        if journey_event.stage != profile.stage:
            # Record stage transition
            if user_id not in self._stage_history:
                self._stage_history[user_id] = []
            
            self._stage_history[user_id].append(journey_event)
            
            # Limit history length
            max_length = 10  # TODO: Load from defaults
            if len(self._stage_history[user_id]) > max_length:
                self._stage_history[user_id] = self._stage_history[user_id][-max_length:]
            
            profile.stage = journey_event.stage
            profile.updated_at = datetime.now()
        
        # Save updated profile
        self.update_profile(profile)
        
        return profile, role_detection, journey_event
    
    def get_stage_history(self, user_id: str) -> list[JourneyEvent]:
        """
        Get stage transition history for user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of JourneyEvent objects in chronological order
        """
        return self._stage_history.get(user_id, [])
    
    def set_preference(self, user_id: str, key: str, value: any) -> UserProfile:
        """
        Set a user preference.
        
        Args:
            user_id: User identifier
            key: Preference key
            value: Preference value
        
        Returns:
            Updated UserProfile
        """
        profile = self.get_profile(user_id)
        profile.preferences[key] = value
        return self.update_profile(profile)
    
    def get_preference(self, user_id: str, key: str, default: any = None) -> any:
        """
        Get a user preference.
        
        Args:
            user_id: User identifier
            key: Preference key
            default: Default value if not found
        
        Returns:
            Preference value or default
        """
        profile = self.get_profile(user_id, create_if_missing=False)
        if profile is None:
            return default
        return profile.preferences.get(key, default)
    
    def delete_profile(self, user_id: str) -> bool:
        """
        Delete user profile and history.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if deleted, False if not found
        """
        if user_id in self._profiles:
            del self._profiles[user_id]
        if user_id in self._stage_history:
            del self._stage_history[user_id]
        return user_id in self._profiles
    
    def get_all_profiles(self) -> Dict[str, UserProfile]:
        """
        Get all stored profiles.
        
        Returns:
            Dict mapping user_id -> UserProfile
        """
        return self._profiles.copy()
    
    def clear_all(self):
        """Clear all profiles and history (useful for testing)."""
        self._profiles.clear()
        self._stage_history.clear()
