"""
Tests for ProfileManager - user profile storage and management.
"""

import pytest
from apps.navi_core.profile_manager import ProfileManager
from apps.navi_core.models import UserProfile, JourneyEvent


@pytest.fixture
def manager():
    """Create ProfileManager instance."""
    pm = ProfileManager()
    yield pm
    # Cleanup after each test
    pm.clear_all()


class TestProfileCreation:
    """Test user profile creation and retrieval."""
    
    def test_get_profile_creates_with_defaults(self, manager):
        """Test that get_profile creates profile with defaults if missing."""
        profile = manager.get_profile("user123")
        
        assert profile is not None
        assert profile.id == "user123"
        assert profile.role == "AdultChild"  # Default
        assert profile.stage == "Awareness"  # Default
        assert profile.preferences == {}
    
    def test_get_profile_returns_existing(self, manager):
        """Test that get_profile returns existing profile."""
        # Create profile
        profile1 = manager.get_profile("user456")
        profile1.role = "Veteran"
        manager.update_profile(profile1)
        
        # Retrieve again
        profile2 = manager.get_profile("user456")
        
        assert profile2.id == "user456"
        assert profile2.role == "Veteran"
    
    def test_get_profile_no_create(self, manager):
        """Test that create_if_missing=False returns None."""
        profile = manager.get_profile("nonexistent", create_if_missing=False)
        
        assert profile is None


class TestProfileUpdate:
    """Test profile updates."""
    
    def test_update_profile(self, manager):
        """Test updating profile fields."""
        profile = manager.get_profile("user789")
        profile.name = "John Doe"
        profile.role = "Spouse"
        profile.stage = "Assessment"
        
        updated = manager.update_profile(profile)
        
        assert updated.name == "John Doe"
        assert updated.role == "Spouse"
        assert updated.stage == "Assessment"
        
        # Verify persistence
        retrieved = manager.get_profile("user789")
        assert retrieved.name == "John Doe"
    
    def test_update_profile_changes_timestamp(self, manager):
        """Test that update changes updated_at timestamp."""
        profile = manager.get_profile("user111")
        original_time = profile.updated_at
        
        # Update something
        profile.role = "Advisor"
        updated = manager.update_profile(profile)
        
        assert updated.updated_at > original_time


class TestDetectionAndUpdate:
    """Test integrated detection and profile update."""
    
    def test_detect_and_update_role(self, manager):
        """Test that detect_and_update detects role from text."""
        text = "I'm a veteran looking for memory care options"
        
        profile, role_det, journey_evt = manager.detect_and_update("user222", text)
        
        assert profile.role == "Veteran"
        assert role_det.role == "Veteran"
        assert role_det.confidence >= 0.7
    
    def test_detect_and_update_stage(self, manager):
        """Test that detect_and_update detects stage from text."""
        text = "I want to compare different options and schedule a tour"
        
        profile, role_det, journey_evt = manager.detect_and_update("user333", text)
        
        assert profile.stage == "Assessment"
        assert journey_evt.stage == "Assessment"
        assert journey_evt.confidence >= 0.6
    
    def test_detect_and_update_both(self, manager):
        """Test detecting both role and stage simultaneously."""
        text = "As a social worker, I'm helping a client compare care options"
        
        profile, role_det, journey_evt = manager.detect_and_update("user444", text)
        
        # Should detect Advisor role
        assert profile.role == "Advisor"
        # Should detect Assessment stage
        assert profile.stage == "Assessment"
    
    def test_stage_transition_recorded(self, manager):
        """Test that stage transitions are recorded in history."""
        # Start in Awareness
        text1 = "I'm thinking about care for my mom"
        profile1, _, evt1 = manager.detect_and_update("user555", text1)
        
        # Move to Assessment
        text2 = "Now I want to compare facilities and tour some options"
        profile2, _, evt2 = manager.detect_and_update("user555", text2)
        
        # Check stage changed
        assert profile2.stage == "Assessment"
        
        # Check history recorded
        history = manager.get_stage_history("user555")
        assert len(history) >= 1
        assert history[-1].stage == "Assessment"


