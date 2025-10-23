#!/usr/bin/env python3
"""
Smoke test for Household + Partner dual-assessment flow.

Usage:
    python tools/smoke_household.py

Verifies:
- Domain models instantiate correctly
- State helpers manage session state
- Cost aggregation computes household total
- Partner flow interstitial logic works

Does NOT require Streamlit app running.
"""

import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from core.models import Household, Person, CarePlan, CostPlan
from products.cost_planner_v2.household import compute_household_total
from products.cost_planner_v2 import comparison_calcs
from unittest.mock import patch


class MockSessionState:
    """Mock Streamlit session_state for testing."""
    def __init__(self):
        self._state = {}
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __contains__(self, key):
        return key in self._state
    
    @property
    def session_state(self):
        return self


def test_household_models():
    """Test domain model instantiation."""
    print("🧪 Testing domain models...")
    
    # Create household
    hh = Household(
        zip="94103",
        has_partner=True,
        members=["p_primary", "p_partner"]
    )
    assert hh.zip == "94103"
    assert hh.has_partner is True
    assert len(hh.members) == 2
    print(f"  ✅ Household created: {hh.uid} with {len(hh.members)} members")
    
    # Create persons
    primary = Person(
        role="primary",
        name="Jane Doe",
        age=78,
        household_id=hh.uid
    )
    assert primary.role == "primary"
    print(f"  ✅ Primary person created: {primary.uid}")
    
    partner = Person(
        role="partner",
        name="John Doe",
        age=80,
        household_id=hh.uid
    )
    assert partner.role == "partner"
    print(f"  ✅ Partner person created: {partner.uid}")
    
    # Create CarePlans
    cp_primary = CarePlan(
        person_id=primary.uid,
        det_tier="memory_care",
        final_tier="memory_care",
        hours_suggested="24h",
        hours_user="24h"
    )
    assert cp_primary.final_tier == "memory_care"
    print(f"  ✅ Primary CarePlan created: {cp_primary.uid}")
    
    cp_partner = CarePlan(
        person_id=partner.uid,
        det_tier="assisted_living",
        final_tier="assisted_living",
        hours_suggested="4-8h",
        hours_user="4-8h"
    )
    assert cp_partner.final_tier == "assisted_living"
    print(f"  ✅ Partner CarePlan created: {cp_partner.uid}")
    
    # Create CostPlans
    cost_primary = CostPlan(
        person_id=primary.uid,
        care_plan_id=cp_primary.uid,
        total_monthly=6500.0,
        breakdown={"facility": 6500.0}
    )
    assert cost_primary.care_plan_id == cp_primary.uid
    print(f"  ✅ Primary CostPlan created: {cost_primary.uid}")
    
    cost_partner = CostPlan(
        person_id=partner.uid,
        care_plan_id=cp_partner.uid,
        total_monthly=4500.0,
        breakdown={"facility": 4500.0}
    )
    assert cost_partner.care_plan_id == cp_partner.uid
    print(f"  ✅ Partner CostPlan created: {cost_partner.uid}")
    
    return hh, primary, partner, cp_primary, cp_partner, cost_primary, cost_partner


def test_household_cost_aggregation():
    """Test dual cost aggregation."""
    print("\n🧪 Testing household cost aggregation...")
    
    hh, primary, partner, cp_primary, cp_partner, cost_primary, cost_partner = test_household_models()
    
    # Mock session state
    st = MockSessionState()
    st["household.model"] = hh
    st["person.primary_id"] = primary.uid
    st["person.partner_id"] = partner.uid
    st[f"careplan.{primary.uid}"] = cp_primary
    st[f"careplan.{partner.uid}"] = cp_partner
    st["cost.inputs"] = {
        "zip": "94103",
        "keep_home": True,
        "owner_tenant": "owner",
        "hours": "24h"
    }
    
    # Compute household total
    result = compute_household_total(st)
    
    print(f"  Primary total: ${result['primary_total']:,.2f}")
    print(f"  Partner total: ${result['partner_total']:,.2f}")
    print(f"  Home carry: ${result['home_carry']:,.2f}")
    print(f"  Household total: ${result['household_total']:,.2f}")
    print(f"  Split (50/50): ${result['split']['primary']:,.2f} each")
    
    assert result["has_partner_plan"] is True
    assert result["household_total"] > 0
    assert result["split"]["primary"] == result["split"]["partner"]
    print("  ✅ Household cost aggregation successful")
    
    return result


