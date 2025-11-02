"""
Automated Test Script for Navi Intelligence Phase 1

This script simulates user journeys and validates that NaviCommunicator
responds correctly to different MCIP states.

Usage:
    python tools/test_navi_intelligence_live.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataclasses import dataclass
from typing import Optional
from core.navi_intelligence import NaviCommunicator
from core.navi import NaviContext


# ============================================================================
# Mock MCIP Data Structures
# ============================================================================

@dataclass
class MockCareRecommendation:
    tier: str
    confidence: float
    flags: list[dict]
    tier_score: float = 0.0
    rationale: Optional[list[str]] = None
    
    def __post_init__(self):
        if self.rationale is None:
            self.rationale = []


@dataclass
class MockFinancialProfile:
    estimated_monthly_cost: float
    runway_months: int
    gap_amount: float
    coverage_percentage: float


@dataclass
class MockAdvisorAppointment:
    scheduled: bool
    date: str = ""
    time: str = ""


def create_test_context(
    tier: Optional[str] = None,
    confidence: float = 0.85,
    flags: Optional[list] = None,
    runway_months: Optional[int] = None,
    gap_amount: Optional[float] = None,
    completed_count: int = 0
) -> NaviContext:
    """Create a test NaviContext with specified MCIP data."""
    care_rec = None
    if tier or flags:
        care_rec = MockCareRecommendation(
            tier=tier or "assisted_living",
            confidence=confidence,
            flags=flags or []
        )
    
    financial = None
    if runway_months is not None or gap_amount is not None:
        financial = MockFinancialProfile(
            estimated_monthly_cost=5200.0,
            runway_months=runway_months if runway_months is not None else 36,
            gap_amount=gap_amount if gap_amount is not None else 1000.0,
            coverage_percentage=0.68
        )
    
    return NaviContext(
        progress={"completed_count": completed_count, "completed_products": []},
        next_action={"action": "Continue", "route": "hub_lobby", "reason": "Keep going"},
        care_recommendation=care_rec,
        financial_profile=financial,
        advisor_appointment=None,
        flags={},
        user_name="Test User",
        is_authenticated=True,
        location="hub",
        hub_key=None,
        product_key=None,
        module_step=None,
        module_total=None
    )


# ============================================================================
# Test Scenarios
# ============================================================================

def print_header(title: str):
    """Print a formatted test header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(label: str, value, expected: Optional[str] = None):
    """Print a test result."""
    if expected:
        match = "✅" if expected.lower() in str(value).lower() else "❌"
        print(f"{match} {label}: {value}")
        if match == "❌":
            print(f"   Expected to contain: {expected}")
    else:
        print(f"   {label}: {value}")


def test_scenario_1_falls_risk():
    """Test Scenario 1: Falls Risk Urgency"""
    print_header("Scenario 1: Falls Risk Detection")
    
    ctx = create_test_context(
        tier="assisted_living",
        confidence=0.88,
        flags=[
            {"type": "falls_risk", "active": True, "severity": "moderate"}
        ]
    )
    
    result = NaviCommunicator.get_hub_encouragement(ctx)
    
    print("\n📋 Test: User with fall risk completes GCP")
    print("   MCIP publishes: falls_risk flag active")
    print("\n🎯 Expected Behavior:")
    print("   - Icon should be 🛡️ (safety shield)")
    print("   - Message mentions 'fall risk'")
    print("   - Status is 'urgent'")
    
    print("\n🔍 Actual Result:")
    print_result("Icon", result["icon"], "🛡️")
    print_result("Text", result["text"], "fall risk")
    print_result("Status", result["status"], "urgent")
    
    return result["icon"] == "🛡️" and "fall" in result["text"].lower()


def test_scenario_2_memory_support():
    """Test Scenario 2: Memory Support Importance"""
    print_header("Scenario 2: Memory Support Detection")
    
    ctx = create_test_context(
        tier="memory_care",
        confidence=0.91,
        flags=[
            {"type": "memory_support", "active": True, "severity": "moderate"}
        ]
    )
    
    result = NaviCommunicator.get_hub_encouragement(ctx)
    
    print("\n📋 Test: User with memory decline completes GCP")
    print("   MCIP publishes: memory_support flag active")
    print("\n🎯 Expected Behavior:")
    print("   - Icon should be 🧠 (brain)")
    print("   - Message mentions 'memory'")
    print("   - Status is 'important'")
    
    print("\n🔍 Actual Result:")
    print_result("Icon", result["icon"], "🧠")
    print_result("Text", result["text"], "memory")
    print_result("Status", result["status"], "important")
    
    return result["icon"] == "🧠" and "memory" in result["text"].lower()


