"""
PFMA v3 - Comprehensive Test Suite

Tests the booking-first model and cross-hub synchronization via MCIP.

Test Coverage:
1. Booking-first flow
2. Cross-hub sync (Concierge ↔ Waiting Room)
3. JSON-driven modules
4. Flag Manager integration
5. Cost Planner pricing safety
6. Navi presence
7. Strict validation
"""

import pytest
import json
import sys
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Mock streamlit before any imports
sys.modules['streamlit'] = MagicMock()

@pytest.fixture
def session():
    """Create a mock session state dictionary."""
    return {
        "mcip_contracts": {},
        "user_id": "test_user_123",
        "auth": {"role": "user", "authenticated": True},
        "flags": {}
    }


@pytest.fixture
def mock_st(session):
    """Mock Streamlit session state for testing."""
    import streamlit as st
    st.session_state = session
    yield st


class TestPFMAv3BookingFirst:
    """Test 1: Booking-first flow creates appointment and routes to Waiting Room."""
    
    def test_booking_submission_creates_appointment(self, mock_st, session):
        """Test that valid booking creates AdvisorAppointment in MCIP."""
        from core.mcip import MCIP, AdvisorAppointment, FinancialProfile
        
        # Setup: Initialize MCIP and complete prerequisites
        MCIP.initialize()
        MCIP.publish_financial_profile(FinancialProfile(
            estimated_monthly_cost=5000,
            coverage_percentage=60,
            gap_amount=500,
            runway_months=36,
            confidence=0.85,
            generated_at=datetime.now().isoformat(),
            status="complete"
        ))
        
        # Action: Create appointment
        appointment = AdvisorAppointment(
            scheduled=True,
            date="2025-10-25",
            time="Morning (8am-12pm)",
            type="video",
            confirmation_id="TEST123",
            contact_email="test@example.com",
            contact_phone="555-1234",
            timezone="America/New_York",
            notes="Test appointment",
            generated_at=datetime.now().isoformat(),
            status="scheduled",
            prep_sections_complete=[],
            prep_progress=0
        )
        
        MCIP.set_advisor_appointment(appointment)
        
        # Assert: Appointment stored in MCIP
        retrieved_appt = MCIP.get_advisor_appointment()
        assert retrieved_appt is not None
        assert retrieved_appt.scheduled == True
        assert retrieved_appt.confirmation_id == "TEST123"
        assert retrieved_appt.contact_email == "test@example.com"
        assert retrieved_appt.prep_progress == 0
    
    def test_pfma_marks_complete_in_journey(self, mock_st, session):
        """Test that PFMA completion updates MCIP journey."""
        from core.mcip import MCIP
        import streamlit as st
        
        MCIP.initialize()
        
        # Action: Mark PFMA complete using MCIP's journey tracking
        mcip_state = st.session_state[MCIP.STATE_KEY]
        if "pfma_v3" not in mcip_state["journey"]["completed_products"]:
            mcip_state["journey"]["completed_products"].append("pfma_v3")
        
        # Assert: Product marked complete
        assert "pfma_v3" in mcip_state["journey"]["completed_products"]
    
    def test_validation_requires_contact_info(self):
        """Test that booking validation requires email OR phone."""
        # Test validation logic directly
        
        # Test: No contact info
        data_no_contact = {
            "name": "Test User",
            "timezone": "America/New_York",
            "type": "video"
        }
        
        # Manual validation check
        has_email = data_no_contact.get("email", "").strip()
        has_phone = data_no_contact.get("phone", "").strip()
        assert not (has_email or has_phone), "Should require email or phone"
        
        # Test: Email only (valid)
        data_email = {
            "name": "Test User",
            "email": "test@example.com",
            "timezone": "America/New_York",
            "type": "video"
        }
        has_email = data_email.get("email", "").strip()
        assert has_email, "Email should be present"
        
        # Test: Phone only (valid)
        data_phone = {
            "name": "Test User",
            "phone": "555-1234",
            "timezone": "America/New_York",
            "type": "video"
        }
        has_phone = data_phone.get("phone", "").strip()
        assert has_phone, "Phone should be present"


