"""
Tests for Trigger Manager - Smart Display Rules for Guidance

Part of Phase 5.1: Smart Triggers Layer
"""

import pytest
import streamlit as st
import time
from pathlib import Path
from apps.navi_core.trigger_manager import (
    should_show,
    reset_triggers,
    get_trigger_stats,
    load_triggers,
    TRIGGER_FILE
)
from apps.navi_core.models import UserProfile


class TestTriggerLoading:
    """Test trigger configuration loading."""
    
    def test_trigger_file_exists(self):
        """Test that triggers.yaml file exists."""
        assert TRIGGER_FILE.exists(), f"Trigger file not found: {TRIGGER_FILE}"
    
    def test_load_triggers_returns_dict(self):
        """Test that load_triggers returns a dictionary."""
        data = load_triggers()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_triggers_has_required_pages(self):
        """Test that triggers includes key pages."""
        data = load_triggers()
        required_pages = ["Welcome", "Care Preferences", "Cost Calculator", "Default"]
        
        for page in required_pages:
            assert page in data, f"Missing required page: {page}"
    
    def test_trigger_rules_structure(self):
        """Test that trigger rules have expected structure."""
        data = load_triggers()
        
        # Check Welcome page has expected keys
        welcome = data["Welcome"]
        assert "show_once_per_session" in welcome
        assert "cool_down_seconds" in welcome
        assert isinstance(welcome["show_once_per_session"], bool)
        assert isinstance(welcome["cool_down_seconds"], int)


class TestShowOncePerSession:
    """Test show_once_per_session behavior."""
    
    def setup_method(self):
        """Reset trigger state before each test."""
        reset_triggers()
    
    def test_shows_first_time(self):
        """Test that guidance shows on first visit."""
        reset_triggers()
        # Welcome requires Awareness stage
        assert should_show("Welcome", user_stage="Awareness") is True
    
    def test_hides_second_time(self):
        """Test that guidance hides on second visit (show_once_per_session)."""
        reset_triggers()
        
        # First call should show (Welcome requires Awareness stage)
        assert should_show("Welcome", user_stage="Awareness") is True
        
        # Second call should hide (Welcome has show_once_per_session: true)
        assert should_show("Welcome", user_stage="Awareness") is False
    
    def test_different_pages_tracked_separately(self):
        """Test that each page is tracked independently."""
        reset_triggers()
        
        # Show Welcome once (requires Awareness stage)
        assert should_show("Welcome", user_stage="Awareness") is True
        assert should_show("Welcome", user_stage="Awareness") is False  # Hidden on repeat
        
        # Care Preferences should still show (different page, supports Awareness/Assessment)
        # Note: Care Preferences has show_once_per_session: false in config
        assert should_show("Care Preferences", user_stage="Assessment") is True
    
    def test_seen_pages_stored_in_session(self):
        """Test that seen pages are stored in session_state."""
        reset_triggers()
        
        should_show("Welcome")
        
        stats = get_trigger_stats()
        assert "Welcome" in stats["seen_pages"]
    
    def test_reset_triggers_clears_seen_pages(self):
        """Test that reset_triggers clears seen pages."""
        should_show("Welcome")
        assert "Welcome" in get_trigger_stats()["seen_pages"]
        
        reset_triggers()
        assert len(get_trigger_stats()["seen_pages"]) == 0