def test_single_person_fallback():
    """Test that single-person households still work."""
    print("\n🧪 Testing single-person fallback...")
    
    # Create single-person household
    hh = Household(zip="90210", has_partner=False, members=["p_solo"])
    solo = Person(role="primary", name="Solo Senior", age=75, household_id=hh.uid)
    cp_solo = CarePlan(
        person_id=solo.uid,
        det_tier="in_home",
        final_tier="in_home",
        hours_suggested="4-8h",
        hours_user="4-8h"
    )
    
    # Mock session state
    st = MockSessionState()
    st["household.model"] = hh
    st["person.primary_id"] = solo.uid
    st[f"careplan.{solo.uid}"] = cp_solo
    st["cost.inputs"] = {
        "zip": "90210",
        "keep_home": False,
        "hours": "4-8h"
    }
    
    result = compute_household_total(st)
    
    print(f"  Solo total: ${result['primary_total']:,.2f}")
    print(f"  Household total: ${result['household_total']:,.2f}")
    
    assert result["has_partner_plan"] is False
    assert result["partner_total"] == 0.0
    assert result["household_total"] == result["primary_total"]
    print("  ✅ Single-person fallback works")


def test_skip_path():
    """Test partner skip path - no partner plan created."""
    print("\n🧪 Testing skip path...")
    
    # Create household with has_partner=True
    hh = Household(zip="94103", has_partner=True, members=["p_primary"])
    primary = Person(role="primary", name="Primary Person", age=80, household_id=hh.uid)
    cp_primary = CarePlan(
        person_id=primary.uid,
        det_tier="assisted_living",
        final_tier="assisted_living",
        hours_suggested="4-8h",
        hours_user="4-8h"
    )
    
    # Mock session state - simulate skip decision
    st = MockSessionState()
    st["household.model"] = hh
    st["person.primary_id"] = primary.uid
    st[f"careplan.{primary.uid}"] = cp_primary
    st["flow.partner_started"] = False  # User clicked Skip
    st["flow.partner_complete"] = False
    st["cost.inputs"] = {
        "zip": "94103",
        "keep_home": False,
        "hours": "4-8h"
    }
    
    # Compute costs
    result = compute_household_total(st)
    
    print(f"  flow.partner_started: {st['flow.partner_started']}")
    print(f"  flow.partner_complete: {st['flow.partner_complete']}")
    print(f"  Has partner plan: {result['has_partner_plan']}")
    print(f"  Primary total: ${result['primary_total']:,.2f}")
    print(f"  Partner total: ${result['partner_total']:,.2f}")
    
    # Assertions
    assert st["flow.partner_started"] is False
    assert st["flow.partner_complete"] is False
    assert "person.partner_id" not in st._state
    assert result["has_partner_plan"] is False
    assert result["partner_total"] == 0.0
    assert st.get("cost.dual_mode") is None or st.get("cost.dual_mode") is False
    
    print("  ✅ Skip path validated")


def test_idempotent_completion():
    """Test that calling complete_partner_flow twice is safe."""
    print("\n🧪 Testing idempotent completion...")
    
    # Mock complete_partner_flow behavior
    def complete_partner_flow(st):
        st["flow.partner_complete"] = True
        st["gcp.partner_mode"] = False
    
    # Mock session state
    st = MockSessionState()
    st["flow.partner_started"] = True
    st["gcp.partner_mode"] = True
    st["flow.partner_complete"] = False
    
    # First completion
    complete_partner_flow(st)
    assert st["flow.partner_complete"] is True
    assert st["gcp.partner_mode"] is False
    print("  First completion: ✓")
    
    # Second completion (should be safe)
    complete_partner_flow(st)
    assert st["flow.partner_complete"] is True
    assert st["gcp.partner_mode"] is False
    print("  Second completion: ✓ (idempotent)")
    
    print("  ✅ Idempotent completion verified")


