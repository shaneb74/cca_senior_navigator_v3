"""
Unit tests for Flag Manager Service

Tests cover:
1. Activate valid flag
2. Re-activate same flag (idempotence)
3. Deactivate flag
4. Invalid flag error (strict mode)
5. Legacy normalization
6. Multiplicative pricing check
7. Chronic condition auto-flags
8. PFMA override precedence

Run with: pytest tests/test_flag_manager.py -v
"""

import json

# Mock streamlit before importing flag_manager
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

sys.modules["streamlit"] = type("MockStreamlit", (), {"session_state": {}})()

from core import flag_manager
from core.flags import COST_MODEL_FLAGS, FLAG_REGISTRY


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch DATA_DIR
        original_data_dir = flag_manager.DATA_DIR
        flag_manager.DATA_DIR = Path(tmpdir)

        yield Path(tmpdir)

        # Restore
        flag_manager.DATA_DIR = original_data_dir


@pytest.fixture
def mock_user_id():
    """Mock user ID for tests"""
    with patch.object(flag_manager, "_get_user_id", return_value="test_user"):
        yield "test_user"


@pytest.fixture
def clean_session(temp_data_dir, mock_user_id):
    """Provide clean session for each test"""
    session_file = temp_data_dir / f"{mock_user_id}.json"
    if session_file.exists():
        session_file.unlink()
    yield session_file


# ==============================================================================
# TEST 1: Activate Valid Flag
# ==============================================================================


def test_activate_valid_flag(clean_session, mock_user_id):
    """Test activating a valid flag creates proper structure"""
    # Activate flag
    flag_manager.activate("mobility_limited", "gcp")

    # Load session
    with open(clean_session) as f:
        session = json.load(f)

    # Verify structure
    assert "flags" in session
    assert "active" in session["flags"]
    assert "provenance" in session["flags"]

    # Verify flag in active list
    assert "mobility_limited" in session["flags"]["active"]

    # Verify provenance
    assert "mobility_limited" in session["flags"]["provenance"]
    prov = session["flags"]["provenance"]["mobility_limited"]
    assert prov["source"] == "gcp"
    assert "updated_at" in prov

    # Verify timestamp format (ISO 8601 with Z)
    timestamp = prov["updated_at"]
    assert timestamp.endswith("Z")
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))  # Should not raise


# ==============================================================================
# TEST 2: Re-activate Same Flag (Idempotence)
# ==============================================================================


def test_reactivate_updates_timestamp(clean_session, mock_user_id):
    """Test re-activating same flag updates timestamp but not duplicates"""
    import time

    # First activation
    flag_manager.activate("mobility_limited", "gcp")

    with open(clean_session) as f:
        session1 = json.load(f)
    timestamp1 = session1["flags"]["provenance"]["mobility_limited"]["updated_at"]

    # Small delay
    time.sleep(0.1)

    # Re-activate
    flag_manager.activate("mobility_limited", "gcp")

    with open(clean_session) as f:
        session2 = json.load(f)

    # Verify no duplicate in active list
    assert session2["flags"]["active"].count("mobility_limited") == 1

    # Verify timestamp updated
    timestamp2 = session2["flags"]["provenance"]["mobility_limited"]["updated_at"]
    assert timestamp2 >= timestamp1  # Should be same or newer


# ==============================================================================
# TEST 3: Deactivate Flag
# ==============================================================================


def test_deactivate_flag(clean_session, mock_user_id):
    """Test deactivating flag removes from active and provenance"""
    # Activate flag
    flag_manager.activate("mobility_limited", "gcp")
    flag_manager.activate("chronic_present", "gcp")

    # Verify both active
    active = flag_manager.get_active()
    assert "mobility_limited" in active
    assert "chronic_present" in active

    # Deactivate one
    flag_manager.deactivate("mobility_limited", "gcp")

    # Load session
    with open(clean_session) as f:
        session = json.load(f)

    # Verify removed from active
    assert "mobility_limited" not in session["flags"]["active"]
    assert "chronic_present" in session["flags"]["active"]

    # Verify removed from provenance (clean state)
    assert "mobility_limited" not in session["flags"]["provenance"]
    assert "chronic_present" in session["flags"]["provenance"]