def test_scenario_3_veteran_benefits():
    """Test Scenario 3: Veteran Benefits Callout"""
    print_header("Scenario 3: Veteran Benefits Detection")
    
    ctx = create_test_context(
        tier="assisted_living",
        confidence=0.90,
        flags=[
            {"type": "veteran_aanda_risk", "active": True}
        ]
    )
    
    result = NaviCommunicator.get_hub_encouragement(ctx)
    
    print("\n📋 Test: Veteran user completes GCP")
    print("   MCIP publishes: veteran_aanda_risk flag active")
    print("\n🎯 Expected Behavior:")
    print("   - Icon should be 🎖️ (military medal)")
    print("   - Message mentions 'veteran' or 'Aid & Attendance'")
    print("   - Mentions '$2,431' benefit amount")
    
    print("\n🔍 Actual Result:")
    print_result("Icon", result["icon"], "🎖️")
    print_result("Text", result["text"], "veteran")
    print_result("Benefit Amount", result["text"], "2,431")
    
    return result["icon"] == "🎖️" and ("veteran" in result["text"].lower() or "2,431" in result["text"])


def test_scenario_4_low_runway():
    """Test Scenario 4: Financial Urgency - Low Runway"""
    print_header("Scenario 4: Financial Urgency Detection")
    
    ctx = create_test_context(
        tier="assisted_living",
        runway_months=8,
        gap_amount=2000
    )
    
    result = NaviCommunicator.get_hub_encouragement(ctx)
    
    print("\n📋 Test: User completes Cost Planner with 8-month runway")
    print("   MCIP calculates: runway_months = 8, gap_amount = $2,000")
    print("\n🎯 Expected Behavior:")
    print("   - Icon should be ⏰ (alarm clock)")
    print("   - Message mentions '8 months' or 'month'")
    print("   - Status is 'urgent'")
    
    print("\n🔍 Actual Result:")
    print_result("Icon", result["icon"], "⏰")
    print_result("Text", result["text"], "month")
    print_result("Status", result["status"], "urgent")
    
    return result["icon"] == "⏰" and "month" in result["text"].lower()


def test_scenario_5_high_confidence():
    """Test Scenario 5: High Confidence Positive Reinforcement"""
    print_header("Scenario 5: High Confidence + Low Risk")
    
    ctx = create_test_context(
        tier="independent",
        confidence=0.95,
        flags=[]  # No risk flags
    )
    
    result = NaviCommunicator.get_hub_encouragement(ctx)
    
    print("\n📋 Test: User completes GCP with 95% confidence, no risks")
    print("   MCIP publishes: confidence = 0.95, flags = []")
    print("\n🎯 Expected Behavior:")
    print("   - Icon should be ✅ (checkmark)")
    print("   - Message is positive/confident")
    print("   - Status is 'confident'")
    
    print("\n🔍 Actual Result:")
    print_result("Icon", result["icon"], "✅")
    print_result("Text", result["text"], "confidence")
    print_result("Status", result["status"], "confident")
    
    return result["icon"] == "✅" and result["status"] == "confident"


def test_scenario_6_dynamic_reason_memory_care():
    """Test Scenario 6: Dynamic Reason Text - Memory Care"""
    print_header("Scenario 6: Dynamic Reason Text (After GCP)")
    
    ctx = create_test_context(
        tier="memory_care",
        confidence=0.92,
        completed_count=1  # GCP complete
    )
    
    result = NaviCommunicator.get_dynamic_reason_text(ctx)
    
    print("\n📋 Test: User completes GCP with Memory Care recommendation")
    print("   MCIP publishes: tier = 'memory_care', completed_count = 1")
    print("\n🎯 Expected Behavior:")
    print("   - Reason text mentions 'Memory Care'")
    print("   - Mentions 'cost' or 'expensive' or 'specialized'")
    
    print("\n🔍 Actual Result:")
    print_result("Reason Text", result, "memory care")
    
    return "memory care" in result.lower() and ("cost" in result.lower() or "specialized" in result.lower())


def test_scenario_7_cost_planner_intro():
    """Test Scenario 7: Cost Planner Intro - Tier Specific"""
    print_header("Scenario 7: Cost Planner Tier-Specific Intro")
    
    ctx = create_test_context(
        tier="assisted_living",
        confidence=0.88
    )
    
    result = NaviCommunicator.get_cost_planner_intro(ctx)
    
    print("\n📋 Test: User enters Cost Planner after GCP (Assisted Living)")
    print("   MCIP tier: 'assisted_living'")
    print("\n🎯 Expected Behavior:")
    print("   - Title mentions cost range '$4,500-6,500'")
    print("   - Title says 'Assisted Living'")
    print("   - Body references GCP recommendation")
    
    print("\n🔍 Actual Result:")
    print_result("Title", result["title"], "Assisted Living")
    print_result("Cost Range", result["title"], "4,500")
    print_result("Body", result["body"], "Guided Care Plan")
    print_result("Tip", result["tip"], "")
    
    return "assisted living" in result["title"].lower() and "4,500" in result["title"]