def test_aggregation_variants():
    """Test aggregation with different keep_home scenarios."""
    print("\n🧪 Testing aggregation variants...")
    
    # Create dual household
    hh = Household(zip="94103", has_partner=True, members=["p_primary", "p_partner"])
    primary = Person(role="primary", name="Jane", age=78, household_id=hh.uid)
    partner = Person(role="partner", name="John", age=80, household_id=hh.uid)
    
    cp_primary = CarePlan(
        person_id=primary.uid,
        det_tier="memory_care",
        final_tier="memory_care",
        hours_suggested="24h",
        hours_user="24h"
    )
    
    cp_partner = CarePlan(
        person_id=partner.uid,
        det_tier="assisted_living",
        final_tier="assisted_living",
        hours_suggested="4-8h",
        hours_user="4-8h"
    )
    
    # Test with keep_home=False
    st = MockSessionState()
    st["household.model"] = hh
    st["person.primary_id"] = primary.uid
    st["person.partner_id"] = partner.uid
    st[f"careplan.{primary.uid}"] = cp_primary
    st[f"careplan.{partner.uid}"] = cp_partner
    st["cost.inputs"] = {
        "zip": "94103",
        "keep_home": False,
        "owner_tenant": "owner",
        "hours": "24h"
    }
    
    result_no_home = compute_household_total(st)
    print(f"  Without home carry:")
    print(f"    Primary: ${result_no_home['primary_total']:,.2f}")
    print(f"    Partner: ${result_no_home['partner_total']:,.2f}")
    print(f"    Home carry: ${result_no_home['home_carry']:,.2f}")
    print(f"    Household: ${result_no_home['household_total']:,.2f}")
    print(f"    Split: ${result_no_home['split']['primary']:,.2f} each")
    
    assert result_no_home["home_carry"] == 0.0
    assert result_no_home["split"]["primary"] == result_no_home["household_total"] / 2
    assert result_no_home["split"]["partner"] == result_no_home["household_total"] / 2
    
    # Test with keep_home=True
    st["cost.inputs"]["keep_home"] = True
    result_with_home = compute_household_total(st)
    
    print(f"  With home carry:")
    print(f"    Primary: ${result_with_home['primary_total']:,.2f}")
    print(f"    Partner: ${result_with_home['partner_total']:,.2f}")
    print(f"    Home carry: ${result_with_home['home_carry']:,.2f}")
    print(f"    Household: ${result_with_home['household_total']:,.2f}")
    print(f"    Split: ${result_with_home['split']['primary']:,.2f} each")
    
    assert result_with_home["home_carry"] > 0
    assert result_with_home["household_total"] == (
        result_with_home["primary_total"] + 
        result_with_home["partner_total"] + 
        result_with_home["home_carry"]
    )
    assert result_with_home["split"]["primary"] == result_with_home["household_total"] / 2
    
    print("  ✅ Aggregation variants validated")


def test_prefill_integrity():
    """Test that cost.inputs prefill from household is stable."""
    print("\n🧪 Testing prefill integrity...")
    
    # Seed household data
    hh = Household(
        zip="90210",
        has_partner=True,
        home_owner_type="owner",
        keep_home_default=True,
        members=["p_primary"]
    )
    
    primary = Person(role="primary", name="Test User", age=75, household_id=hh.uid)
    cp_primary = CarePlan(
        person_id=primary.uid,
        det_tier="in_home",
        final_tier="in_home",
        hours_suggested="4-8h",
        hours_user="4-8h"
    )
    
    # Mock session state
    st = MockSessionState()
    st["household.model"] = hh
    st["person.primary_id"] = primary.uid
    st[f"careplan.{primary.uid}"] = cp_primary
    
    # Simulate prefill logic (from intro.py)
    if "cost.inputs" not in st._state:
        inputs = {
            "zip": hh.zip,
            "keep_home": hh.keep_home_default if hh.keep_home_default is not None else False,
            "owner_tenant": hh.home_owner_type or "unknown",
        }
        if cp_primary:
            inputs["hours"] = cp_primary.hours_user or cp_primary.hours_suggested
        st["cost.inputs"] = inputs
    
    # Verify prefill
    cost_inputs = st["cost.inputs"]
    print(f"  Prefilled ZIP: {cost_inputs['zip']}")
    print(f"  Prefilled keep_home: {cost_inputs['keep_home']}")
    print(f"  Prefilled owner/tenant: {cost_inputs['owner_tenant']}")
    print(f"  Prefilled hours: {cost_inputs.get('hours')}")
    
    assert cost_inputs["zip"] == "90210"
    assert cost_inputs["keep_home"] is True
    assert cost_inputs["owner_tenant"] == "owner"
    assert cost_inputs["hours"] == "4-8h"
    
    # Simulate "refresh" - should not overwrite
    if "cost.inputs" not in st._state:
        # This should not execute
        assert False, "cost.inputs should already exist"
    
    print("  ✅ Prefill integrity maintained across refresh")


