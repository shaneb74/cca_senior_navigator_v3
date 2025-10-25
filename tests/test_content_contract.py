"""
Unit tests for the content contract system.

Tests token interpolation, possessive forms, fallback behavior, and immutability.
"""

import pytest
from unittest.mock import patch

from core.content_contract import (
    TokenContext,
    first_name,
    possessive,
    build_token_context,
    interpolate,
    resolve_content,
    _deep_copy,
    _merge_overrides
)


class TestFirstName:
    """Test first name extraction."""
    
    def test_single_name(self):
        assert first_name("Mary") == "Mary"
    
    def test_multiple_names(self):
        assert first_name("Mary Jo Smith") == "Mary"
    
    def test_empty_string(self):
        assert first_name("") == ""
    
    def test_whitespace_only(self):
        assert first_name("   ") == ""
    
    def test_none_input(self):
        assert first_name(None) == ""


class TestPossessive:
    """Test possessive form generation."""
    
    def test_regular_name(self):
        assert possessive("Mary") == "Mary's"
    
    def test_name_ending_in_s(self):
        assert possessive("James") == "James's"
    
    def test_name_ending_in_s_ap_style(self):
        assert possessive("James", ap_style=True) == "James'"
    
    def test_empty_name(self):
        assert possessive("") == "your"
    
    def test_none_name(self):
        assert possessive(None) == "your"
    
    def test_whitespace_name(self):
        assert possessive("   ") == "your"


class TestBuildTokenContext:
    """Test token context building from session state."""
    
    def test_with_person_name(self):
        session_state = {
            "person_a_name": "Shane Johnson",
            "relationship_type": "Parent",
            "zip_code": "90210",
            "state": "CA"
        }
        
        ctx = build_token_context(session_state)
        
        assert ctx.name == "Shane"
        assert ctx.name_possessive == "Shane's"
        assert ctx.relation == "your loved one"
        assert ctx.zip_code == "90210"
        assert ctx.state == "CA"
    
    def test_self_relationship(self):
        session_state = {
            "person_a_name": "John",
            "relationship_type": "Myself"
        }
        
        ctx = build_token_context(session_state)
        
        assert ctx.name == "John"
        assert ctx.relation == "you"
    
    def test_no_name_fallback(self):
        session_state = {}
        
        ctx = build_token_context(session_state)
        
        assert ctx.name == "you"
        assert ctx.name_possessive == "your"
        assert ctx.relation == "your loved one"
        assert ctx.zip_code == "your area"
    
    def test_legacy_name_keys(self):
        session_state = {
            "planning_for_name": "Alice"
        }
        
        ctx = build_token_context(session_state)
        
        assert ctx.name == "Alice"
        assert ctx.name_possessive == "Alice's"


class TestInterpolate:
    """Test token interpolation functionality."""
    
    def setup_method(self):
        self.ctx = TokenContext(
            name="Sarah",
            name_possessive="Sarah's",
            zip_code="94102",
            state="CA",
            tier="Assisted Living",
            hours="40",
            relation="your loved one"
        )
    
    def test_string_interpolation(self):
        text = "About {NAME} and {NAME_POS} care needs in {ZIP}"
        result = interpolate(text, self.ctx)
        
        assert result == "About Sarah and Sarah's care needs in 94102"
    
    def test_no_tokens(self):
        text = "This has no tokens"
        result = interpolate(text, self.ctx)
        
        assert result == text
    
    def test_list_interpolation(self):
        data = [
            "Care for {NAME}",
            "Located in {ZIP}",
            "No tokens here"
        ]
        
        result = interpolate(data, self.ctx)
        
        assert result == [
            "Care for Sarah",
            "Located in 94102", 
            "No tokens here"
        ]
    
    def test_dict_interpolation(self):
        data = {
            "title": "About {NAME}",
            "subtitle": "{NAME_POS} assessment",
            "metadata": {
                "location": "{ZIP}",
                "tier": "{TIER}"
            }
        }
        
        result = interpolate(data, self.ctx)
        
        expected = {
            "title": "About Sarah",
            "subtitle": "Sarah's assessment",
            "metadata": {
                "location": "94102",
                "tier": "Assisted Living"
            }
        }
        
        assert result == expected
    
    def test_header_name_truncation(self):
        # Test with long name
        long_ctx = TokenContext(name="Bartholomew Alexander", name_possessive="Bartholomew Alexander's")
        text = "Welcome {NAME}"
        
        result = interpolate(text, long_ctx, is_header=True)
        
        assert "..." in result
        assert len(result.replace("Welcome ", "").replace("...", "")) <= 20
    
    def test_unknown_token_warning(self, caplog):
        text = "Hello {UNKNOWN_TOKEN}"
        
        result = interpolate(text, self.ctx)
        
        # Should leave unknown token unchanged
        assert result == "Hello {UNKNOWN_TOKEN}"
        
        # Should log warning (check if logging is captured)
        # Note: This test may need adjustment based on logging setup


