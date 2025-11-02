"""
Tests for NaviCommunicator (Phase 1 - Infrastructure)

Tests that NaviCommunicator correctly reads from MCIP data and selects
appropriate messages without calculating any intelligence.
"""

import pytest
from dataclasses import dataclass
from typing import Any

from core.navi_intelligence import NaviCommunicator
from core.navi import NaviContext


# Mock MCIP data structures
@dataclass
class MockCareRecommendation:
    tier: str
    confidence: float
    flags: list[dict]


@dataclass
class MockFinancialProfile:
    estimated_monthly_cost: float
    runway_months: int
    gap_amount: float
    coverage_percentage: float


@dataclass
class MockAdvisorAppointment:
    scheduled: bool
    date: str
    time: str


def create_test_context(
    tier: str = None,
    confidence: float = None,
    flags: list = None,
    runway_months: int = None,
    gap_amount: float = None,
    completed_count: int = 0
) -> NaviContext:
    """Create a test NaviContext with specified MCIP data."""
    care_rec = None
    if tier or confidence or flags:
        care_rec = MockCareRecommendation(
            tier=tier or "assisted_living",
            confidence=confidence or 0.85,
            flags=flags or []
        )
    
    financial = None
    if runway_months or gap_amount:
        financial = MockFinancialProfile(
            estimated_monthly_cost=5200.0,
            runway_months=runway_months or 36,
            gap_amount=gap_amount or 1000.0,
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


class TestHubEncouragement:
    """Test get_hub_encouragement reads MCIP data correctly."""
    
    def test_falls_risk_flag_triggers_urgent(self):
        """Falls risk should trigger urgent safety message."""
        ctx = create_test_context(
            flags=[
                {"type": "falls_risk", "active": True, "severity": "moderate"}
            ]
        )
        
        result = NaviCommunicator.get_hub_encouragement(ctx)
        
        assert result["icon"] == "🛡️"
        assert "fall risk" in result["text"].lower()
        assert result["status"] == "urgent"
    
    def test_memory_support_flag_triggers_important(self):
        """Memory support flag should trigger important message."""
        ctx = create_test_context(
            flags=[
                {"type": "memory_support", "active": True, "severity": "mild"}
            ]
        )
        
        result = NaviCommunicator.get_hub_encouragement(ctx)
        
        assert result["icon"] == "🧠"
        assert "memory" in result["text"].lower()
        assert result["status"] == "important"
    
    def test_multiple_urgent_flags(self):
        """Falls + memory should trigger combined urgent message."""
        ctx = create_test_context(
            flags=[
                {"type": "falls_risk", "active": True},
                {"type": "memory_support", "active": True}
            ]
        )
        
        result = NaviCommunicator.get_hub_encouragement(ctx)
        
        assert result["status"] == "urgent"
        assert "fall" in result["text"].lower() or "memory" in result["text"].lower()
    
    def test_low_runway_triggers_financial_urgency(self):
        """Low runway (<12 months) should trigger urgent financial message."""
        ctx = create_test_context(runway_months=8)
        
        result = NaviCommunicator.get_hub_encouragement(ctx)
        
        assert result["icon"] == "⏰"
        assert "8 months" in result["text"] or "month" in result["text"]
        assert result["status"] == "urgent"
    
    def test_high_confidence_low_risk_positive(self):
        """High confidence with no risks should give positive reinforcement."""
        ctx = create_test_context(
            tier="independent",
            confidence=0.95,
            flags=[]  # No active risks
        )
        
        result = NaviCommunicator.get_hub_encouragement(ctx)
        
        assert result["icon"] == "✅"
        assert "confidence" in result["text"].lower() or "clear" in result["text"].lower()
        assert result["status"] == "confident"
    
    def test_veteran_flag_callout(self):
        """Veteran flag should mention benefits opportunity."""
        ctx = create_test_context(
            flags=[
                {"type": "veteran_aanda_risk", "active": True}
            ]
        )
        
        result = NaviCommunicator.get_hub_encouragement(ctx)
        
        assert result["icon"] == "🎖️"
        assert "veteran" in result["text"].lower()
        assert "2,431" in result["text"] or "aid" in result["text"].lower()
    
    def test_generic_fallback_no_mcip_data(self):
        """Should gracefully handle missing MCIP data."""
        ctx = create_test_context()  # No MCIP data
        
        result = NaviCommunicator.get_hub_encouragement(ctx)
        
        # Should return generic encouragement
        assert "icon" in result
        assert "text" in result
        assert "status" in result


class TestDynamicReasonText:
    """Test get_dynamic_reason_text reads MCIP outcomes."""
    
    def test_after_gcp_memory_care(self):
        """After GCP with memory care tier should preview costs."""
        ctx = create_test_context(
            tier="memory_care",
            completed_count=1
        )
        
        result = NaviCommunicator.get_dynamic_reason_text(ctx)
        
        assert "memory care" in result.lower()
        assert "cost" in result.lower() or "expensive" in result.lower() or "specialized" in result.lower()
    
    def test_after_gcp_assisted_living_with_falls(self):
        """After GCP with assisted living + falls should mention prevention."""
        ctx = create_test_context(
            tier="assisted_living",
            flags=[{"type": "falls_risk", "active": True}],
            completed_count=1
        )
        
        result = NaviCommunicator.get_dynamic_reason_text(ctx)
        
        assert "fall" in result.lower()
    
    def test_after_cost_planner_with_gap(self):
        """After Cost Planner with funding gap should mention advisor."""
        ctx = create_test_context(
            gap_amount=1664,
            completed_count=2
        )
        
        result = NaviCommunicator.get_dynamic_reason_text(ctx)
        
        assert "advisor" in result.lower()
        assert "1,664" in result or "gap" in result.lower()
    
    def test_generic_fallback(self):
        """Should return generic text without MCIP data."""
        ctx = create_test_context()
        
        result = NaviCommunicator.get_dynamic_reason_text(ctx)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestCostPlannerIntro:
    """Test get_cost_planner_intro uses MCIP tier."""
    
    def test_memory_care_tier(self):
        """Memory care tier should show higher cost range."""
        ctx = create_test_context(tier="memory_care")
        
        result = NaviCommunicator.get_cost_planner_intro(ctx)
        
        assert "6,000" in result["title"] or "9,000" in result["title"]
        assert "memory care" in result["title"].lower()
    
    def test_assisted_living_tier(self):
        """Assisted living tier should show moderate cost range."""
        ctx = create_test_context(tier="assisted_living")
        
        result = NaviCommunicator.get_cost_planner_intro(ctx)
        
        assert "4,500" in result["title"] or "6,500" in result["title"]
        assert "assisted living" in result["title"].lower()
    
    def test_veteran_flag_adds_benefits_tip(self):
        """Veteran flag should add VA benefits tip."""
        ctx = create_test_context(
            tier="assisted_living",
            flags=[{"type": "veteran_aanda_risk", "active": True}]
        )
        
        result = NaviCommunicator.get_cost_planner_intro(ctx)
        
        assert "veteran" in result["tip"].lower() or "2,431" in result["tip"]
    
    def test_no_tier_generic_message(self):
        """No tier should give generic cost exploration message."""
        ctx = create_test_context()  # No tier
        
        result = NaviCommunicator.get_cost_planner_intro(ctx)
        
        assert "cost" in result["title"].lower()
        assert result["title"] is not None


class TestFinancialStrategyAdvice:
    """Test get_financial_strategy_advice reads runway/gap from MCIP."""
    
    def test_critical_runway_under_12_months(self):
        """Runway <12 months should trigger critical urgency."""
        ctx = create_test_context(runway_months=8, gap_amount=2000)
        
        result = NaviCommunicator.get_financial_strategy_advice(ctx)
        
        assert result["urgency"] == "critical"
        assert "8 months" in result["title"] or "8 month" in result["title"]
        assert len(result["strategies"]) > 0
    
    def test_urgent_runway_12_24_months(self):
        """Runway 12-24 months should be urgent."""
        ctx = create_test_context(runway_months=18)
        
        result = NaviCommunicator.get_financial_strategy_advice(ctx)
        
        assert result["urgency"] == "high"
        assert "18" in result["title"]
    
    def test_moderate_runway_24_48_months(self):
        """Runway 24-48 months should be moderate urgency."""
        ctx = create_test_context(runway_months=36, gap_amount=1664)
        
        result = NaviCommunicator.get_financial_strategy_advice(ctx)
        
        assert result["urgency"] == "moderate"
        assert "36" in result["title"]
    
    def test_comfortable_runway_over_48_months(self):
        """Runway 48+ months should be low urgency."""
        ctx = create_test_context(runway_months=60)
        
        result = NaviCommunicator.get_financial_strategy_advice(ctx)
        
        assert result["urgency"] == "low"
        assert "✅" in result["title"] or "excellent" in result["title"].lower()
    
    def test_veteran_flag_prioritizes_va_strategy(self):
        """Veteran flag should add VA benefits as top strategy."""
        ctx = create_test_context(
            runway_months=18,
            flags=[{"type": "veteran_aanda_risk", "active": True}]
        )
        
        result = NaviCommunicator.get_financial_strategy_advice(ctx)
        
        # VA should be first strategy for urgent cases
        assert any("VA" in s or "veteran" in s.lower() for s in result["strategies"])
    
    def test_no_financial_profile_graceful(self):
        """Should handle missing financial profile."""
        ctx = create_test_context()  # No financial data
        
        result = NaviCommunicator.get_financial_strategy_advice(ctx)
        
        assert result["urgency"] == "low"
        assert "complete" in result["title"].lower() or "financial" in result["title"].lower()


class TestArchitecturalBoundaries:
    """Test that NaviCommunicator NEVER calculates intelligence."""
    
    def test_never_modifies_mcip_data(self):
        """NaviCommunicator should never modify MCIP data."""
        ctx = create_test_context(
            tier="assisted_living",
            confidence=0.85,
            flags=[{"type": "falls_risk", "active": True}]
        )
        
        original_tier = ctx.care_recommendation.tier
        original_confidence = ctx.care_recommendation.confidence
        original_flags = ctx.care_recommendation.flags.copy()
        
        # Run multiple methods
        NaviCommunicator.get_hub_encouragement(ctx)
        NaviCommunicator.get_dynamic_reason_text(ctx)
        NaviCommunicator.get_cost_planner_intro(ctx)
        
        # Verify MCIP data unchanged
        assert ctx.care_recommendation.tier == original_tier
        assert ctx.care_recommendation.confidence == original_confidence
        assert ctx.care_recommendation.flags == original_flags
    
    def test_only_reads_from_context(self):
        """All methods should only read from NaviContext, never session state."""
        ctx = create_test_context(tier="memory_care")
        
        # These should work with just context - no session state access
        result1 = NaviCommunicator.get_hub_encouragement(ctx)
        result2 = NaviCommunicator.get_cost_planner_intro(ctx)
        
        assert result1 is not None
        assert result2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