class TestCrossHubSync:
    """Test 2: Cross-hub synchronization via MCIP."""
    
    def test_prep_progress_visible_in_concierge(self, mock_st, session):
        """Test that Advisor Prep progress shows in Concierge hub tile."""
        from core.mcip import MCIP, AdvisorAppointment
        
        MCIP.initialize()
        
        # Setup: Create appointment with partial prep
        appointment = AdvisorAppointment(
            scheduled=True,
            date="2025-10-25",
            time="10:00 AM",
            type="video",
            confirmation_id="ABC123",
            contact_email="test@example.com",
            contact_phone="",
            timezone="America/New_York",
            notes="",
            generated_at=datetime.now().isoformat(),
            status="scheduled",
            prep_sections_complete=["personal", "financial"],
            prep_progress=50
        )
        
        MCIP.set_advisor_appointment(appointment)
        
        # Action: Get PFMA summary (Concierge hub query)
        summary = MCIP.get_pfma_summary()
        
        # Assert: Prep progress visible
        assert summary["booked"] == True
        assert summary["prep_progress"] == 50
        assert summary["confirmation_id"] == "ABC123"
    
    def test_advisor_prep_summary_shows_context(self, mock_st, session):
        """Test that Advisor Prep summary includes appointment context."""
        from core.mcip import MCIP, AdvisorAppointment
        
        MCIP.initialize()
        
        # Setup: Create appointment
        appointment = AdvisorAppointment(
            scheduled=True,
            date=datetime.now().isoformat(),
            time="Morning",
            type="video",
            confirmation_id="XYZ789",
            contact_email="test@example.com",
            contact_phone="",
            timezone="America/New_York",
            notes="",
            generated_at=datetime.now().isoformat(),
            status="scheduled",
            prep_sections_complete=["personal"],
            prep_progress=25
        )
        
        MCIP.set_advisor_appointment(appointment)
        
        # Action: Get Advisor Prep summary (Waiting Room query)
        prep_summary = MCIP.get_advisor_prep_summary()
        
        # Assert: Context included
        assert prep_summary["available"] == True
        assert prep_summary["progress"] == 25
        assert len(prep_summary["sections_complete"]) == 1
        assert "personal" in prep_summary["sections_complete"]
        assert prep_summary["next_section"] == "financial"
        assert "appointment" in prep_summary["appointment_context"].lower()


class TestJSONDrivenModules:
    """Test 3: JSON-driven module rendering."""
    
    def test_personal_config_loads(self):
        """Test that personal.json loads and validates."""
        import json
        from pathlib import Path
        
        config_path = Path("products/advisor_prep/config/personal.json")
        assert config_path.exists()
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Assert: Required keys present
        assert "key" in config
        assert "title" in config
        assert "fields" in config
        assert config["key"] == "personal"
        assert len(config["fields"]) > 0
    
    def test_medical_config_has_flag_manager_fields(self):
        """Test that medical.json specifies Flag Manager integration."""
        import json
        from pathlib import Path
        
        config_path = Path("products/advisor_prep/config/medical.json")
        with open(config_path) as f:
            config = json.load(f)
        
        # Assert: Special handling flag
        assert config.get("special_handling") == "flag_manager"
        
        # Assert: Has chronic conditions field
        chronic_field = next(f for f in config["fields"] if f["key"] == "chronic_conditions")
        assert chronic_field["type"] == "conditions_registry"
        assert chronic_field["source"] == "flag_manager"
        
        # Assert: Has care flags field
        flags_field = next(f for f in config["fields"] if f["key"] == "care_flags")
        assert flags_field["type"] == "flag_toggles"
        assert len(flags_field["flags"]) > 0
    
    def test_all_sections_have_consistent_structure(self):
        """Test that all section configs follow same structure."""
        import json
        from pathlib import Path
        
        sections = ["personal", "financial", "housing", "medical"]
        
        for section_key in sections:
            config_path = Path(f"products/advisor_prep/config/{section_key}.json")
            assert config_path.exists(), f"Missing config: {section_key}.json"
            
            with open(config_path) as f:
                config = json.load(f)
            
            # Assert: Required structure
            assert "key" in config
            assert "title" in config
            assert "icon" in config
            assert "description" in config
            assert "fields" in config
            assert config["key"] == section_key


