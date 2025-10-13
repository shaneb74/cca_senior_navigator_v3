"""
Tests for the Guided Care Plan care_recommendation module.

Run with: pytest tests/test_care_recommendation.py -v
"""
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from products.gcp.modules.care_recommendation.logic import (
    derive,
    _score_from_options,
    _score_multi,
    _eval,
    _confidence_label,
    sections_to_inputs
)


def load_test_manifest():
    """Load the actual module manifest for testing."""
    path = Path(__file__).parent.parent / "products" / "gcp" / "modules" / "care_recommendation" / "module.json"
    with path.open() as f:
        return json.load(f)


class TestScoring:
    """Test scoring logic functions."""
    
    def test_score_from_options_returns_correct_score(self):
        """Test single-select scoring."""
        questions = [
            {
                "id": "mobility",
                "options": [
                    {"label": "Independent", "value": "independent", "score": 0},
                    {"label": "Walker", "value": "walker", "score": 1},
                    {"label": "Wheelchair", "value": "wheelchair", "score": 2}
                ]
            }
        ]
        answers = {"mobility": "walker"}
        
        score = _score_from_options(questions, "mobility", answers)
        
        assert score == 1
    
    def test_score_from_options_handles_missing_answer(self):
        """Test that missing answers return 0."""
        questions = [{"id": "test", "options": [{"value": "a", "score": 5}]}]
        answers = {}
        
        score = _score_from_options(questions, "test", answers)
        
        assert score == 0
    
    def test_score_multi_sums_multiple_values(self):
        """Test multi-select scoring."""
        questions = [
            {
                "id": "badls",
                "options": [
                    {"label": "Bathing", "value": "bathing", "score": 1},
                    {"label": "Dressing", "value": "dressing", "score": 1},
                    {"label": "Eating", "value": "eating", "score": 1}
                ]
            }
        ]
        answers = {"badls": ["bathing", "dressing"]}
        
        score = _score_multi(questions, "badls", answers)
        
        assert score == 2
    
    def test_score_multi_respects_cap(self):
        """Test that scoring cap is enforced."""
        questions = [
            {
                "id": "conditions",
                "options": [
                    {"value": "diabetes", "score": 1},
                    {"value": "chf", "score": 1},
                    {"value": "copd", "score": 1},
                    {"value": "htn", "score": 1}
                ]
            }
        ]
        answers = {"conditions": ["diabetes", "chf", "copd", "htn"]}
        
        score = _score_multi(questions, "conditions", answers, cap=3)
        
        assert score == 3


class TestConditionalEvaluation:
    """Test the _eval function for conditional logic."""
    
    def test_eval_eq_condition(self):
        """Test equality condition."""
        ctx = {"memory_changes": "moderate"}
        
        assert _eval({"eq": ["memory_changes", "moderate"]}, ctx) is True
        assert _eval({"eq": ["memory_changes", "severe"]}, ctx) is False
    
    def test_eval_in_condition(self):
        """Test 'in' condition."""
        ctx = {"memory_changes": "moderate"}
        
        assert _eval({"in": ["memory_changes", ["moderate", "severe"]]}, ctx) is True
        assert _eval({"in": ["memory_changes", ["none", "occasional"]]}, ctx) is False
    
    def test_eval_gt_lt_conditions(self):
        """Test numeric comparison conditions."""
        ctx = {"score": 15}
        
        assert _eval({"gt": ["score", 10]}, ctx) is True
        assert _eval({"gt": ["score", 20]}, ctx) is False
        assert _eval({"lt": ["score", 20]}, ctx) is True
        assert _eval({"gte": ["score", 15]}, ctx) is True
    
    def test_eval_all_condition(self):
        """Test 'all' compound condition."""
        ctx = {"memory_changes": "severe", "primary_support": "none"}
        
        condition = {"all": [
            {"eq": ["memory_changes", "severe"]},
            {"eq": ["primary_support", "none"]}
        ]}
        
        assert _eval(condition, ctx) is True
    
    def test_eval_any_condition(self):
        """Test 'any' compound condition."""
        ctx = {"falls": "multiple"}
        
        condition = {"any": [
            {"eq": ["falls", "multiple"]},
            {"eq": ["mobility", "bedbound"]}
        ]}
        
        assert _eval(condition, ctx) is True