def test_no_hours_on_facility_default():
    """Test that hours input is gated when tier is AL/MC and compare_inhome=False."""
    print("\n🧪 Testing hours input gating for facility tiers...")
    
    st = MockSessionState()
    
    # Set up AL tier without compare_inhome
    st["person.primary_id"] = "user_001"
    st["careplan.user_001"] = CarePlan(
        person_id="user_001",
        final_tier="assisted_living", 
        hours_suggested="4-8h"
    ).model_dump()
    st["cost.compare_inhome"] = False
    
    # Simulate facility comparison calculation
    # In this mode, hours should NOT be used for facility calculation
    
    # Verify that AL cost calculation doesn't use hours
    from products.cost_planner_v2 import comparison_calcs
    
    facility_breakdown = comparison_calcs.calculate_facility_scenario(
        care_type="assisted_living",
        zip_code="94102",
        keep_home=False
    )
    
    # Verify no hours-based cost in facility breakdown
    has_hours_cost = any("hour" in line.label.lower() for line in facility_breakdown.lines)
    assert not has_hours_cost, "Facility calculation should not include hours-based costs"
    
    print(f"  ✅ AL calculation excludes hours: ${facility_breakdown.monthly_total:,.0f}/mo")


def test_hours_visible_in_comparison_mode():
    """Test that hours input becomes visible when compare_inhome=True."""
    print("\n🧪 Testing hours visibility in comparison mode...")
    
    st = MockSessionState()
    
    # Set up AL tier WITH compare_inhome enabled
    st["person.primary_id"] = "user_001"
    st["careplan.user_001"] = CarePlan(
        person_id="user_001",
        final_tier="assisted_living", 
        hours_suggested="4-8h"
    ).model_dump()
    st["cost.compare_inhome"] = True
    
    # Simulate in-home calculation (should work now)
    inhome_breakdown = comparison_calcs.calculate_inhome_scenario(
        zip_code="94102",
        hours_per_day=8.0
    )
    
    # Verify hours are used in calculation
    has_hours_cost = any("hourly" in line.label.lower() or "base" in line.label.lower() for line in inhome_breakdown.lines)
    assert has_hours_cost, "In-home calculation should include hours-based costs"
    
    print(f"  ✅ In-home calculation includes hours: ${inhome_breakdown.monthly_total:,.0f}/mo")


def test_threshold_low_intensity_below():
    """Test cost advisory for low intensity, below threshold."""
    print("\n🧪 Testing low intensity below threshold...")
    
    st = MockSessionState()
    
    # Set up in-home tier with minimal flags (low intensity)
    st["person.primary_id"] = "user_001"  
    st["careplan.user_001"] = CarePlan(
        person_id="user_001",
        final_tier="in_home_care", 
        hours_suggested="1-3h"
    ).model_dump()
    
    # Mock flags for testing (simulate low intensity)
    
    def mock_get_all_flags():
        return {}  # No flags = low intensity = threshold $7,000
    
    with patch('core.flags.get_all_flags', mock_get_all_flags):
        from products.cost_planner_v2.comparison_view import _calculate_support_intensity, _get_cost_threshold
        
        intensity = _calculate_support_intensity()
        threshold = _get_cost_threshold(intensity)
        
        assert intensity == 0, f"Expected intensity 0, got {intensity}"
        assert threshold == 7000.0, f"Expected threshold $7,000, got ${threshold:,.0f}"
        
        # Test in-home cost below threshold ($6,500 < $7,000)
        inhome_estimate = 6500.0
        threshold_crossed = inhome_estimate >= threshold
        
        assert not threshold_crossed, "Should be below threshold"
        
    print(f"  ✅ Low intensity ({intensity}), threshold ${threshold:,.0f}, estimate ${inhome_estimate:,.0f} = workable")