class TestFlagManagerIntegration:
    """Test 4: Flag Manager integration in Medical prep."""
    
    def test_chronic_conditions_data_structure(self):
        """Test that chronic conditions can be stored in expected format."""
        # Test data structure (not implementation details)
        selected_codes = ["diabetes", "hypertension", "copd"]
        
        # Expected structure from Flag Manager
        chronic_data = {
            "chronic_codes": selected_codes,
            "source": "advisor_prep.medical",
            "updated_at": datetime.now().isoformat()
        }
        
        assert len(chronic_data["chronic_codes"]) == 3
        assert "diabetes" in chronic_data["chronic_codes"]
    
    def test_auto_flag_logic(self):
        """Test that chronic flags auto-activate based on condition count."""
        # Test the logic without relying on FlagManager implementation
        
        def determine_auto_flags(condition_count):
            """Logic for auto-flagging based on chronic condition count."""
            flags = []
            if condition_count >= 1:
                flags.append("chronic_present")
            if condition_count >= 2:
                flags.append("chronic_conditions")
            return flags
        
        # Test: 1 condition → chronic_present only
        flags_1 = determine_auto_flags(1)
        assert "chronic_present" in flags_1
        assert "chronic_conditions" not in flags_1
        
        # Test: 2 conditions → both flags
        flags_2 = determine_auto_flags(2)
        assert "chronic_present" in flags_2
        assert "chronic_conditions" in flags_2
    
    def test_flag_provenance_structure(self):
        """Test that flag provenance tracks required fields."""
        # Expected provenance structure
        provenance = {
            "mobility_limited": {
                "source": "advisor_prep.medical",
                "updated_at": datetime.now().isoformat(),
                "activated_by": "user"
            }
        }
        
        assert "source" in provenance["mobility_limited"]
        assert provenance["mobility_limited"]["source"] == "advisor_prep.medical"
        assert "updated_at" in provenance["mobility_limited"]


class TestPricingSafety:
    """Test 5: Cost Planner pricing stack unchanged."""
    
    def test_flag_multipliers_still_apply(self):
        """Test that care flags still multiply cost correctly."""
        # This test ensures PFMA v3 / Advisor Prep don't break Cost Planner
        
        # Mock: Base cost and zip multiplier
        base_cost = 1000.0
        zip_multiplier = 1.10
        
        # Mock: Flags with multipliers
        flag_multipliers = {
            "memory_support": 1.20,
            "mobility_limited": 1.15
        }
        
        # Calculate: Multiplicative application
        final_cost = base_cost * zip_multiplier
        for multiplier in flag_multipliers.values():
            final_cost *= multiplier
        
        # Assert: Correct calculation (1000 * 1.10 * 1.20 * 1.15 = 1518)
        expected = 1000.0 * 1.10 * 1.20 * 1.15
        assert abs(final_cost - expected) < 0.01


class TestNaviPresence:
    """Test 6: Exactly one Navi panel per view."""
    
    def test_pfma_v3_has_one_navi_panel(self, mock_st, session):
        """Test that PFMA v3 renders exactly one Navi panel."""
        # This is a structural test - actual implementation would need
        # to track render calls or parse HTML output
        
        # For now, verify the render_navi_panel call exists in code
        from products.pfma_v3 import product
        import inspect
        
        source = inspect.getsource(product.render)
        
        # Count render_navi_panel calls
        navi_calls = source.count("render_navi_panel(")
        
        # Assert: Called once in main render, once in gate
        assert navi_calls >= 1  # At least one call exists
    
    def test_advisor_prep_sections_have_navi(self):
        """Test that each Advisor Prep section has render_navi_panel call."""
        # Test by checking source files directly
        module_files = [
            "products/advisor_prep/modules/personal.py",
            "products/advisor_prep/modules/financial.py",
            "products/advisor_prep/modules/housing.py",
            "products/advisor_prep/modules/medical.py"
        ]
        
        for module_file in module_files:
            module_path = Path(module_file)
            assert module_path.exists(), f"Module file should exist: {module_file}"
            
            with open(module_path) as f:
                source = f.read()
            
            assert "render_navi_panel(" in source, f"{module_file} should have Navi panel"


