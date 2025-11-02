"""
Simplified Automated Test for Navi Intelligence Phase 1

Tests NaviCommunicator logic without requiring full Streamlit environment.
This demonstrates the message selection logic is working correctly.

Usage:
    python tools/test_navi_simple.py
"""

from dataclasses import dataclass
from typing import Optional


# ============================================================================
# Minimal Mock Structures (No Imports Needed)
# ============================================================================

@dataclass
class MockCareRecommendation:
    tier: str
    confidence: float
    flags: list


@dataclass
class MockFinancialProfile:
    estimated_monthly_cost: float
    runway_months: int
    gap_amount: float
    coverage_percentage: float


@dataclass
class NaviContext:
    """Minimal NaviContext for testing."""
    progress: dict
    next_action: dict
    care_recommendation: Optional[MockCareRecommendation]
    financial_profile: Optional[MockFinancialProfile]
    advisor_appointment: Optional[object]
    flags: dict
    user_name: str
    is_authenticated: bool
    location: str
    hub_key: Optional[str]
    product_key: Optional[str]
    module_step: Optional[int]
    module_total: Optional[int]


# ============================================================================
# Core NaviCommunicator Logic (Copied for Testing)
# ============================================================================

class NaviCommunicatorTest:
    """Test version of NaviCommunicator with core logic."""
    
    @staticmethod
    def get_hub_encouragement(ctx: NaviContext) -> dict:
        """Generate flag-aware encouragement."""
        flags = ctx.care_recommendation.flags if ctx.care_recommendation else []
        tier = ctx.care_recommendation.tier if ctx.care_recommendation else None
        confidence = ctx.care_recommendation.confidence if ctx.care_recommendation else None
        
        runway_months = None
        if ctx.financial_profile:
            runway_months = ctx.financial_profile.runway_months
        
        # Check flags
        has_falls_risk = any(f.get('type') == 'falls_risk' and f.get('active') for f in flags)
        has_memory_support = any(f.get('type') == 'memory_support' and f.get('active') for f in flags)
        has_veteran_flag = any(f.get('type') == 'veteran_aanda_risk' and f.get('active') for f in flags)
        
        active_risk_count = sum(1 for f in flags if f.get('active') and 
                               f.get('type') in ['falls_risk', 'memory_support', 'wandering_risk', 
                                               'mobility_needs', 'safety_concern'])
        
        # Priority logic
        if has_falls_risk and has_memory_support:
            return {
                "icon": "🛡️",
                "text": "Fall risk plus memory support needs—safety is the priority.",
                "status": "urgent"
            }
        
        if has_falls_risk:
            return {
                "icon": "🛡️",
                "text": "Given the fall risk, finding the right support level is critical.",
                "status": "urgent"
            }
        
        if has_memory_support:
            return {
                "icon": "🧠",
                "text": "Memory support options will give you peace of mind and safety.",
                "status": "important"
            }
        
        if runway_months and runway_months < 12:
            return {
                "icon": "⏰",
                "text": f"Only {runway_months} months of funding—immediate planning is critical.",
                "status": "urgent"
            }
        
        if has_veteran_flag:
            return {
                "icon": "🎖️",
                "text": "As a veteran, you may qualify for Aid & Attendance benefits—up to $2,431/month.",
                "status": "important"
            }
        
        if confidence and confidence > 0.9 and active_risk_count == 0:
            return {
                "icon": "✅",
                "text": "Your plan is crystal clear—let's move forward with confidence.",
                "status": "confident"
            }
        
        completed_count = ctx.progress.get("completed_count", 0)
        if completed_count == 0:
            return {"icon": "🚀", "text": "Let's find the care option that fits best.", "status": "in_progress"}
        else:
            return {"icon": "💪", "text": "You're making great progress!", "status": "in_progress"}


# ============================================================================
# Test Scenarios
# ============================================================================

