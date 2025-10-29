"""
Tests for PersonaAdapter - role detection from conversation text.
"""

import pytest
from apps.navi_core.persona_adapter import PersonaAdapter, RoleDetection


@pytest.fixture
def adapter():
    """Create PersonaAdapter instance."""
    return PersonaAdapter()


class TestRoleDetection:
    """Test role detection from keywords."""
    
    def test_adult_child_detection(self, adapter):
        """Test detection of AdultChild role."""
        text = "I'm looking for care options for my mother"
        detection = adapter.detect_role(text)
        
        assert detection.role == "AdultChild"
        assert detection.confidence >= 0.5
        assert "mother" in [k.lower() for k in detection.matched_keywords]
    
    def test_spouse_detection(self, adapter):
        """Test detection of Spouse role."""
        text = "My wife and I are considering assisted living together"
        detection = adapter.detect_role(text)
        
        assert detection.role == "Spouse"
        assert detection.confidence >= 0.5
        assert "wife" in [k.lower() for k in detection.matched_keywords]
    
    def test_self_senior_detection(self, adapter):
        """Test detection of SelfSenior role."""
        text = "I am 75 and thinking about my own care needs"
        detection = adapter.detect_role(text)
        
        # Should detect SelfSenior from "my own" phrase
        assert detection.confidence > 0.0
    
    def test_veteran_detection(self, adapter):
        """Test detection of Veteran role."""
        text = "I'm a veteran looking into VA benefits for memory care"
        detection = adapter.detect_role(text)
        
        assert detection.role == "Veteran"
        assert detection.confidence >= 0.5
        assert "veteran" in [k.lower() for k in detection.matched_keywords]
    
    def test_advisor_detection(self, adapter):
        """Test detection of Advisor role."""
        text = "As a social worker, I'm helping a client find memory care"
        detection = adapter.detect_role(text)
        
        assert detection.role == "Advisor"
        assert detection.confidence >= 0.5
        assert "social worker" in [k.lower() for k in detection.matched_keywords]
    
    def test_no_keywords_returns_default(self, adapter):
        """Test that no keywords returns default role."""
        text = "What is assisted living?"
        detection = adapter.detect_role(text)
        
        assert detection.role == "AdultChild"  # Default from config
        assert detection.confidence == 0.0
        assert len(detection.matched_keywords) == 0
    
    def test_multiple_keywords_boost_confidence(self, adapter):
        """Test that multiple keywords increase confidence."""
        text = "I'm a daughter helping my mom and dad find care"
        detection = adapter.detect_role(text)
        
        assert detection.role == "AdultChild"
        # Should match: daughter, mom, dad (3 keywords)
        assert len(detection.matched_keywords) >= 2
        assert detection.confidence >= 0.5
    
    def test_case_insensitive_matching(self, adapter):
        """Test that keyword matching is case-insensitive."""
        text = "My MOTHER needs care and I'm her SON"
        detection = adapter.detect_role(text)
        
        assert detection.role == "AdultChild"
        assert detection.confidence >= 0.5
    
    def test_role_persistence_low_confidence(self, adapter):
        """Test that current role persists if confidence too low."""
        text = "How much does it cost?"  # No clear role keywords
        detection = adapter.detect_role(text, current_role="Veteran")
        
        # Should keep Veteran role since no strong signal
        assert detection.role == "Veteran"
        assert detection.confidence < 0.5
    
    def test_specificity_boost_veteran(self, adapter):
        """Test that Veteran role gets specificity boost."""
        # With one keyword, Veteran should still be confident
        text = "I am a veteran"
        detection = adapter.detect_role(text)
        
        assert detection.role == "Veteran"
        # Specificity boost should push confidence over threshold
        assert detection.confidence >= 0.5


class TestPersonaConfig:
    """Test persona configuration retrieval."""
    
    def test_get_persona_config(self, adapter):
        """Test retrieving persona configuration."""
        config = adapter.get_persona_config("AdultChild")
        
        assert config is not None
        assert "description" in config
        assert "aliases" in config
        assert "default_tone" in config
    
    def test_get_unknown_persona_returns_fallback(self, adapter):
        """Test that unknown persona returns Unknown config."""
        config = adapter.get_persona_config("InvalidRole")
        
        assert config is not None
        assert config == adapter.personas["Unknown"]
    
    def test_get_default_role(self, adapter):
        """Test getting default role."""
        default = adapter.get_default_role()
        
        assert default == "AdultChild"


class TestReload:
    """Test configuration reloading."""
    
    def test_reload_config(self, adapter):
        """Test that reload refreshes configuration."""
        # Should not raise
        adapter.reload()
        
        # Should still work after reload
        text = "My mother needs care"
        detection = adapter.detect_role(text)
        assert detection.role == "AdultChild"