# ==============================================================================
# TEST 4: Invalid Flag Error (Strict Mode)
# ==============================================================================


def test_invalid_flag_strict_mode(clean_session, mock_user_id):
    """Test invalid flag raises error in strict mode"""
    # Ensure strict mode
    original_mode = flag_manager.VALIDATION_MODE
    flag_manager.VALIDATION_MODE = "strict"

    try:
        # Attempt to activate invalid flag
        with pytest.raises(flag_manager.InvalidFlagError) as exc_info:
            flag_manager.activate("mobility_limit", "gcp")  # Missing 'ed'

        # Verify error message contains helpful info
        error_msg = str(exc_info.value)
        assert "mobility_limit" in error_msg
        assert "not found" in error_msg.lower()
        assert "FLAG_REGISTRY" in error_msg

        # Verify session was NOT created (error prevented write)
        assert not clean_session.exists()

    finally:
        flag_manager.VALIDATION_MODE = original_mode


# ==============================================================================
# TEST 5: Legacy Normalization
# ==============================================================================


def test_legacy_normalization(clean_session, mock_user_id):
    """Test legacy care_recommendation.flags converts to new structure"""
    # Create legacy session format
    legacy_session = {
        "mcip_contracts": {
            "care_recommendation": {
                "flags": [
                    {"id": "mobility_limited", "label": "..."},
                    {"id": "chronic_present", "label": "..."},
                ]
            }
        }
    }

    # Write legacy format
    with open(clean_session, "w") as f:
        json.dump(legacy_session, f)

    # Read flags via Flag Manager (should normalize)
    active = flag_manager.get_active()

    # Verify legacy flags accessible
    assert "mobility_limited" in active
    assert "chronic_present" in active

    # Verify provenance created
    prov = flag_manager.get_provenance("mobility_limited")
    assert prov is not None
    assert prov["source"] == "legacy_gcp"


# ==============================================================================
# TEST 6: Multiplicative Pricing Check
# ==============================================================================


def test_multiplicative_pricing(clean_session, mock_user_id):
    """Test cost multipliers apply correctly (multiplicative)"""
    # Activate two cost flags
    flag_manager.activate("mobility_limited", "gcp")  # 1.15x
    flag_manager.activate("chronic_conditions", "gcp")  # 1.10x

    # Get active cost flags
    active = flag_manager.get_active()
    cost_flags = [f for f in active if f in COST_MODEL_FLAGS]

    # Calculate multiplier
    total_multiplier = 1.0
    for flag_id in cost_flags:
        multiplier = FLAG_REGISTRY[flag_id].get("cost_multiplier", 1.0)
        total_multiplier *= multiplier

    # Verify multiplicative: 1.15 * 1.10 = 1.265
    expected = 1.15 * 1.10
    assert abs(total_multiplier - expected) < 0.001  # Float comparison

    # Test with base price
    base_price = 5000
    final_price = base_price * total_multiplier
    assert abs(final_price - 6325.0) < 0.01  # 5000 * 1.265 = 6325


# ==============================================================================
# TEST 7: Chronic Condition Auto-Flags
# ==============================================================================


def test_chronic_condition_auto_flags(clean_session, mock_user_id):
    """Test chronic condition count triggers correct flags"""
    # Test 0 conditions → no flags
    flag_manager.update_chronic_conditions([], "gcp")
    active = flag_manager.get_active()
    assert "chronic_present" not in active
    assert "chronic_conditions" not in active

    # Test 1 condition → chronic_present only
    flag_manager.update_chronic_conditions(["diabetes"], "gcp")
    active = flag_manager.get_active()
    assert "chronic_present" in active
    assert "chronic_conditions" not in active

    # Verify condition stored
    conditions = flag_manager.get_chronic_conditions()
    assert len(conditions) == 1
    assert conditions[0]["code"] == "diabetes"
    assert conditions[0]["source"] == "gcp"

    # Test 2 conditions → both flags
    flag_manager.update_chronic_conditions(["diabetes", "copd"], "gcp")
    active = flag_manager.get_active()
    assert "chronic_present" in active
    assert "chronic_conditions" in active

    # Verify conditions stored
    conditions = flag_manager.get_chronic_conditions()
    assert len(conditions) == 2
    codes = [c["code"] for c in conditions]
    assert "diabetes" in codes
    assert "copd" in codes

    # Test removing conditions (back to 1) → deactivates chronic_conditions
    flag_manager.update_chronic_conditions(["diabetes"], "gcp")
    active = flag_manager.get_active()
    assert "chronic_present" in active
    assert "chronic_conditions" not in active