class TestDerive:
    """Test the main derive function with realistic scenarios."""
    
    def test_severe_memory_with_no_support_triggers_high_tier(self):
        """Test high-acuity recommendation for severe memory + no support."""
        manifest = load_test_manifest()
        answers = {
            "age_range": "85_plus",
            "living_situation": "alone",
            "isolation": "easy",
            "memory_changes": "severe",
            "primary_support": "none",
            "meds_complexity": "moderate",
            "mobility": "walker",
            "falls": "one",
            "chronic_conditions": ["diabetes"],
            "help_overall": "daily_help",
            "badls": ["bathing"],
            "iadls": ["meal_prep"],
            "hours_per_day": "4_8h",
            "behaviors": ["wandering"],
            "mood": "okay"
        }
        
        result = derive(manifest, answers, {})
        
        assert "Memory Care" in result["tier"]
        assert result["score"] > 15
        assert result["confidence"] > 0.5
        assert "tier" in result
        assert "points" in result
        assert isinstance(result["points"], list)
        assert len(result["points"]) > 0
    
    def test_independent_senior_gets_low_tier_recommendation(self):
        """Test independent living recommendation for healthy senior."""
        manifest = load_test_manifest()
        answers = {
            "age_range": "65_74",
            "living_situation": "family",
            "isolation": "easy",
            "memory_changes": "none",
            "primary_support": "family",
            "meds_complexity": "none",
            "mobility": "independent",
            "falls": "none",
            "chronic_conditions": [],
            "help_overall": "independent",
            "badls": [],
            "iadls": [],
            "hours_per_day": "lt1h",
            "behaviors": [],
            "mood": "great"
        }
        
        result = derive(manifest, answers, {})
        
        assert "Independent" in result["tier"] or "In-Home" in result["tier"]
        assert result["score"] < 10
        assert result["confidence"] > 0.7
    
    def test_assisted_living_recommendation_for_moderate_needs(self):
        """Test assisted living for moderate care needs."""
        manifest = load_test_manifest()
        answers = {
            "age_range": "75_84",
            "living_situation": "alone",
            "isolation": "somewhat",
            "memory_changes": "occasional",
            "primary_support": "family",
            "meds_complexity": "moderate",
            "mobility": "walker",
            "falls": "one",
            "chronic_conditions": ["htn", "arthritis"],
            "help_overall": "some_help",
            "badls": ["bathing"],
            "iadls": ["meal_prep", "housekeeping"],
            "hours_per_day": "1_3h",
            "behaviors": [],
            "mood": "mostly_good"
        }
        
        result = derive(manifest, answers, {})
        
        # Should be moderate tier (not independent, not memory care)
        assert result["score"] >= 8
        assert result["score"] <= 25
        assert result["confidence"] > 0.6
    
    def test_missing_critical_fields_returns_incomplete(self):
        """Test that missing required fields are handled gracefully."""
        manifest = load_test_manifest()
        answers = {
            "age_range": "75_84",
            # Missing critical fields: memory_changes, mobility, help_overall
        }
        
        result = derive(manifest, answers, {})
        
        assert result["tier"] == "Incomplete assessment"
        assert result["confidence"] == 0.0
        assert "missing" in " ".join(result["points"]).lower()
        assert "metadata" in result
        assert "missing_fields" in result["metadata"]
    
    def test_empty_answers_returns_error(self):
        """Test that empty answers are handled."""
        manifest = load_test_manifest()
        answers = {}
        
        result = derive(manifest, answers, {})
        
        assert result["tier"] == "Unable to determine"
        assert result["confidence"] == 0.0
    
    def test_flags_are_evaluated(self):
        """Test that warning flags are properly raised."""
        manifest = load_test_manifest()
        answers = {
            "age_range": "85_plus",
            "living_situation": "alone",
            "isolation": "very",
            "memory_changes": "severe",
            "primary_support": "none",
            "meds_complexity": "complex",
            "mobility": "wheelchair",
            "falls": "multiple",
            "chronic_conditions": ["diabetes", "chf"],
            "help_overall": "full_support",
            "badls": ["bathing", "dressing", "eating"],
            "iadls": ["meal_prep"],
            "hours_per_day": "24h",
            "behaviors": ["wandering", "confusion"],
            "mood": "low"
        }
        
        result = derive(manifest, answers, {})
        
        assert "flags" in result
        assert isinstance(result["flags"], dict)
        # Should have multiple flags raised for this high-risk scenario
        assert len(result["flags"]) > 0
    
    def test_confidence_calculation(self):
        """Test confidence scoring based on completeness."""
        manifest = load_test_manifest()
        
        # All questions answered
        complete_answers = {
            "age_range": "75_84",
            "living_situation": "alone",
            "isolation": "easy",
            "memory_changes": "occasional",
            "primary_support": "family",
            "meds_complexity": "simple",
            "mobility": "walker",
            "falls": "none",
            "chronic_conditions": ["htn"],
            "help_overall": "some_help",
            "badls": ["bathing"],
            "iadls": ["meal_prep"],
            "hours_per_day": "1_3h",
            "behaviors": [],
            "mood": "mostly_good"
        }
        
        result = derive(manifest, complete_answers, {})
        
        assert result["confidence"] > 0.8
        assert result["confidence_label"] in ["High confidence", "Moderate confidence"]
    
    def test_metadata_includes_scoring_details(self):
        """Test that metadata includes useful debugging info."""
        manifest = load_test_manifest()
        answers = {
            "age_range": "75_84",
            "living_situation": "alone",
            "isolation": "easy",
            "memory_changes": "occasional",
            "primary_support": "family",
            "meds_complexity": "simple",
            "mobility": "independent",
            "falls": "none",
            "chronic_conditions": [],
            "help_overall": "some_help",
            "badls": [],
            "iadls": ["meal_prep"],
            "hours_per_day": "1_3h",
            "behaviors": [],
            "mood": "okay"
        }
        
        result = derive(manifest, answers, {})
        
        assert "metadata" in result
        metadata = result["metadata"]
        assert "total_score" in metadata
        assert "tier_level" in metadata
        assert "score_breakdown" in metadata
        assert "answered_count" in metadata
        assert "total_questions" in metadata


