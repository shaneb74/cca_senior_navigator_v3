#!/usr/bin/env python3
"""
Test Enhanced LLM Blurb Templates for Cost Planner Handoff

Tests the new contextual template system with all context variables:
- PRIMARY_TIER, PARTNER_TIER, DUAL_MODE
- THRESHOLD_CROSSED, CARE_INTENSITY, COMPARE_INHOME_SUGGESTED

Run: python test_handoff_templates.py
"""

import unittest
import sys
sys.path.append('.')

from ai.navi_engine import generate_handoff_blurb, _get_handoff_templates


class TestHandoffTemplates(unittest.TestCase):
    """Test enhanced handoff blurb templates."""
    
    def test_assisted_living_basic(self):
        """Test basic assisted living template."""
        blurb = generate_handoff_blurb(
            primary_tier="assisted_living",
            dual_mode=False,
            care_intensity="medium"
        )
        
        self.assertIn("Assisted Living", blurb)
        self.assertIn("costs", blurb)
        self.assertIn("monthly fees", blurb)

    def test_assisted_living_with_partner(self):
        """Test assisted living with partner having different tier."""
        blurb = generate_handoff_blurb(
            primary_tier="assisted_living",
            partner_tier="in_home",
            dual_mode=True,
            care_intensity="medium"
        )
        
        self.assertIn("Assisted Living", blurb)
        self.assertIn("partner's care options", blurb)
        self.assertIn("both of you", blurb)

    def test_assisted_living_compare_inhome(self):
        """Test assisted living with in-home comparison suggested."""
        blurb = generate_handoff_blurb(
            primary_tier="assisted_living",
            compare_inhome_suggested=True,
            care_intensity="medium"
        )
        
        self.assertIn("Assisted Living", blurb)
        self.assertIn("compare them with staying home", blurb)

    def test_assisted_living_threshold_crossed(self):
        """Test assisted living with budget concerns."""
        blurb = generate_handoff_blurb(
            primary_tier="assisted_living",
            threshold_crossed=True,
            care_intensity="medium"
        )
        
        self.assertIn("Assisted Living", blurb)
        self.assertIn("fit your budget", blurb)
        self.assertIn("financial assistance", blurb)

    def test_assisted_living_high_intensity(self):
        """Test assisted living with high care intensity."""
        blurb = generate_handoff_blurb(
            primary_tier="assisted_living",
            care_intensity="high"
        )
        
        self.assertIn("Assisted Living", blurb)
        self.assertIn("specialized care level", blurb)

    def test_memory_care_basic(self):
        """Test memory care template."""
        blurb = generate_handoff_blurb(
            primary_tier="memory_care",
            dual_mode=False,
            care_intensity="medium"
        )
        
        self.assertIn("Memory Care", blurb)
        self.assertIn("costs", blurb)

    def test_in_home_basic(self):
        """Test basic in-home care template."""
        blurb = generate_handoff_blurb(
            primary_tier="in_home",
            dual_mode=False,
            care_intensity="medium"
        )
        
        self.assertIn("in-home care", blurb)
        self.assertIn("hours and services", blurb)

    def test_in_home_with_facility_partner(self):
        """Test in-home with partner needing facility care."""
        blurb = generate_handoff_blurb(
            primary_tier="in_home",
            partner_tier="assisted_living",
            dual_mode=True,
            care_intensity="medium"
        )
        
        self.assertIn("in-home care", blurb)
        self.assertIn("facility options", blurb)
        self.assertIn("all your choices", blurb)

    def test_in_home_high_intensity(self):
        """Test in-home care with high intensity needs."""
        blurb = generate_handoff_blurb(
            primary_tier="in_home",
            care_intensity="high"
        )
        
        self.assertIn("intensive in-home support", blurb)
        self.assertIn("overnight care", blurb)

    def test_in_home_threshold_crossed(self):
        """Test in-home care with budget concerns."""
        blurb = generate_handoff_blurb(
            primary_tier="in_home",
            threshold_crossed=True
        )
        
        self.assertIn("in-home care", blurb)
        self.assertIn("within your budget", blurb)
        self.assertIn("veteran benefits", blurb)

    def test_in_home_customizable(self):
        """Test in-home care with customization focus."""
        blurb = generate_handoff_blurb(
            primary_tier="in_home",
            compare_inhome_suggested=True
        )
        
        self.assertIn("customize in-home care", blurb)
        self.assertIn("specific needs", blurb)

    def test_stay_home_basic(self):
        """Test stay home / independent template."""
        blurb = generate_handoff_blurb(
            primary_tier="none",
            dual_mode=False
        )
        
        self.assertIn("optional support services", blurb)
        self.assertIn("safety net", blurb)

    def test_stay_home_dual_mode(self):
        """Test stay home with dual mode."""
        blurb = generate_handoff_blurb(
            primary_tier="none",
            dual_mode=True
        )
        
        self.assertIn("optional support services", blurb)
        self.assertIn("care needs change", blurb)

    def test_stay_home_threshold_crossed(self):
        """Test stay home with budget focus."""
        blurb = generate_handoff_blurb(
            primary_tier="none",
            threshold_crossed=True
        )
        
        self.assertIn("affordable support services", blurb)
        self.assertIn("stay independent", blurb)

    def test_veteran_flag_context(self):
        """Test veteran flag adds appropriate context."""
        blurb = generate_handoff_blurb(
            primary_tier="assisted_living",
            flags=["veteran_aanda_risk"]
        )
        
        self.assertIn("veteran benefits", blurb)

    def test_support_flag_context(self):
        """Test support flag adds appropriate context."""
        blurb = generate_handoff_blurb(
            primary_tier="in_home",
            flags=["limited_support"]
        )
        
        self.assertIn("family support", blurb)
        self.assertIn("respite", blurb)

    def test_fall_risk_flag_context(self):
        """Test fall risk flag adds safety context."""
        blurb = generate_handoff_blurb(
            primary_tier="assisted_living",
            flags=["fall_risk"]
        )
        
        self.assertIn("safety features", blurb)
        self.assertIn("emergency response", blurb)

    def test_template_priority_order(self):
        """Test that templates are returned in priority order."""
        templates = _get_handoff_templates(
            primary_tier="assisted_living",
            partner_tier="in_home",
            dual_mode=True,
            flags=["veteran_aanda_risk"]
        )
        
        self.assertTrue(len(templates) > 0)
        # First template should be the most specific (partner context)
        self.assertIn("partner's care options", templates[0])

    def test_fallback_template(self):
        """Test fallback template for unknown scenarios."""
        blurb = generate_handoff_blurb(
            primary_tier="unknown_tier",  # This should trigger fallback
            dual_mode=False
        )
        
        # Should get a fallback template
        self.assertIn("costs", blurb)
        self.assertIn("care options", blurb)

    def test_all_context_variables(self):
        """Test template with all context variables set."""
        blurb = generate_handoff_blurb(
            primary_tier="memory_care",
            partner_tier="assisted_living", 
            dual_mode=True,
            threshold_crossed=True,
            care_intensity="high",
            compare_inhome_suggested=True,
            flags=["veteran_aanda_risk", "fall_risk"]
        )
        
        self.assertIn("Memory Care", blurb)
        # Should pick the most relevant template based on context priority
        self.assertTrue(len(blurb) > 10)  # Should generate meaningful content


if __name__ == "__main__":
    print("🧪 Testing Enhanced LLM Blurb Templates")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)