class TestPreferences:
    """Test preference management."""
    
    def test_set_preference(self, manager):
        """Test setting a user preference."""
        profile = manager.set_preference("user666", "tone_preference", "Empathetic")
        
        assert profile.preferences["tone_preference"] == "Empathetic"
    
    def test_get_preference(self, manager):
        """Test getting a user preference."""
        manager.set_preference("user777", "detail_level", "high")
        
        value = manager.get_preference("user777", "detail_level")
        
        assert value == "high"
    
    def test_get_preference_default(self, manager):
        """Test getting preference with default value."""
        value = manager.get_preference("user888", "nonexistent", default="fallback")
        
        assert value == "fallback"
    
    def test_get_preference_nonexistent_user(self, manager):
        """Test getting preference for nonexistent user returns default."""
        value = manager.get_preference("nonexistent", "key", default="default")
        
        assert value == "default"


class TestStageHistory:
    """Test stage transition history tracking."""
    
    def test_stage_history_empty_for_new_user(self, manager):
        """Test that new users have empty stage history."""
        history = manager.get_stage_history("newuser")
        
        assert history == []
    
    def test_stage_history_tracks_transitions(self, manager):
        """Test that stage transitions are tracked."""
        # Create multiple transitions
        manager.detect_and_update("user999", "I'm thinking about care")
        manager.detect_and_update("user999", "Now I want to compare options and tour")
        manager.detect_and_update("user999", "I'm ready to decide and choose")
        
        history = manager.get_stage_history("user999")
        
        # Should have transition events
        assert len(history) >= 1
        assert all(isinstance(evt, JourneyEvent) for evt in history)
    
    def test_stage_history_limited_length(self, manager):
        """Test that stage history is limited to max length."""
        # Simulate many transitions (more than max_length=10)
        for i in range(15):
            text = f"Stage transition number {i} with keywords compare tour"
            manager.detect_and_update("user000", text)
        
        history = manager.get_stage_history("user000")
        
        # Should be limited to 10 entries
        assert len(history) <= 10


class TestProfileDeletion:
    """Test profile deletion."""
    
    def test_delete_profile(self, manager):
        """Test deleting a profile."""
        # Create profile
        manager.get_profile("userdel")
        
        # Delete it
        result = manager.delete_profile("userdel")
        
        # Verify deleted (get without create should return None)
        profile = manager.get_profile("userdel", create_if_missing=False)
        assert profile is None
    
    def test_delete_nonexistent_profile(self, manager):
        """Test deleting nonexistent profile."""
        # Should not raise
        result = manager.delete_profile("nonexistent")
        
        # Result indicates not found
        assert result is not None  # Function should complete


class TestGetAllProfiles:
    """Test retrieving all profiles."""
    
    def test_get_all_profiles(self, manager):
        """Test getting all stored profiles."""
        # Create multiple profiles
        manager.get_profile("user1")
        manager.get_profile("user2")
        manager.get_profile("user3")
        
        all_profiles = manager.get_all_profiles()
        
        assert len(all_profiles) == 3
        assert "user1" in all_profiles
        assert "user2" in all_profiles
        assert "user3" in all_profiles


class TestClearAll:
    """Test clearing all profiles."""
    
    def test_clear_all(self, manager):
        """Test clearing all profiles and history."""
        # Create profiles
        manager.get_profile("user_a")
        manager.get_profile("user_b")
        manager.detect_and_update("user_a", "I want to compare options")
        
        # Clear all
        manager.clear_all()
        
        # Verify empty
        all_profiles = manager.get_all_profiles()
        assert len(all_profiles) == 0
        
        history = manager.get_stage_history("user_a")
        assert len(history) == 0