class TestHelperFunctions:
    """Test helper utility functions."""
    
    def test_confidence_label_categories(self):
        """Test confidence labeling."""
        assert _confidence_label(0.95) == "High confidence"
        assert _confidence_label(0.75) == "Moderate confidence"
        assert _confidence_label(0.55) == "Low confidence"
        assert _confidence_label(0.3) == "Insufficient data"
    
    def test_sections_to_inputs_extracts_all_questions(self):
        """Test that sections_to_inputs flattens questions correctly."""
        manifest = load_test_manifest()
        inputs = sections_to_inputs(manifest)
        
        assert len(inputs) > 0
        assert all("id" in q for q in inputs)


if __name__ == "__main__":
    # Quick smoke test
    print("Running quick smoke tests...")
    
    # Test basic scoring
    test_scoring = TestScoring()
    test_scoring.test_score_from_options_returns_correct_score()
    test_scoring.test_score_multi_respects_cap()
    print("✅ Scoring tests passed")
    
    # Test conditional evaluation
    test_eval = TestConditionalEvaluation()
    test_eval.test_eval_eq_condition()
    test_eval.test_eval_all_condition()
    print("✅ Conditional evaluation tests passed")
    
    # Test derive scenarios
    test_derive = TestDerive()
    test_derive.test_independent_senior_gets_low_tier_recommendation()
    test_derive.test_missing_critical_fields_returns_incomplete()
    print("✅ Derive tests passed")
    
    print("\n🎉 All smoke tests passed! Run 'pytest tests/test_care_recommendation.py -v' for full test suite.")