def test_scenario_8_financial_strategy():
    """Test Scenario 8: Financial Strategy - Critical Runway"""
    print_header("Scenario 8: Financial Strategy Advice")
    
    ctx = create_test_context(
        tier="assisted_living",
        runway_months=10,
        gap_amount=2200,
        flags=[
            {"type": "veteran_aanda_risk", "active": True}
        ]
    )
    
    result = NaviCommunicator.get_financial_strategy_advice(ctx)
    
    print("\n📋 Test: User with 10-month runway, veteran status")
    print("   MCIP: runway_months = 10, veteran flag active")
    print("\n🎯 Expected Behavior:")
    print("   - Title shows '10 months'")
    print("   - Urgency is 'critical'")
    print("   - Strategies include VA benefits")
    print("   - First strategy mentions 'VA' or 'veteran'")
    
    print("\n🔍 Actual Result:")
    print_result("Title", result["title"], "10")
    print_result("Urgency", result["urgency"], "critical")
    print(f"   Strategies ({len(result['strategies'])} total):")
    for i, strategy in enumerate(result["strategies"], 1):
        print(f"      {i}. {strategy}")
    
    has_va = any("VA" in s or "veteran" in s.lower() for s in result["strategies"])
    print(f"\n   VA Strategy Present: {'✅' if has_va else '❌'}")
    
    return result["urgency"] == "critical" and has_va


def test_scenario_9_multiple_urgent_flags():
    """Test Scenario 9: Multiple Urgent Flags (Priority Logic)"""
    print_header("Scenario 9: Multiple Urgent Flags (Priority)")
    
    ctx = create_test_context(
        tier="memory_care",
        confidence=0.90,
        flags=[
            {"type": "falls_risk", "active": True, "severity": "high"},
            {"type": "memory_support", "active": True, "severity": "moderate"},
            {"type": "wandering_risk", "active": True}
        ]
    )
    
    result = NaviCommunicator.get_hub_encouragement(ctx)
    
    print("\n📋 Test: User with falls + memory + wandering flags")
    print("   MCIP publishes: 3 urgent risk flags active")
    print("\n🎯 Expected Behavior:")
    print("   - Falls + Memory should trigger combined urgent message")
    print("   - Priority 1 (falls + memory) should win")
    print("   - Status should be 'urgent'")
    
    print("\n🔍 Actual Result:")
    print_result("Icon", result["icon"], "🛡️")
    print_result("Text", result["text"], "fall")
    print_result("Status", result["status"], "urgent")
    
    return result["status"] == "urgent" and ("fall" in result["text"].lower() or "memory" in result["text"].lower())


def test_scenario_10_no_mcip_data():
    """Test Scenario 10: Graceful Degradation (No MCIP Data)"""
    print_header("Scenario 10: Graceful Degradation")
    
    ctx = create_test_context(
        # No tier, no flags, no financial data
    )
    
    result = NaviCommunicator.get_hub_encouragement(ctx)
    
    print("\n📋 Test: New user, no MCIP data available")
    print("   MCIP: care_recommendation = None, financial_profile = None")
    print("\n🎯 Expected Behavior:")
    print("   - Should return generic encouragement")
    print("   - Should not crash or error")
    print("   - Should have valid icon, text, status")
    
    print("\n🔍 Actual Result:")
    print(f"   Icon: {result['icon']} (valid: {'✅' if result['icon'] else '❌'})")
    print(f"   Text: {result['text']} (valid: {'✅' if result['text'] else '❌'})")
    print(f"   Status: {result['status']} (valid: {'✅' if result['status'] else '❌'})")
    
    return result["icon"] and result["text"] and result["status"]


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all test scenarios."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "NAVI INTELLIGENCE PHASE 1 - AUTOMATED TESTS" + " " * 15 + "║")
    print("╚" + "═" * 68 + "╝")
    
    tests = [
        ("Falls Risk Detection", test_scenario_1_falls_risk),
        ("Memory Support Detection", test_scenario_2_memory_support),
        ("Veteran Benefits Callout", test_scenario_3_veteran_benefits),
        ("Financial Urgency (Low Runway)", test_scenario_4_low_runway),
        ("High Confidence + Low Risk", test_scenario_5_high_confidence),
        ("Dynamic Reason Text", test_scenario_6_dynamic_reason_memory_care),
        ("Cost Planner Tier Intro", test_scenario_7_cost_planner_intro),
        ("Financial Strategy Advice", test_scenario_8_financial_strategy),
        ("Multiple Urgent Flags", test_scenario_9_multiple_urgent_flags),
        ("Graceful Degradation", test_scenario_10_no_mcip_data),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n📊 Results: {passed_count}/{total_count} tests passed\n")
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print("\n" + "=" * 70)
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED! Navi Intelligence is working correctly.")
    else:
        print(f"⚠️  {total_count - passed_count} test(s) failed. Review output above.")
    
    print("=" * 70 + "\n")
    
    return passed_count == total_count


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