# ==============================================================================
# TEST 8: PFMA Override Precedence (Last Writer Wins)
# ==============================================================================


def test_pfma_override_precedence(clean_session, mock_user_id):
    """Test PFMA edits supersede GCP via timestamp"""
    import time

    # GCP activates flag
    flag_manager.activate("mobility_limited", "gcp")

    prov1 = flag_manager.get_provenance("mobility_limited")
    assert prov1["source"] == "gcp"
    timestamp1 = prov1["updated_at"]

    # Small delay
    time.sleep(0.1)

    # PFMA re-activates (confirms)
    flag_manager.activate("mobility_limited", "pfma")

    prov2 = flag_manager.get_provenance("mobility_limited")
    assert prov2["source"] == "pfma"  # Source updated to PFMA
    timestamp2 = prov2["updated_at"]
    assert timestamp2 >= timestamp1  # Timestamp newer

    # Verify flag still active
    active = flag_manager.get_active()
    assert "mobility_limited" in active

    # Test PFMA deactivation
    flag_manager.deactivate("mobility_limited", "pfma")
    active = flag_manager.get_active()
    assert "mobility_limited" not in active  # PFMA deactivation wins


# ==============================================================================
# ADDITIONAL TESTS
# ==============================================================================


def test_get_all_provenance(clean_session, mock_user_id):
    """Test getting all provenance metadata"""
    flag_manager.activate("mobility_limited", "gcp")
    flag_manager.activate("chronic_present", "pfma")

    all_prov = flag_manager.get_all_provenance()

    assert "mobility_limited" in all_prov
    assert "chronic_present" in all_prov
    assert all_prov["mobility_limited"]["source"] == "gcp"
    assert all_prov["chronic_present"]["source"] == "pfma"


def test_validate_flags_multiple(clean_session, mock_user_id):
    """Test validating multiple flags at once"""
    # All valid
    invalid = flag_manager.validate_flags(["mobility_limited", "chronic_present"], "test")
    assert len(invalid) == 0

    # Some invalid (strict mode)
    original_mode = flag_manager.VALIDATION_MODE
    flag_manager.VALIDATION_MODE = "strict"

    try:
        with pytest.raises(flag_manager.InvalidFlagError):
            flag_manager.validate_flags(["mobility_limited", "invalid_flag"], "test")
    finally:
        flag_manager.VALIDATION_MODE = original_mode


def test_condition_validation(clean_session, mock_user_id):
    """Test condition code validation"""
    # Valid codes
    invalid = flag_manager.validate_condition_codes(["diabetes", "copd"], "test")
    assert len(invalid) == 0

    # Invalid code (strict mode)
    original_mode = flag_manager.VALIDATION_MODE
    flag_manager.VALIDATION_MODE = "strict"

    try:
        with pytest.raises(flag_manager.InvalidConditionError):
            flag_manager.validate_condition_codes(["diabetes", "invalid_disease"], "test")
    finally:
        flag_manager.VALIDATION_MODE = original_mode


def test_conditions_registry_load():
    """Test conditions registry loads correctly"""
    registry = flag_manager.get_conditions_registry()

    assert "version" in registry
    assert "conditions" in registry
    assert len(registry["conditions"]) >= 15  # Should have at least 15 conditions

    # Check structure of first condition
    first_cond = registry["conditions"][0]
    assert "code" in first_cond
    assert "label" in first_cond
    assert "category" in first_cond
    assert "common" in first_cond


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
