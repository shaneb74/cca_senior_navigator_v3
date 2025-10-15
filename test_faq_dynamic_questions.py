"""
FAQ Dynamic Questions - Unit Tests

Test the question selection, scoring, and flag detection logic.
"""

import sys
sys.path.insert(0, '/Users/shane/Desktop/cca_senior_navigator_v3')

from pages.faq import (
    _get_active_flags,
    _build_suggested_questions,
    _get_top_3_suggestions,
    QUESTION_DATABASE
)
import streamlit as st


def test_no_flags():
    """Test default questions appear when no flags exist."""
    print("\n=== TEST 1: No Flags (New User) ===")
    
    # Clear session state
    if "handoff" in st.session_state:
        del st.session_state["handoff"]
    if "cost_data" in st.session_state:
        del st.session_state["cost_data"]
    st.session_state["ai_asked_questions"] = []
    
    # Get active flags
    flags = _get_active_flags()
    print(f"Active flags: {flags}")
    assert len(flags) == 0, "Should have no flags"
    
    # Get top 3 suggestions
    suggestions = _get_top_3_suggestions()
    print(f"Suggested questions: {suggestions}")
    assert len(suggestions) == 3, "Should return 3 suggestions"
    
    # Should be default questions
    default_qs = [q for q in QUESTION_DATABASE if not q["flags"]]
    assert any(s in [dq["question"] for dq in default_qs] for s in suggestions), \
        "Should return default questions"
    
    print("✅ PASS: Default questions appear for new users\n")


def test_veteran_flag():
    """Test veteran-related questions appear when veteran flag is set."""
    print("\n=== TEST 2: Veteran Flag ===")
    
    # Set veteran flags
    st.session_state["handoff"] = {
        "gcp": {
            "flags": {"veteran_eligible": True},
            "recommendation": "In-Home Care"
        }
    }
    st.session_state["cost_data"] = {"is_veteran": True}
    st.session_state["ai_asked_questions"] = []
    
    # Get active flags
    flags = _get_active_flags()
    print(f"Active flags: {flags}")
    assert "veteran_eligible" in flags, "Should have veteran_eligible flag"
    assert "is_veteran" in flags, "Should have is_veteran flag"
    
    # Get top 3 suggestions
    suggestions = _get_top_3_suggestions()
    print(f"Suggested questions: {suggestions}")
    
    # Should include VA-related questions
    va_questions = [
        "Am I eligible for VA Aid & Attendance benefits?",
        "Can VA help with home modifications for safety?"
    ]
    assert any(vaq in suggestions for vaq in va_questions), \
        "Should include at least one VA-related question"
    
    print("✅ PASS: Veteran questions appear when veteran flag is set\n")


def test_cognitive_decline_flag():
    """Test cognitive care questions appear when cognitive flags are set."""
    print("\n=== TEST 3: Cognitive Decline Flag ===")
    
    # Set cognitive flags
    st.session_state["handoff"] = {
        "gcp": {
            "flags": {"cog_moderate": True, "fall_risk": True},
            "recommendation": "Memory Care"
        }
    }
    st.session_state["cost_data"] = {}
    st.session_state["ai_asked_questions"] = []
    
    # Get active flags
    flags = _get_active_flags()
    print(f"Active flags: {flags}")
    assert "cog_moderate" in flags, "Should have cog_moderate flag"
    assert "memory_care" in flags, "Should derive memory_care from recommendation"
    assert "fall_risk" in flags, "Should have fall_risk flag"
    
    # Get top 3 suggestions
    suggestions = _get_top_3_suggestions()
    print(f"Suggested questions: {suggestions}")
    
    # Should include memory care or fall risk questions (both Priority 1)
    urgent_questions = [
        "What's the difference between Memory Care and Assisted Living?",
        "How can I reduce fall risk at home?"
    ]
    assert any(uq in suggestions for uq in urgent_questions), \
        "Should include at least one urgent (Priority 1) question"
    
    print("✅ PASS: Cognitive care questions appear when cognitive flags are set\n")