class TestCooldownBehavior:
    """Test cool_down_seconds throttling."""
    
    def setup_method(self):
        """Reset trigger state before each test."""
        reset_triggers()
    
    def test_cooldown_blocks_immediate_repeat(self):
        """Test that cooldown prevents immediate repeat display."""
        reset_triggers()
        
        # Care Preferences has 60-second cooldown and requires Awareness/Assessment stage
        # First call should show
        assert should_show("Care Preferences", user_stage="Assessment") is True
        
        # Immediate second call should be blocked by cooldown
        # Note: Care Preferences has show_once_per_session: false
        # but cool_down_seconds: 60
        result = should_show("Care Preferences", user_stage="Assessment")
        # This will be False due to cooldown
        assert result is False
    
    def test_cooldown_allows_after_time_passes(self):
        """Test that cooldown allows display after time passes."""
        reset_triggers()
        
        # Set last guidance time to 120 seconds ago
        st.session_state["_guidance_last_time"] = time.time() - 120
        
        # FAQ has 30-second cooldown, so 120 seconds should be sufficient
        assert should_show("FAQ") is True
    
    def test_zero_cooldown_allows_repeats(self):
        """Test that zero cooldown allows immediate repeats."""
        reset_triggers()
        
        # Summary has cool_down_seconds: 0 and show_once_per_session: false
        assert should_show("Summary") is True
        assert should_show("Summary") is True  # Should still show
    
    def test_cooldown_timestamp_stored(self):
        """Test that cooldown timestamp is stored in session."""
        reset_triggers()
        
        before_time = time.time()
        should_show("Care Preferences")
        after_time = time.time()
        
        stats = get_trigger_stats()
        last_time = stats["last_time"]
        
        assert before_time <= last_time <= after_time


class TestStageAllowed:
    """Test stage_allowed conditional logic."""
    
    def setup_method(self):
        """Reset trigger state before each test."""
        reset_triggers()
    
    def test_shows_when_stage_matches(self):
        """Test that guidance shows when stage is in allowed list."""
        reset_triggers()
        
        # Welcome has stage_allowed: ["Awareness"]
        assert should_show("Welcome", user_stage="Awareness") is True
    
    def test_hides_when_stage_not_allowed(self):
        """Test that guidance hides when stage is not in allowed list."""
        reset_triggers()
        
        # Welcome has stage_allowed: ["Awareness"]
        # Should hide for Decision stage
        assert should_show("Welcome", user_stage="Decision") is False
    
    def test_shows_when_no_stage_restriction(self):
        """Test that guidance shows when stage_allowed is empty."""
        reset_triggers()
        
        # Summary has stage_allowed: [] (no restrictions)
        assert should_show("Summary", user_stage="Decision") is True
        assert should_show("Summary", user_stage="Awareness") is True
    
    def test_uses_profile_stage_when_not_specified(self):
        """Test that stage is read from user profile if not provided."""
        reset_triggers()
        
        # Create mock profile with Decision stage
        profile = UserProfile(id="test", name="Test", role="AdultChild")
        profile.stage = "Decision"
        st.session_state["user_profile"] = profile
        
        # Cost Calculator has stage_allowed: ["Decision", "Placement"]
        assert should_show("Cost Calculator") is True
    
    def test_defaults_to_awareness_stage(self):
        """Test that stage defaults to Awareness when no profile exists."""
        reset_triggers()
        
        # Clear profile
        if "user_profile" in st.session_state:
            del st.session_state["user_profile"]
        
        # Welcome allows Awareness stage
        assert should_show("Welcome") is True


class TestTriggerIntegration:
    """Test integration of multiple trigger rules."""
    
    def setup_method(self):
        """Reset trigger state before each test."""
        reset_triggers()
    
    def test_all_rules_evaluated_in_order(self):
        """Test that all rules are evaluated in correct order."""
        reset_triggers()
        
        # GCP Assessment has:
        # - show_once_per_session: false
        # - cool_down_seconds: 0
        # - stage_allowed: ["Assessment", "Decision"]
        
        # Should show for Assessment stage
        assert should_show("GCP Assessment", user_stage="Assessment") is True
        
        # Should hide for Awareness stage (fails stage check)
        assert should_show("GCP Assessment", user_stage="Awareness") is False
    
    def test_default_fallback_behavior(self):
        """Test that unknown pages use Default rules."""
        reset_triggers()
        
        # Unknown page should use Default rules
        # Default has show_once_per_session: true
        assert should_show("UnknownPage") is True
        assert should_show("UnknownPage") is False  # Second call hidden
    
    def test_trigger_stats_accuracy(self):
        """Test that get_trigger_stats returns accurate state."""
        reset_triggers()
        
        # Trigger multiple pages
        should_show("Welcome")
        should_show("Care Preferences")
        
        stats = get_trigger_stats()
        
        # Welcome should be in seen_pages
        assert "Welcome" in stats["seen_pages"]
        
        # Should have timestamp
        assert stats["last_time"] > 0