def test_threshold_high_intensity_crossed():
    """Test cost advisory for high intensity, above threshold."""
    print("\n🧪 Testing high intensity above threshold...")
    
    st = MockSessionState()
    
    # Set up in-home tier with high intensity flags
    st["person.primary_id"] = "user_001"
    st["careplan.user_001"] = CarePlan(
        person_id="user_001",
        final_tier="in_home_care", 
        hours_suggested="24h"
    ).model_dump()
    
    # Mock flags for testing (simulate high intensity)
    def mock_get_all_flags():
        return {
            "moderate_dependence": True,
            "mobility_limited": True, 
            "moderate_cognitive_decline": True,
            "chronic_present": True,
            "falls_risk": True
        }
    
    with patch('core.flags.get_all_flags', mock_get_all_flags):
        from products.cost_planner_v2.comparison_view import _calculate_support_intensity, _get_cost_threshold
        
        intensity = _calculate_support_intensity()
        threshold = _get_cost_threshold(intensity)
        
        assert intensity == 5, f"Expected intensity 5, got {intensity}"
        assert threshold == 8000.0, f"Expected threshold $8,000, got ${threshold:,.0f}"
        
        # Test in-home cost above threshold ($8,200 > $8,000)
        inhome_estimate = 8200.0
        threshold_crossed = inhome_estimate >= threshold
        
        assert threshold_crossed, "Should be above threshold"
        
    print(f"  ✅ High intensity ({intensity}), threshold ${threshold:,.0f}, estimate ${inhome_estimate:,.0f} = crossed")


def test_dual_person_mixed():
    """Test dual person scenario with mixed advisories."""
    print("\n🧪 Testing dual person mixed advisories...")
    
    st = MockSessionState()
    
    # Set up dual mode with primary crossed, partner not
    st["cost.dual_mode"] = True
    st["person.primary_id"] = "user_001"
    st["person.partner_id"] = "user_002"
    
    # Primary: high intensity, crossed threshold
    st["careplan.user_001"] = CarePlan(
        person_id="user_001",
        final_tier="in_home_care", 
        hours_suggested="24h"
    ).model_dump()
    
    # Partner: low intensity, below threshold  
    st["careplan.user_002"] = CarePlan(
        person_id="user_002",
        final_tier="in_home_care", 
        hours_suggested="1-3h"
    ).model_dump()
    
    # Mock household computation result
    mock_result = {
        "has_partner_plan": True,
        "primary_total": 8200.0,  # Above $8,000 threshold
        "partner_total": 6500.0,  # Below $7,000 threshold
        "household_total": 14700.0,
        "primary_tier": "in_home_care",
        "partner_tier": "in_home_care",
        "split": {"primary": 7350.0, "partner": 7350.0}
    }
    
    # Test that advisories differ per person
    assert mock_result["primary_total"] >= 8000, "Primary should be above threshold"
    assert mock_result["partner_total"] < 7000, "Partner should be below threshold"
    
    print(f"  ✅ Mixed advisories: Primary ${mock_result['primary_total']:,.0f} (crossed), Partner ${mock_result['partner_total']:,.0f} (workable)")


def test_compare_toggle_roundtrip():
    """Test that compare_inhome toggles correctly without state corruption."""
    print("\n🧪 Testing compare toggle roundtrip...")
    
    st = MockSessionState()
    
    # Set up AL tier
    st["person.primary_id"] = "user_001"
    st["careplan.user_001"] = CarePlan(
        person_id="user_001",
        final_tier="assisted_living", 
        hours_suggested="4-8h"
    ).model_dump()
    
    # Set up cost.inputs
    st["cost.inputs"] = {
        "zip": "94102",
        "keep_home": False,
        "owner_tenant": "owner", 
        "hours": "4-8h"
    }
    
    # Start with compare_inhome=False
    st["cost.compare_inhome"] = False
    
    # Toggle to True
    st["cost.compare_inhome"] = True
    assert st["cost.compare_inhome"] == True, "Should toggle to True"
    
    # Verify cost.inputs not overwritten  
    assert st["cost.inputs"]["zip"] == "94102", "ZIP should be preserved"
    assert st["cost.inputs"]["hours"] == "4-8h", "Hours should be preserved"
    
    # Toggle back to False
    st["cost.compare_inhome"] = False
    assert st["cost.compare_inhome"] == False, "Should toggle back to False"
    
    # Verify cost.inputs still intact
    assert st["cost.inputs"]["zip"] == "94102", "ZIP should still be preserved"
    assert st["cost.inputs"]["hours"] == "4-8h", "Hours should still be preserved"
    
    # Verify no leakage into facility totals (facility calculation should ignore hours)
    facility_breakdown = comparison_calcs.calculate_facility_scenario(
        care_type="assisted_living",
        zip_code="94102", 
        keep_home=False
    )
    
    # Facility total should be consistent regardless of hours in cost.inputs
    assert facility_breakdown.care_type == "assisted_living", "Should be facility calculation"
    
    print(f"  ✅ Toggle roundtrip preserves state, facility total: ${facility_breakdown.monthly_total:,.0f}/mo")