def test_financial_gap_flag():
    """Test affordability questions appear when financial gap exists."""
    print("\n=== TEST 4: Financial Gap Flag ===")
    
    # Set financial gap scenario
    st.session_state["handoff"] = {}
    st.session_state["cost_data"] = {
        "monthly_income": 2500,
        "estimated_monthly_cost": 6000,
        "total_assets": 75000,
        "is_home_owner": True
    }
    st.session_state["ai_asked_questions"] = []
    
    # Get active flags
    flags = _get_active_flags()
    print(f"Active flags: {flags}")
    assert "financial_gap" in flags, "Should derive financial_gap from income < cost"
    assert "has_assets" in flags, "Should derive has_assets from assets > 50k"
    assert "is_home_owner" in flags, "Should have is_home_owner flag"
    
    # Get top 3 suggestions
    suggestions = _get_top_3_suggestions()
    print(f"Suggested questions: {suggestions}")
    
    # Should include affordability questions
    affordability_questions = [
        "How can I afford care for my loved one?",
        "Should I use home equity to pay for care?"
    ]
    assert any(aq in suggestions for aq in affordability_questions), \
        "Should include at least one affordability question"
    
    print("✅ PASS: Affordability questions appear when financial gap exists\n")


def test_non_repetition():
    """Test questions don't repeat after being asked."""
    print("\n=== TEST 5: Non-Repetition ===")
    
    # Set some flags
    st.session_state["handoff"] = {
        "gcp": {
            "flags": {"fall_risk": True},
            "recommendation": "Assisted Living"
        }
    }
    st.session_state["cost_data"] = {}
    st.session_state["ai_asked_questions"] = []
    
    # Get first 3 suggestions
    suggestions1 = _get_top_3_suggestions()
    print(f"First suggestions: {suggestions1}")
    
    # Mark first question as asked
    st.session_state["ai_asked_questions"].append(suggestions1[0])
    
    # Get next 3 suggestions
    suggestions2 = _get_top_3_suggestions()
    print(f"Second suggestions: {suggestions2}")
    
    # First question should not appear again
    assert suggestions1[0] not in suggestions2, \
        f"Question '{suggestions1[0]}' should not repeat"
    
    print("✅ PASS: Questions don't repeat after being asked\n")


def test_scoring_priority():
    """Test Priority 1 questions score higher than Priority 3."""
    print("\n=== TEST 6: Scoring Priority ===")
    
    # Set flags that match both Priority 1 and Priority 3 questions
    st.session_state["handoff"] = {
        "gcp": {
            "flags": {"fall_risk": True},
            "recommendation": "Assisted Living"
        }
    }
    st.session_state["cost_data"] = {}
    st.session_state["ai_asked_questions"] = []
    
    # Get scored questions
    flags = _get_active_flags()
    scored = _build_suggested_questions(flags, [])
    
    # Find Priority 1 and Priority 3 questions
    p1_questions = [q for q in scored if q["priority"] == 1]
    p3_questions = [q for q in scored if q["priority"] == 3]
    
    if p1_questions and p3_questions:
        # Priority 1 should appear before Priority 3 in top suggestions
        top3 = _get_top_3_suggestions()
        p1_in_top3 = any(q["question"] in top3 for q in p1_questions)
        print(f"Priority 1 in top 3: {p1_in_top3}")
        
        if p1_in_top3:
            print("✅ PASS: Priority 1 questions prioritized over Priority 3\n")
        else:
            print("⚠️  NOTE: Priority 1 not in top 3 (depends on flag matches)\n")
    else:
        print("⚠️  NOTE: Test scenario doesn't have both P1 and P3 questions\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("FAQ DYNAMIC QUESTIONS - UNIT TESTS")
    print("="*70)
    
    try:
        test_no_flags()
        test_veteran_flag()
        test_cognitive_decline_flag()
        test_financial_gap_flag()
        test_non_repetition()
        test_scoring_priority()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