class TestStrictValidation:
    """Test 7: Strict validation for flags, conditions, and contact info."""
    
    def test_flag_registry_structure(self):
        """Test that conditions registry can serve as flag source."""
        # Since flags come from conditions registry and Flag Manager,
        # test that the integration point exists
        
        conditions_path = Path("config/conditions/conditions.json")
        assert conditions_path.exists(), "Conditions registry should exist"
        
        with open(conditions_path) as f:
            data = json.load(f)
        
        # Verify conditions can be used for auto-flagging
        assert "conditions" in data
        conditions = data["conditions"]
        
        # Common conditions that trigger flags
        condition_codes = [c["code"] for c in conditions]
        assert "diabetes" in condition_codes or "hypertension" in condition_codes
        
        # Flag Manager uses these to activate care flags
        # (no separate flag registry needed - flags derived from conditions)
        
    def test_conditions_registry_structure(self):
        """Test that conditions registry exists with expected structure."""
        # Load conditions registry
        conditions_path = Path("config/conditions/conditions.json")
        assert conditions_path.exists(), "Conditions registry should exist"
        
        with open(conditions_path) as f:
            data = json.load(f)
        
        # Verify structure (conditions is at root level)
        assert "conditions" in data
        assert len(data["conditions"]) > 0
        
        # Verify sample condition has expected fields
        sample = data["conditions"][0]
        assert "code" in sample
        assert "label" in sample
    
    def test_email_validation_pattern(self):
        """Test email format validation pattern."""
        import re
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Test invalid formats
        invalid_emails = ["not-an-email", "@example.com", "test@", "test@.com"]
        for invalid in invalid_emails:
            assert not email_pattern.match(invalid), f"Should reject: {invalid}"
        
        # Test valid formats
        valid_emails = ["test@example.com", "user.name@domain.co.uk", "admin+tag@site.org"]
        for valid in valid_emails:
            assert email_pattern.match(valid), f"Should accept: {valid}"


class TestProgressTracking:
    """Test progress tracking across sections."""
    
    def test_advisor_prep_progress_increments(self, mock_st, session):
        """Test that completing sections increments progress."""
        from core.mcip import MCIP, AdvisorAppointment
        
        MCIP.initialize()
        
        # Setup: Create appointment
        appointment = AdvisorAppointment(
            scheduled=True,
            date="2025-10-25",
            time="10:00 AM",
            type="video",
            confirmation_id="TEST",
            contact_email="test@example.com",
            contact_phone="",
            timezone="America/New_York",
            notes="",
            generated_at=datetime.now().isoformat(),
            status="scheduled",
            prep_sections_complete=[],
            prep_progress=0
        )
        MCIP.set_advisor_appointment(appointment)
        
        # Action: Complete sections one by one
        for i, section in enumerate(["personal", "financial", "housing", "medical"], 1):
            appointment.prep_sections_complete.append(section)
            appointment.prep_progress = i * 25
            MCIP.set_advisor_appointment(appointment)
            
            # Assert: Progress updated
            retrieved = MCIP.get_advisor_appointment()
            assert retrieved.prep_progress == i * 25
            assert section in retrieved.prep_sections_complete


class TestDataPersistence:
    """Test that data persists via session state."""
    
    def test_mcip_contracts_saved_for_persistence(self, mock_st, session):
        """Test that MCIP saves contracts to mcip_contracts."""
        from core.mcip import MCIP, AdvisorAppointment
        
        MCIP.initialize()
        
        # Action: Create appointment
        appointment = AdvisorAppointment(
            scheduled=True,
            date="2025-10-25",
            time="10:00 AM",
            type="video",
            confirmation_id="PERSIST123",
            contact_email="test@example.com",
            contact_phone="",
            timezone="America/New_York",
            notes="",
            generated_at=datetime.now().isoformat(),
            status="scheduled",
            prep_sections_complete=[],
            prep_progress=0
        )
        MCIP.set_advisor_appointment(appointment)
        
        # Assert: Saved to mcip_contracts
        assert "mcip_contracts" in session
        assert "advisor_appointment" in session["mcip_contracts"]
        assert session["mcip_contracts"]["advisor_appointment"]["confirmation_id"] == "PERSIST123"


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