class TestResolveContent:
    """Test content resolution with validation, overrides, and interpolation."""
    
    def test_basic_resolution(self):
        spec = {
            "copy": {
                "title": "Care for {NAME}",
                "subtitle": "Assessment for {NAME_POS} needs"
            }
        }
        
        ctx = TokenContext(name="Mike", name_possessive="Mike's")
        
        result = resolve_content(spec, None, ctx)
        
        expected = {
            "copy": {
                "title": "Care for Mike",
                "subtitle": "Assessment for Mike's needs"
            }
        }
        
        assert result == expected
    
    def test_with_overrides(self):
        base_spec = {
            "copy": {
                "title": "Original title for {NAME}",
                "subtitle": "Original subtitle"
            }
        }
        
        overrides = {
            "copy": {
                "title": "Override title for {NAME}"
            }
        }
        
        ctx = TokenContext(name="Lisa", name_possessive="Lisa's")
        
        result = resolve_content(base_spec, overrides, ctx)
        
        expected = {
            "copy": {
                "title": "Override title for Lisa",
                "subtitle": "Original subtitle"
            }
        }
        
        assert result == expected
    
    def test_immutability(self):
        """Test that original objects are not modified."""
        original_spec = {
            "copy": {
                "title": "Care for {NAME}"
            }
        }
        
        original_copy = original_spec.copy()
        ctx = TokenContext(name="Tom", name_possessive="Tom's")
        
        result = resolve_content(original_spec, None, ctx)
        
        # Original should be unchanged
        assert original_spec == original_copy
        
        # Result should be different
        assert result != original_spec
        assert result["copy"]["title"] == "Care for Tom"


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_deep_copy(self):
        original = {
            "level1": {
                "level2": ["item1", "item2"],
                "value": "test"
            }
        }
        
        copy = _deep_copy(original)
        
        # Should be equal but not same object
        assert copy == original
        assert copy is not original
        assert copy["level1"] is not original["level1"]
        assert copy["level1"]["level2"] is not original["level1"]["level2"]
    
    def test_merge_overrides(self):
        base = {
            "section1": {
                "key1": "value1",
                "key2": "value2"
            },
            "section2": "base_value"
        }
        
        overrides = {
            "section1": {
                "key1": "override_value1"
            },
            "section3": "new_value"
        }
        
        result = _merge_overrides(base, overrides)
        
        expected = {
            "section1": {
                "key1": "override_value1",
                "key2": "value2"
            },
            "section2": "base_value",
            "section3": "new_value"
        }
        
        assert result == expected


class TestTokenContextEdgeCases:
    """Test edge cases in token context building."""
    
    def test_empty_session_state(self):
        ctx = build_token_context({})
        
        assert ctx.name == "you"
        assert ctx.name_possessive == "your"
        assert ctx.zip_code == "your area"
        assert ctx.relation == "your loved one"
    
    def test_planning_for_relationship_self(self):
        session_state = {
            "planning_for_relationship": "self",
            "person_a_name": "Alex"
        }
        
        ctx = build_token_context(session_state)
        
        assert ctx.relation == "you"
    
    def test_planning_for_relationship_someone_else(self):
        session_state = {
            "planning_for_relationship": "someone_else",
            "person_a_name": "Alex"
        }
        
        ctx = build_token_context(session_state)
        
        assert ctx.relation == "your loved one"


# Integration test to verify the full pipeline
class TestIntegration:
    """Integration tests for the full content contract pipeline."""
    
    def test_full_pipeline_with_session_state(self):
        """Test the full pipeline with realistic session state."""
        
        # Mock session state
        with patch('streamlit.session_state', {
            "person_a_name": "Margaret Ann",
            "relationship_type": "Parent",
            "zip_code": "10001"
        }):
            
            spec = {
                "module": {
                    "display": {
                        "title": "Care Planning for {NAME}",
                        "subtitle": "We'll help find the right care for {NAME} in {ZIP}"
                    }
                },
                "copy": {
                    "welcome": "Welcome! Let's plan care for {RELATION}.",
                    "next_steps": [
                        "Assess {NAME_POS} daily needs",
                        "Review options in {ZIP}",
                        "Connect with providers"
                    ]
                }
            }
            
            # This should work with the actual session state
            from core.content_contract import resolve_content, build_token_context
            import streamlit as st
            
            ctx = build_token_context(st.session_state)
            result = resolve_content(spec, None, ctx)
            
            assert result["module"]["display"]["title"] == "Care Planning for Margaret"
            assert "Margaret" in result["module"]["display"]["subtitle"]
            assert "10001" in result["module"]["display"]["subtitle"]
            assert result["copy"]["welcome"] == "Welcome! Let's plan care for your loved one."
            assert result["copy"]["next_steps"][0] == "Assess Margaret's daily needs"


if __name__ == "__main__":
    pytest.main([__file__])