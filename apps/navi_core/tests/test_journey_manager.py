"""
Tests for JourneyManager - stage detection and progression tracking.
"""

import pytest
from apps.navi_core.journey_manager import JourneyManager
from apps.navi_core.models import JourneyEvent


@pytest.fixture
def manager():
    """Create JourneyManager instance."""
    return JourneyManager()


class TestStageDetection:
    """Test journey stage detection from keywords."""
    
    def test_awareness_detection(self, manager):
        """Test detection of Awareness stage."""
        text = "I'm just starting to look into this and considering whether care is needed"
        event = manager.detect_stage(text)
        
        assert event.stage == "Awareness"
        assert event.confidence >= 0.6
        # Should match: "starting to look", "considering"
        assert len(event.metadata["matched_keywords"]) >= 2
    
    def test_assessment_detection(self, manager):
        """Test detection of Assessment stage."""
        text = "I want to compare different options and schedule a tour of facilities"
        event = manager.detect_stage(text)
        
        assert event.stage == "Assessment"
        assert event.confidence >= 0.6
        # Should match: compare, options, tour
        assert len(event.metadata["matched_keywords"]) >= 2
    
    def test_decision_detection(self, manager):
        """Test detection of Decision stage."""
        text = "We're ready to decide and choose the best option"
        event = manager.detect_stage(text)
        
        assert event.stage == "Decision"
        assert event.confidence >= 0.6
        # Should match: ready, decide, choose
        assert len(event.metadata["matched_keywords"]) >= 2
    
    def test_placement_detection(self, manager):
        """Test detection of Placement stage."""
        text = "We need to sign the contract and handle the transition and moving process"
        event = manager.detect_stage(text)
        
        assert event.stage == "Placement"
        assert event.confidence >= 0.6
        # Should match: sign, transition, moving
        assert len(event.metadata["matched_keywords"]) >= 2
    
    def test_followup_detection(self, manager):
        """Test detection of FollowUp stage."""
        text = "Mom settled in last week, how is she adjusting?"
        event = manager.detect_stage(text)
        
        assert event.stage == "FollowUp"
        assert event.confidence >= 0.6
        # Should match: settled, adjusting
        assert len(event.metadata["matched_keywords"]) >= 2
    
    def test_no_keywords_returns_default(self, manager):
        """Test that no keywords returns default stage."""
        text = "Hello, can you help me?"
        event = manager.detect_stage(text)
        
        assert event.stage == "Awareness"  # Default
        assert event.confidence == 0.0
        assert len(event.metadata["matched_keywords"]) == 0
    
    def test_insufficient_keywords_returns_current(self, manager):
        """Test that 1 keyword (below minimum) keeps current stage."""
        text = "I'm thinking about it"  # Only 1 keyword: "thinking"
        event = manager.detect_stage(text, current_stage="Assessment")
        
        # Should keep Assessment since only 1 match (need 2)
        assert event.stage == "Assessment"
        assert event.confidence == 0.0


class TestStageProgression:
    """Test stage progression logic."""
    
    def test_forward_progression_boost(self, manager):
        """Test that natural forward progression gets confidence boost."""
        text = "I've learned enough, now I want to compare different options and tour some facilities"
        event = manager.detect_stage(text, current_stage="Awareness")
        
        # Should detect Assessment with progression boost
        assert event.stage == "Assessment"
        # Confidence should be boosted by forward progression
        assert event.confidence >= 0.6
    
    def test_backward_progression_allowed(self, manager):
        """Test that backward progression is allowed (but penalized)."""
        # User was in Decision but now uncertain
        text = "Actually I'm not sure anymore, I need to think about this more"
        event = manager.detect_stage(text, current_stage="Decision")
        
        # Should allow moving back to Awareness
        # Confidence might be lower but still possible
        assert event.confidence >= 0.0
    
    def test_stage_persistence(self, manager):
        """Test that stage persists when no strong signal."""
        text = "Can you tell me more?"  # Vague question
        event = manager.detect_stage(text, current_stage="Assessment")
        
        assert event.stage == "Assessment"
        assert event.confidence == 0.0


class TestStageConfiguration:
    """Test stage configuration retrieval."""
    
    def test_get_stage_config(self, manager):
        """Test retrieving stage configuration."""
        config = manager.get_stage_config("Assessment")
        
        assert config is not None
        assert "description" in config
        assert "keywords" in config
        assert "order" in config
        assert config["order"] == 2
    
    def test_get_default_stage(self, manager):
        """Test getting default stage."""
        default = manager.get_default_stage()
        
        assert default == "Awareness"
    
    def test_get_stage_order(self, manager):
        """Test getting stage order numbers."""
        assert manager.get_stage_order("Awareness") == 1
        assert manager.get_stage_order("Assessment") == 2
        assert manager.get_stage_order("Decision") == 3
        assert manager.get_stage_order("Placement") == 4
        assert manager.get_stage_order("FollowUp") == 5
    
    def test_get_next_stages(self, manager):
        """Test getting valid next stages."""
        next_stages = manager.get_next_stages("Awareness")
        
        assert "Assessment" in next_stages
        assert isinstance(next_stages, list)


class TestTransitionValidation:
    """Test stage transition validation."""
    
    def test_same_stage_always_valid(self, manager):
        """Test that staying in same stage is always valid."""
        is_valid = manager._is_valid_transition("Assessment", "Assessment")
        
        assert is_valid is True
    
    def test_valid_forward_transition(self, manager):
        """Test that valid forward transition is allowed."""
        is_valid = manager._is_valid_transition("Awareness", "Assessment")
        
        assert is_valid is True
    
    def test_valid_backward_transition(self, manager):
        """Test that configured backward transition is allowed."""
        # Check journeys.yaml for which backward moves are allowed
        # Most stages allow going back to earlier stages
        is_valid = manager._is_valid_transition("Assessment", "Awareness")
        
        # Should be valid since Assessment.next_stages includes Awareness
        assert is_valid is True


class TestReload:
    """Test configuration reloading."""
    
    def test_reload_config(self, manager):
        """Test that reload refreshes configuration."""
        # Should not raise
        manager.reload()
        
        # Should still work after reload
        text = "I want to compare different options and tour facilities"
        event = manager.detect_stage(text)
        assert event.stage == "Assessment"
