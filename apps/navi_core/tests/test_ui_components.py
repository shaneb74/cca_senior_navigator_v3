"""
Tests for UI Components - Progress Widgets

Part of Phase 5.2: Global Progress Tracker
"""

import pytest
import streamlit as st
from apps.navi_core.ui_components import (
    navi_progress_widget,
    navi_compact_progress,
    navi_milestone_badge,
    navi_progress_summary,
    _shorten_page_name,
    _get_milestone
)
from apps.navi_core.progress_manager import (
    mark_page_complete,
    reset_progress,
    load_progress_config
)


class TestMilestoneBadge:
    """Test milestone badge logic."""
    
    def test_milestone_badge_0_percent(self):
        """Test badge for 0% progress."""
        badge = navi_milestone_badge(0)
        # No milestone achieved yet
        assert badge is None
    
    def test_milestone_badge_25_percent(self):
        """Test badge for 25% progress."""
        badge = navi_milestone_badge(25)
        assert badge == "🌟 Getting Started"
    
    def test_milestone_badge_50_percent(self):
        """Test badge for 50% progress."""
        badge = navi_milestone_badge(50)
        assert badge == "⭐ Midpoint Milestone"
    
    def test_milestone_badge_75_percent(self):
        """Test badge for 75% progress."""
        badge = navi_milestone_badge(75)
        assert badge == "🎯 Nearly Complete"
    
    def test_milestone_badge_100_percent(self):
        """Test badge for 100% progress."""
        badge = navi_milestone_badge(100)
        assert badge == "🏆 Journey Complete"
    
    def test_milestone_badge_between_milestones(self):
        """Test badge for percentage between milestones."""
        badge = navi_milestone_badge(40)
        # Should return badge for previous milestone (25%)
        assert badge == "🌟 Getting Started"


class TestPageNameShortening:
    """Test page name shortening helper."""
    
    def test_shorten_common_names(self):
        """Test shortening of common page names."""
        assert _shorten_page_name("Care Preferences") == "Care Pref"
        assert _shorten_page_name("Cost Calculator") == "Costs"
        assert _shorten_page_name("Guided Care Plan (GCP)") == "GCP"
        assert _shorten_page_name("Financial Assessment") == "Finance"
        assert _shorten_page_name("Move Preferences") == "Location"
        assert _shorten_page_name("Concierge Hub") == "Concierge"
    
    def test_shorten_unknown_names(self):
        """Test shortening of unknown page names."""
        # Should truncate long names to 10 chars
        long_name = "Very Long Page Name That Exceeds Limit"
        shortened = _shorten_page_name(long_name)
        assert len(shortened) <= 10


class TestGetMilestone:
    """Test milestone checking helper."""
    
    def test_get_milestone_exact_match(self):
        """Test milestone detection at exact percentage."""
        cfg = load_progress_config()
        
        milestone = _get_milestone(25, cfg)
        assert milestone is not None
        assert "badge" in milestone
        assert milestone["badge"] == "🌟 Getting Started"
    
    def test_get_milestone_no_match(self):
        """Test milestone detection when no match."""
        cfg = load_progress_config()
        
        milestone = _get_milestone(37, cfg)
        assert milestone is None


class TestProgressSummary:
    """Test progress summary data structure."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_progress_summary_structure(self):
        """Test that progress summary returns expected structure."""
        reset_progress()
        summary = navi_progress_summary()
        
        required_keys = [
            "percent",
            "weighted_percent",
            "completed_count",
            "total_count"
        ]
        
        for key in required_keys:
            assert key in summary
    
    def test_progress_summary_empty(self):
        """Test progress summary with no pages completed."""
        reset_progress()
        summary = navi_progress_summary()
        
        assert summary["percent"] == 0
        assert summary["completed_count"] == 0
    
    def test_progress_summary_with_progress(self):
        """Test progress summary with some pages completed."""
        reset_progress()
        mark_page_complete("Welcome")
        mark_page_complete("Care Preferences")
        
        summary = navi_progress_summary()
        
        assert summary["percent"] > 0
        assert summary["completed_count"] == 2


class TestProgressWidget:
    """Test main progress widget rendering."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_progress_widget_renders_without_error(self):
        """Test that progress widget renders without raising exceptions."""
        reset_progress()
        try:
            navi_progress_widget()
        except Exception as e:
            pytest.fail(f"Progress widget raised exception: {e}")
    
    def test_progress_widget_weighted_mode(self):
        """Test progress widget in weighted mode."""
        reset_progress()
        try:
            navi_progress_widget(use_weighted=True)
        except Exception as e:
            pytest.fail(f"Weighted progress widget raised exception: {e}")
    
    def test_progress_widget_with_next_step(self):
        """Test progress widget with next step enabled."""
        reset_progress()
        try:
            navi_progress_widget(show_next_step=True)
        except Exception as e:
            pytest.fail(f"Progress widget with next step raised exception: {e}")
    
    def test_progress_widget_at_completion(self):
        """Test progress widget when all pages completed."""
        reset_progress()
        cfg = load_progress_config()
        
        for page in cfg.get("pages", []):
            mark_page_complete(page)
        
        try:
            navi_progress_widget(show_next_step=True)
        except Exception as e:
            pytest.fail(f"Completed progress widget raised exception: {e}")


class TestCompactProgress:
    """Test compact progress widget."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_compact_progress_renders_without_error(self):
        """Test that compact progress renders without raising exceptions."""
        reset_progress()
        try:
            navi_compact_progress()
        except Exception as e:
            pytest.fail(f"Compact progress raised exception: {e}")
    
    def test_compact_progress_with_percentage(self):
        """Test compact progress with percentage display."""
        reset_progress()
        try:
            navi_compact_progress(show_percentage=True)
        except Exception as e:
            pytest.fail(f"Compact progress with percentage raised exception: {e}")
    
    def test_compact_progress_without_percentage(self):
        """Test compact progress without percentage display."""
        reset_progress()
        try:
            navi_compact_progress(show_percentage=False)
        except Exception as e:
            pytest.fail(f"Compact progress without percentage raised exception: {e}")


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Reset progress before each test."""
        reset_progress()
    
    def test_widgets_handle_empty_config(self):
        """Test that widgets handle empty progress gracefully."""
        reset_progress()
        
        # All widgets should render without error at 0%
        try:
            navi_progress_widget()
            navi_compact_progress()
            summary = navi_progress_summary()
            
            assert summary["percent"] == 0
        except Exception as e:
            pytest.fail(f"Widget failed with empty progress: {e}")
    
    def test_milestone_badge_boundary_values(self):
        """Test milestone badge at boundary values."""
        # Test at exact milestones and one before/after
        test_values = [
            (0, None),  # No milestone yet
            (24, None),  # Before first milestone
            (25, "🌟 Getting Started"),  # First milestone
            (26, "🌟 Getting Started"),  # After first, returns previous
            (49, "🌟 Getting Started"),  # Before second milestone
            (50, "⭐ Midpoint Milestone"),  # Second milestone
            (51, "⭐ Midpoint Milestone"),
            (74, "⭐ Midpoint Milestone"),
            (75, "🎯 Nearly Complete"),  # Third milestone
            (76, "🎯 Nearly Complete"),
            (99, "🎯 Nearly Complete"),
            (100, "🏆 Journey Complete"),  # Final milestone
        ]
        
        for val, expected in test_values:
            badge = navi_milestone_badge(val)
            assert badge == expected, f"Expected {expected} for {val}%, got {badge}"
    
    def test_shorten_empty_page_name(self):
        """Test shortening empty page name."""
        result = _shorten_page_name("")
        assert result == ""
