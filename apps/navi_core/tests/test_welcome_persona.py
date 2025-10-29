"""
Tests for welcome page persona selection integration.

Validates that UI persona choices map correctly to internal persona IDs
and that the integration with UserProfile works as expected.
"""

import pytest
from apps.navi_core.persona_adapter import PERSONA_CHOICES
from apps.navi_core.models import UserProfile


class TestPersonaChoicesMapping:
    """Test that PERSONA_CHOICES mapping is correct."""
    
    def test_persona_choices_exist(self):
        """Test that PERSONA_CHOICES constant is defined."""
        assert PERSONA_CHOICES is not None
        assert isinstance(PERSONA_CHOICES, dict)
        assert len(PERSONA_CHOICES) > 0
    
    def test_adult_child_mapping(self):
        """Test that Adult Child maps to AdultChild."""
        assert PERSONA_CHOICES["Adult Child (Son or Daughter)"] == "AdultChild"
    
    def test_spouse_mapping(self):
        """Test that Spouse / Partner maps to Spouse."""
        assert PERSONA_CHOICES["Spouse / Partner"] == "Spouse"
    
    def test_veteran_mapping(self):
        """Test that Veteran maps to Veteran."""
        assert PERSONA_CHOICES["Veteran"] == "Veteran"
    
    def test_advisor_mapping(self):
        """Test that Advisor / Professional maps to Advisor."""
        assert PERSONA_CHOICES["Advisor / Professional"] == "Advisor"
    
    def test_self_senior_mapping(self):
        """Test that Self maps to SelfSenior."""
        assert PERSONA_CHOICES["Self (I'm the one seeking care)"] == "SelfSenior"
    
    def test_unknown_mapping(self):
        """Test that Other / Unsure maps to Unknown."""
        assert PERSONA_CHOICES["Other / Unsure"] == "Unknown"
    
    def test_all_values_are_valid_personas(self):
        """Test that all mapped values are valid persona IDs."""
        valid_personas = {"AdultChild", "Spouse", "SelfSenior", "Veteran", "Advisor", "Unknown"}
        
        for ui_label, persona_id in PERSONA_CHOICES.items():
            assert persona_id in valid_personas, f"{ui_label} maps to invalid persona: {persona_id}"
    
    def test_no_duplicate_mappings(self):
        """Test that UI labels don't have conflicting mappings."""
        # Check that each UI label appears only once
        ui_labels = list(PERSONA_CHOICES.keys())
        assert len(ui_labels) == len(set(ui_labels)), "Duplicate UI labels found"


class TestUserProfileIntegration:
    """Test UserProfile integration with persona selection."""
    
    def test_create_profile_with_spouse_role(self):
        """Test creating UserProfile with Spouse role from UI selection."""
        relationship = "Spouse / Partner"
        role = PERSONA_CHOICES[relationship]
        
        profile = UserProfile(
            id="user_test_123",
            name="Mary",
            role=role,
            relationship=relationship,
            stage="Awareness"
        )
        
        assert profile.role == "Spouse"
        assert profile.relationship == "Spouse / Partner"
        assert profile.name == "Mary"
        assert profile.stage == "Awareness"
    
    def test_create_profile_with_adult_child_role(self):
        """Test creating UserProfile with AdultChild role from UI selection."""
        relationship = "Adult Child (Son or Daughter)"
        role = PERSONA_CHOICES[relationship]
        
        profile = UserProfile(
            id="user_test_456",
            name="John",
            role=role,
            relationship=relationship
        )
        
        assert profile.role == "AdultChild"
        assert profile.relationship == "Adult Child (Son or Daughter)"
    
    def test_create_profile_with_veteran_role(self):
        """Test creating UserProfile with Veteran role from UI selection."""
        relationship = "Veteran"
        role = PERSONA_CHOICES[relationship]
        
        profile = UserProfile(
            id="user_test_789",
            name="Bob",
            role=role,
            relationship=relationship
        )
        
        assert profile.role == "Veteran"
        assert profile.relationship == "Veteran"
    
    def test_profile_serialization_with_persona(self):
        """Test that UserProfile with persona can be serialized to dict."""
        relationship = "Spouse / Partner"
        role = PERSONA_CHOICES[relationship]
        
        profile = UserProfile(
            id="user_test_serial",
            name="Sarah",
            role=role,
            relationship=relationship,
            stage="Assessment"
        )
        
        profile_dict = profile.model_dump()
        
        assert profile_dict["role"] == "Spouse"
        assert profile_dict["relationship"] == "Spouse / Partner"
        assert profile_dict["name"] == "Sarah"
        assert profile_dict["stage"] == "Assessment"
    
    def test_profile_deserialization_from_session(self):
        """Test that UserProfile can be recreated from session_state dict."""
        session_data = {
            "id": "user_session_test",
            "name": "Alice",
            "role": "Advisor",
            "relationship": "Advisor / Professional",
            "stage": "Assessment",
            "preferences": {},
            "created_at": "2025-10-29T10:00:00",
            "updated_at": "2025-10-29T10:00:00"
        }
        
        # This simulates what happens when loading from session_state
        profile = UserProfile(**session_data)
        
        assert profile.id == "user_session_test"
        assert profile.role == "Advisor"
        assert profile.relationship == "Advisor / Professional"


class TestPersonaWorkflow:
    """Test complete persona selection workflow."""
    
    def test_ui_to_profile_workflow(self):
        """Test complete flow from UI selection to UserProfile creation."""
        # Step 1: User selects from UI dropdown
        ui_selection = "Spouse / Partner"
        
        # Step 2: Map to internal persona ID
        role = PERSONA_CHOICES[ui_selection]
        assert role == "Spouse"
        
        # Step 3: Create UserProfile
        profile = UserProfile(
            id="user_workflow_test",
            name="TestUser",
            role=role,
            relationship=ui_selection,
            stage="Awareness"
        )
        
        # Step 4: Serialize for session storage
        session_data = profile.model_dump()
        
        # Step 5: Verify session data is correct
        assert session_data["role"] == "Spouse"
        assert session_data["relationship"] == "Spouse / Partner"
        
        # Step 6: Simulate reloading from session
        reloaded_profile = UserProfile(**session_data)
        assert reloaded_profile.role == "Spouse"
        assert reloaded_profile.relationship == "Spouse / Partner"
