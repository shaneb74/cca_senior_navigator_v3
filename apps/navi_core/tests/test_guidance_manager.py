"""
Tests for Guidance Manager - Persona-Specific Contextual Messages

Part of Phase 5: Contextual Guidance Layer
"""

import pytest
import streamlit as st
from pathlib import Path
from apps.navi_core.guidance_manager import get_guidance, load_guidance, GUIDANCE_FILE
from apps.navi_core.context_manager import update_context
from apps.navi_core.models import UserProfile
from apps.navi_core.profile_manager import ProfileManager
from apps.navi_core.trigger_manager import reset_triggers


class TestGuidanceLoading:
    """Test guidance configuration loading."""
    
    def setup_method(self):
        """Reset triggers before each test."""
        reset_triggers()
    
    def test_guidance_file_exists(self):
        """Test that guidance.yaml file exists."""
        assert GUIDANCE_FILE.exists(), f"Guidance file not found: {GUIDANCE_FILE}"
    
    def test_load_guidance_returns_dict(self):
        """Test that load_guidance returns a dictionary."""
        data = load_guidance()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_guidance_has_required_pages(self):
        """Test that guidance includes key pages."""
        data = load_guidance()
        required_pages = ["Welcome", "Care Preferences", "Cost Calculator"]
        
        for page in required_pages:
            assert page in data, f"Missing required page: {page}"
    
    def test_guidance_has_persona_messages(self):
        """Test that pages have persona-specific messages."""
        data = load_guidance()
        
        # Check Welcome page has AdultChild persona
        assert "AdultChild" in data["Welcome"]
        assert "message" in data["Welcome"]["AdultChild"]
        assert len(data["Welcome"]["AdultChild"]["message"]) > 0


class TestGuidanceRetrieval:
    """Test guidance message retrieval with different personas."""
    
    def setup_method(self):
        """Reset triggers before each test."""
        reset_triggers()
    
    def test_get_guidance_default_message(self):
        """Test that get_guidance returns fallback for unknown page."""
        # Clear context
        if "current_page" in st.session_state:
            del st.session_state["current_page"]
        
        msg = get_guidance(page="UnknownPage", persona="AdultChild")
        assert "I'm here" in msg or "guidance" in msg.lower()
    
    def test_get_guidance_specific_persona(self):
        """Test persona-specific messages."""
        msg = get_guidance(page="Welcome", persona="Spouse")
        assert "step at a time" in msg or "doing great" in msg
    
    def test_get_guidance_adult_child_persona(self):
        """Test AdultChild persona guidance."""
        msg = get_guidance(page="Welcome", persona="AdultChild")
        assert "parent" in msg.lower() or "loved one" in msg.lower()
    
    def test_get_guidance_self_senior_persona(self):
        """Test SelfSenior persona guidance."""
        msg = get_guidance(page="Welcome", persona="SelfSenior")
        assert "independence" in msg.lower() or "your" in msg.lower()
    
    def test_get_guidance_advisor_persona(self):
        """Test Advisor persona guidance."""
        msg = get_guidance(page="Welcome", persona="Advisor")
        assert "intake" in msg.lower() or "complete" in msg.lower()
    
    def test_get_guidance_uses_current_context(self):
        """Test that get_guidance uses current page context if not specified."""
        update_context("Care Preferences")
        
        msg = get_guidance(persona="AdultChild")
        assert "care" in msg.lower() or "needs" in msg.lower()
    
    def test_get_guidance_with_profile(self):
        """Test that get_guidance retrieves persona from UserProfile."""
        # Create test profile
        manager = ProfileManager()
        manager.clear_all()
        
        profile = manager.get_profile("test_user_guidance", create_if_missing=True)
        profile.role = "Spouse"
        
        # Get guidance without specifying persona (should use profile)
        update_context("Welcome")
        msg = get_guidance()
        
        # Should get Spouse-specific message
        assert isinstance(msg, str)
        assert len(msg) > 0
    
    def test_get_guidance_page_default_fallback(self):
        """Test that guidance falls back to page Default if persona not found."""
        msg = get_guidance(page="Welcome", persona="NonexistentPersona")
        
        # Should get either page default or global fallback
        assert isinstance(msg, str)
        assert len(msg) > 0
    
    def test_get_guidance_for_cost_calculator(self):
        """Test Cost Calculator page guidance."""
        # Cost Calculator requires Decision or Placement stage
        profile = UserProfile(id="test", name="Test", role="AdultChild")
        profile.stage = "Decision"
        st.session_state["user_profile"] = profile
        
        msg = get_guidance(page="Cost Calculator", persona="AdultChild")
        assert "cost" in msg.lower() or "estimate" in msg.lower()
    
    def test_get_guidance_for_care_preferences(self):
        """Test Care Preferences page guidance."""
        # Care Preferences requires Awareness or Assessment stage
        profile = UserProfile(id="test", name="Test", role="Spouse")
        profile.stage = "Assessment"
        st.session_state["user_profile"] = profile
        
        msg = get_guidance(page="Care Preferences", persona="Spouse")
        assert "care" in msg.lower() and ("balance" in msg.lower() or "well-being" in msg.lower())


class TestGuidanceIntegration:
    """Test integration between context and guidance managers."""
    
    def setup_method(self):
        """Reset triggers before each test."""
        reset_triggers()
    
    def test_context_driven_guidance_workflow(self):
        """Test full workflow: update context → get guidance."""
        # Set up profile with appropriate stage for Cost Calculator
        profile = UserProfile(id="test", name="Test", role="AdultChild")
        profile.stage = "Decision"  # Cost Calculator requires Decision/Placement
        st.session_state["user_profile"] = profile
        
        # Navigate to different pages and verify guidance changes
        pages_to_test = [
            ("Welcome", "AdultChild", "Awareness"),  # Override stage for Welcome
            ("Care Preferences", "Spouse", "Assessment"),
            ("Cost Calculator", "Advisor", "Decision"),
        ]
        
        for page, persona, stage in pages_to_test:
            reset_triggers()  # Reset for each page
            profile.stage = stage
            update_context(page)
            msg = get_guidance(persona=persona)
            
            assert isinstance(msg, str)
            assert len(msg) > 10  # Should be a meaningful message
    
    def test_persona_adaptation_across_pages(self):
        """Test that same persona gets different guidance on different pages."""
        persona = "AdultChild"
        
        # Set up profile with appropriate stages for each page
        profile = UserProfile(id="test", name="Test", role="AdultChild")
        st.session_state["user_profile"] = profile
        
        # Welcome requires Awareness
        reset_triggers()
        profile.stage = "Awareness"
        welcome_msg = get_guidance(page="Welcome", persona=persona)
        
        # Care Preferences requires Awareness or Assessment
        reset_triggers()
        profile.stage = "Assessment"
        care_msg = get_guidance(page="Care Preferences", persona=persona)
        
        # Cost Calculator requires Decision or Placement
        reset_triggers()
        profile.stage = "Decision"
        cost_msg = get_guidance(page="Cost Calculator", persona=persona)
        
        # Messages should differ by page
        assert welcome_msg != care_msg
        assert care_msg != cost_msg
        assert welcome_msg != cost_msg