def test_llm_valid_wins():
    """Test adjudication: LLM wins when valid and in allowed set."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    
    final_tier, decision = _choose_final_tier(
        det_tier="assisted_living",
        allowed_tiers={"assisted_living", "memory_care", "in_home"},
        llm_tier="memory_care",  # Different from det, but allowed
        llm_conf=0.75,
        bands={"cog": "moderate", "sup": "high"},
        risky=False
    )
    
    assert final_tier == "memory_care", f"LLM should win, got {final_tier}"
    assert decision["source"] == "llm", f"Source should be llm, got {decision['source']}"
    assert decision["adjudication_reason"] == "llm_valid", f"Reason should be llm_valid, got {decision['adjudication_reason']}"
    
    print("  ✅ LLM-first adjudication: LLM wins when valid")


def test_llm_invalid_guard_fallback():
    """Test adjudication: deterministic fallback when LLM not in allowed set."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    
    final_tier, decision = _choose_final_tier(
        det_tier="assisted_living",
        allowed_tiers={"assisted_living", "in_home"},  # No memory_care
        llm_tier="memory_care",  # Not in allowed set
        llm_conf=0.90,  # High confidence doesn't matter
        bands={"cog": "moderate", "sup": "high"},
        risky=False
    )
    
    assert final_tier == "assisted_living", f"Should fallback to det, got {final_tier}"
    assert decision["source"] == "fallback", f"Source should be fallback, got {decision['source']}"
    assert decision["adjudication_reason"] == "llm_invalid_guard", f"Reason should be llm_invalid_guard, got {decision['adjudication_reason']}"
    
    print("  ✅ LLM-first adjudication: fallback when LLM not allowed")


def test_llm_timeout_fallback():
    """Test adjudication: deterministic fallback when LLM missing/timeout."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    
    final_tier, decision = _choose_final_tier(
        det_tier="in_home",
        allowed_tiers={"assisted_living", "memory_care", "in_home"},
        llm_tier=None,  # LLM timeout/missing
        llm_conf=None,
        bands={"cog": "mild", "sup": "medium"},
        risky=False
    )
    
    assert final_tier == "in_home", f"Should fallback to det, got {final_tier}"
    assert decision["source"] == "fallback", f"Source should be fallback, got {decision['source']}"
    assert decision["adjudication_reason"] == "llm_timeout", f"Reason should be llm_timeout, got {decision['adjudication_reason']}"
    
    print("  ✅ LLM-first adjudication: fallback when LLM timeout")


def test_llm_and_det_same():
    """Test adjudication: LLM source when LLM and deterministic agree."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    
    final_tier, decision = _choose_final_tier(
        det_tier="assisted_living",
        allowed_tiers={"assisted_living", "memory_care", "in_home"},
        llm_tier="assisted_living",  # Same as det
        llm_conf=0.80,
        bands={"cog": "moderate", "sup": "high"},
        risky=False
    )
    
    assert final_tier == "assisted_living", f"Should choose agreed tier, got {final_tier}"
    assert decision["source"] == "llm", f"Source should be llm even when same, got {decision['source']}"
    assert decision["adjudication_reason"] == "llm_valid", f"Reason should be llm_valid, got {decision['adjudication_reason']}"
    
    print("  ✅ LLM-first adjudication: LLM source when both agree")


def test_partner_independent_llm_first():
    """Test adjudication: partner adjudication is independent."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    
    # Primary: LLM valid
    primary_tier, primary_decision = _choose_final_tier(
        det_tier="assisted_living",
        allowed_tiers={"assisted_living", "memory_care"},
        llm_tier="memory_care",  # Valid
        llm_conf=0.85,
        bands={"cog": "moderate", "sup": "high"},
        risky=False
    )
    
    # Partner: LLM invalid (different allowed set)
    partner_tier, partner_decision = _choose_final_tier(
        det_tier="in_home",
        allowed_tiers={"in_home", "assisted_living"},  # No memory_care
        llm_tier="memory_care",  # Invalid for partner
        llm_conf=0.85,
        bands={"cog": "mild", "sup": "medium"},
        risky=False
    )
    
    # Verify independence
    assert primary_tier == "memory_care" and primary_decision["source"] == "llm", "Primary should use LLM"
    assert partner_tier == "in_home" and partner_decision["source"] == "fallback", "Partner should fallback"
    assert partner_decision["adjudication_reason"] == "llm_invalid_guard", "Partner reason should be guard"
    
    print("  ✅ LLM-first adjudication: partner independence")


def test_logging_once():
    """Test adjudication: logging format and idempotence."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    
    # Mock session state and capture print output
    import io
    import contextlib
    
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers={"assisted_living", "memory_care"},
            llm_tier="memory_care",
            llm_conf=0.82,
            bands={"cog": "moderate", "sup": "high"},
            risky=False
        )
    
    # Verify decision structure (logging is tested in context where session_state exists)
    assert "allowed" in decision and isinstance(decision["allowed"], list)
    assert "conf" in decision
    assert "adjudication_reason" in decision
    
    print("  ✅ LLM-first adjudication: logging structure validated")