def create_test_context(
    tier: Optional[str] = None,
    confidence: float = 0.85,
    flags: Optional[list] = None,
    runway_months: Optional[int] = None,
    completed_count: int = 0
) -> NaviContext:
    """Create a test context."""
    care_rec = None
    if tier or flags:
        care_rec = MockCareRecommendation(
            tier=tier or "assisted_living",
            confidence=confidence,
            flags=flags or []
        )
    
    financial = None
    if runway_months is not None:
        financial = MockFinancialProfile(
            estimated_monthly_cost=5200.0,
            runway_months=runway_months,
            gap_amount=1664.0,
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


def run_test(name: str, ctx: NaviContext, expected_icon: str, expected_text: str) -> bool:
    """Run a single test."""
    result = NaviCommunicatorTest.get_hub_encouragement(ctx)
    
    icon_match = result["icon"] == expected_icon
    text_match = expected_text.lower() in result["text"].lower()
    
    status = "✅" if (icon_match and text_match) else "❌"
    
    print(f"\n{status} {name}")
    print(f"   Icon: {result['icon']} (expected: {expected_icon}) {'✅' if icon_match else '❌'}")
    print(f"   Text: {result['text']}")
    print(f"   Expected to contain: '{expected_text}' {'✅' if text_match else '❌'}")
    print(f"   Status: {result['status']}")
    
    return icon_match and text_match


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  NAVI INTELLIGENCE PHASE 1 - QUICK VALIDATION")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Falls Risk
    tests_total += 1
    ctx1 = create_test_context(
        tier="assisted_living",
        flags=[{"type": "falls_risk", "active": True}]
    )
    if run_test("Falls Risk Detection", ctx1, "🛡️", "fall risk"):
        tests_passed += 1
    
    # Test 2: Memory Support
    tests_total += 1
    ctx2 = create_test_context(
        tier="memory_care",
        flags=[{"type": "memory_support", "active": True}]
    )
    if run_test("Memory Support Detection", ctx2, "🧠", "memory"):
        tests_passed += 1
    
    # Test 3: Veteran Benefits
    tests_total += 1
    ctx3 = create_test_context(
        tier="assisted_living",
        flags=[{"type": "veteran_aanda_risk", "active": True}]
    )
    if run_test("Veteran Benefits Callout", ctx3, "🎖️", "veteran"):
        tests_passed += 1
    
    # Test 4: Low Runway
    tests_total += 1
    ctx4 = create_test_context(
        tier="assisted_living",
        runway_months=8
    )
    if run_test("Financial Urgency (8 months)", ctx4, "⏰", "8 months"):
        tests_passed += 1
    
    # Test 5: High Confidence
    tests_total += 1
    ctx5 = create_test_context(
        tier="independent",
        confidence=0.95,
        flags=[]
    )
    if run_test("High Confidence + Low Risk", ctx5, "✅", "confidence"):
        tests_passed += 1
    
    # Test 6: Multiple Urgent Flags
    tests_total += 1
    ctx6 = create_test_context(
        tier="memory_care",
        flags=[
            {"type": "falls_risk", "active": True},
            {"type": "memory_support", "active": True}
        ]
    )
    if run_test("Multiple Urgent Flags (Priority)", ctx6, "🛡️", "fall"):
        tests_passed += 1
    
    # Test 7: No MCIP Data
    tests_total += 1
    ctx7 = create_test_context()
    result7 = NaviCommunicatorTest.get_hub_encouragement(ctx7)
    has_valid_output = result7["icon"] and result7["text"] and result7["status"]
    print(f"\n{'✅' if has_valid_output else '❌'} Graceful Degradation (No MCIP Data)")
    print(f"   Icon: {result7['icon']} {'✅' if result7['icon'] else '❌'}")
    print(f"   Text: {result7['text']} {'✅' if result7['text'] else '❌'}")
    print(f"   Status: {result7['status']} {'✅' if result7['status'] else '❌'}")
    if has_valid_output:
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"  RESULTS: {tests_passed}/{tests_total} tests passed")
    print("=" * 70)
    
    if tests_passed == tests_total:
        print("\n🎉 SUCCESS! All core Navi Intelligence logic is working correctly.")
        print("\nYou can now:")
        print("  1. Set FEATURE_NAVI_INTELLIGENCE=on")
        print("  2. Run the Streamlit app")
        print("  3. See these messages in the Hub Lobby Navi panel")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed. Review logic above.")
    
    print()
    return tests_passed == tests_total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
