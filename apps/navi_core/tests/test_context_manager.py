"""
Tests for Context Manager - Page Tracking for Contextual Guidance

Part of Phase 5: Contextual Guidance Layer
"""

import pytest
import streamlit as st
from apps.navi_core.context_manager import update_context, get_current_context


class TestContextTracking:
    """Test page context tracking functionality."""
    
    def test_update_context_stores_page(self):
        """Test that update_context stores page name in session_state."""
        # Clear any existing context
        if "current_page" in st.session_state:
            del st.session_state["current_page"]
        
        # Update context
        result = update_context("Care Preferences")
        
        # Verify stored and returned
        assert result == "Care Preferences"
        assert st.session_state["current_page"] == "Care Preferences"
    
    def test_get_current_context_retrieves_page(self):
        """Test that get_current_context retrieves stored page name."""
        # Set up context
        st.session_state["current_page"] = "Cost Calculator"
        
        # Retrieve context
        result = get_current_context()
        
        assert result == "Cost Calculator"
    
    def test_get_current_context_defaults_to_welcome(self):
        """Test that get_current_context returns 'Welcome' when not set."""
        # Clear any existing context
        if "current_page" in st.session_state:
            del st.session_state["current_page"]
        
        # Get context with no value set
        result = get_current_context()
        
        assert result == "Welcome"
    
    def test_context_update_and_retrieve_workflow(self):
        """Test full workflow of updating and retrieving context."""
        # Clear initial state
        if "current_page" in st.session_state:
            del st.session_state["current_page"]
        
        # Simulate navigation through pages
        update_context("Welcome")
        assert get_current_context() == "Welcome"
        
        update_context("For Someone Else")
        assert get_current_context() == "For Someone Else"
        
        update_context("GCP Assessment")
        assert get_current_context() == "GCP Assessment"
    
    def test_context_persists_across_calls(self):
        """Test that context persists in session_state."""
        update_context("Financial Assessment")
        
        # Multiple retrievals should return same value
        assert get_current_context() == "Financial Assessment"
        assert get_current_context() == "Financial Assessment"
        
        # Value should still be in session_state
        assert st.session_state["current_page"] == "Financial Assessment"
    
    def test_context_overwrites_previous_value(self):
        """Test that updating context overwrites previous page."""
        update_context("Page A")
        assert get_current_context() == "Page A"
        
        update_context("Page B")
        assert get_current_context() == "Page B"
        
        # Old value should be gone
        assert st.session_state["current_page"] == "Page B"