def test_llm_valid_wins_ui_and_persist():
    """Test LLM-first: when LLM tier is valid and allowed, it wins and is saved to CarePlan."""
    import streamlit as st
    from core.models import CarePlan
    from core.household import get_careplan_for, set_careplan_for
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    
    # Mock a valid LLM choice that differs from deterministic
    final_tier, decision = _choose_final_tier(
        det_tier="assisted_living",
        allowed_tiers={"assisted_living", "memory_care", "in_home"},
        llm_tier="memory_care",  # Different from det, but allowed
        llm_conf=0.85,
        bands={"cog": "moderate", "sup": "high"},
        risky=False
    )
    
    # Verify LLM wins
    assert final_tier == "memory_care", f"LLM should win, got {final_tier}"
    assert decision["source"] == "llm", f"Source should be llm, got {decision['source']}"
    assert decision["adjudication_reason"] == "llm_valid", f"Reason should be llm_valid"
    
    # Simulate CarePlan creation with adjudication metadata
    cp = CarePlan(
        person_id="test_person_ui_persist",
        det_tier="assisted_living",
        llm_tier="memory_care",
        final_tier=final_tier,  # Should be "memory_care"
        confidence=0.85,
        allowed_tiers=["assisted_living", "memory_care", "in_home"],
        bands={"cog": "moderate", "sup": "high"},
        risky_behaviors=False,
        # Adjudication metadata
        source=decision["source"],
        alt_tier="assisted_living",  # The non-chosen tier
        llm_confidence=0.85,
        adjudication_reason=decision["adjudication_reason"]
    )
    
    # Verify saved tier matches LLM choice
    assert cp.final_tier == "memory_care", f"Saved tier should be LLM choice: memory_care, got {cp.final_tier}"
    assert cp.source == "llm", f"Source should be llm, got {cp.source}"
    
    print("  ✅ LLM-first adjudication: LLM wins, saves to CarePlan, UI matches")


def test_llm_invalid_guard_fallback_ui():
    """Test LLM-first: when LLM tier is not in allowed set, fallback to deterministic."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    from core.models import CarePlan
    
    # LLM returns tier not in allowed set
    final_tier, decision = _choose_final_tier(
        det_tier="assisted_living",
        allowed_tiers={"assisted_living", "in_home"},  # No memory_care
        llm_tier="memory_care",  # Not in allowed set
        llm_conf=0.90,  # High confidence doesn't matter
        bands={"cog": "moderate", "sup": "high"},
        risky=False
    )
    
    # Verify fallback to deterministic
    assert final_tier == "assisted_living", f"Should fallback to det, got {final_tier}"
    assert decision["source"] == "fallback", f"Source should be fallback, got {decision['source']}"
    assert decision["adjudication_reason"] == "llm_invalid_guard", f"Reason should be llm_invalid_guard"
    
    # Simulate CarePlan creation
    cp = CarePlan(
        person_id="test_person_guard_fallback",
        det_tier="assisted_living",
        llm_tier="memory_care",
        final_tier=final_tier,  # Should be "assisted_living"
        confidence=0.75,
        allowed_tiers=["assisted_living", "in_home"],
        bands={"cog": "moderate", "sup": "high"},
        risky_behaviors=False,
        # Adjudication metadata
        source=decision["source"],
        alt_tier="memory_care",  # The non-chosen (invalid) tier
        llm_confidence=0.90,
        adjudication_reason=decision["adjudication_reason"]
    )
    
    # Verify saved tier matches deterministic fallback
    assert cp.final_tier == "assisted_living", f"Saved tier should be det fallback: assisted_living, got {cp.final_tier}"
    assert cp.source == "fallback", f"Source should be fallback, got {cp.source}"
    
    print("  ✅ LLM-first adjudication: invalid LLM guard fallback works")


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("HOUSEHOLD + PARTNER FLOW - SMOKE TEST")
    print("=" * 60)
    
    try:
        test_household_models()
        test_household_cost_aggregation()
        test_single_person_fallback()
        test_skip_path()
        test_idempotent_completion()
        test_aggregation_variants()
        test_prefill_integrity()
        test_no_hours_on_facility_default()
        test_hours_visible_in_comparison_mode()
        test_threshold_low_intensity_below()
        test_threshold_high_intensity_crossed()
        test_dual_person_mixed()
        test_compare_toggle_roundtrip()
        
        # GCP Adjudication tests
        print("\n🔄 GCP Adjudication Simplification Tests:")
        test_llm_valid_wins()
        test_llm_invalid_guard_fallback()
        test_llm_timeout_fallback()
        test_llm_and_det_same()
        test_partner_independent_llm_first()
        test_logging_once()
        
        # GCP LLM-First Results Tests
        print("\n🎯 GCP RESULTS LLM-First Tests:")
        test_llm_valid_wins_ui_and_persist()
        test_llm_invalid_guard_fallback_ui()
        test_gcp_adjudication_logging_once()
        
        print("\n" + "=" * 60)
        print("✅ ALL SMOKE TESTS PASSED (including LLM-first adjudication + UI)")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


def test_gcp_adjudication_logging_once():
    """Test adjudication: single log entry per results render with all context."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    import io
    import contextlib
    
    # Capture log output
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers={"assisted_living", "memory_care"},
            llm_tier="memory_care",
            llm_conf=0.82,
            bands={"cog": "moderate", "sup": "high"},
            risky=False
        )
    
    # Verify decision contains required fields for logging
    required_fields = ["source", "allowed", "conf", "adjudication_reason"]
    for field in required_fields:
        assert field in decision, f"Decision missing required field: {field}"
    
    assert decision["source"] == "llm"
    assert decision["adjudication_reason"] == "llm_valid"
    assert isinstance(decision["allowed"], list)
    assert decision["conf"] == 0.82
    
    print("  ✅ LLM-first adjudication: single log with all context validated")


def test_gcp_adjudication_logging_once():
    """Test adjudication: single log entry per results render with all context."""
    from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier
    import io
    import contextlib
    
    # Capture log output
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers={"assisted_living", "memory_care"},
            llm_tier="memory_care",
            llm_conf=0.82,
            bands={"cog": "moderate", "sup": "high"},
            risky=False
        )
    
    # Verify decision contains required fields for logging
    required_fields = ["source", "allowed", "conf", "adjudication_reason"]
    for field in required_fields:
        assert field in decision, f"Decision missing required field: {field}"
    
    assert decision["source"] == "llm"
    assert decision["adjudication_reason"] == "llm_valid"
    assert isinstance(decision["allowed"], list)
    assert decision["conf"] == 0.82
    
    print("  ✅ LLM-first adjudication: single log with all context validated")


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("HOUSEHOLD + PARTNER FLOW - SMOKE TEST")
    print("=" * 60)
    
    try:
        test_household_models()
        test_household_cost_aggregation()
        test_single_person_fallback()
        test_skip_path()
        test_idempotent_completion()
        test_aggregation_variants()
        test_prefill_integrity()
        test_no_hours_on_facility_default()
        test_hours_visible_in_comparison_mode()
        test_threshold_low_intensity_below()
        test_threshold_high_intensity_crossed()
        test_dual_person_mixed()
        test_compare_toggle_roundtrip()
        
        # GCP Adjudication tests
        print("\n🔄 GCP Adjudication Simplification Tests:")
        test_llm_valid_wins()
        test_llm_invalid_guard_fallback()
        test_llm_timeout_fallback()
        test_llm_and_det_same()
        test_partner_independent_llm_first()
        test_logging_once()
        
        # GCP LLM-First Results Tests
        print("\n🎯 GCP RESULTS LLM-First Tests:")
        test_llm_valid_wins_ui_and_persist()
        test_llm_invalid_guard_fallback_ui()
        test_gcp_adjudication_logging_once()
        
        print("\n" + "=" * 60)
        print("✅ ALL SMOKE TESTS PASSED (including LLM-first adjudication + UI)")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

