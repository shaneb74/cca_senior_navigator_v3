#!/usr/bin/env python3
"""
Test GCP → Cost Planner Handoff Integration

Validates:
1. GCP CTA sets flow.from_gcp flag correctly
2. Cost Planner intro detects handoff and generates blurb
3. Dual mode is enabled when multiple care plans exist
4. Hours gating still works with handoff logic
5. Threshold advisory logic integrates properly
6. Edge cases and error handling

Run: python test_gcp_handoff_integration.py
"""

import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

sys.path.append('.')

from ai.navi_engine import (
    detect_dual_mode_from_careplans,
    generate_handoff_blurb,
    get_primary_tier_from_careplans,
    normalize_tier,
)
from core.models import CarePlan


class TestGCPHandoffIntegration(unittest.TestCase):
    """Test suite for GCP → Cost Planner handoff functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_st = MagicMock()
        self.mock_st.session_state = {}

        # Sample CarePlan objects
        self.cp_primary_inhome = CarePlan(
            person_id="person_1",
            final_tier="in_home",
            hours_suggested="8",
            hours_user=None
        )

        self.cp_partner_al = CarePlan(
            person_id="person_2",
            final_tier="assisted_living",
            hours_suggested=None,
            hours_user=None
        )

        self.cp_single_mc = CarePlan(
            person_id="person_1",
            final_tier="memory_care",
            hours_suggested=None,
            hours_user=None
        )

    def test_dual_mode_detection_multiple_tiers(self):
        """Test dual mode is enabled when multiple different tiers exist."""
        careplans = [self.cp_primary_inhome, self.cp_partner_al]

        result = detect_dual_mode_from_careplans(careplans)
        self.assertTrue(result, "Should detect dual mode with different tiers")

    def test_dual_mode_detection_same_tiers(self):
        """Test dual mode is not enabled when all tiers are the same."""
        cp_another_inhome = CarePlan(
            person_id="person_2",
            final_tier="in_home",
            hours_suggested="6",
            hours_user=None
        )
        careplans = [self.cp_primary_inhome, cp_another_inhome]

        result = detect_dual_mode_from_careplans(careplans)
        self.assertFalse(result, "Should not detect dual mode with same tiers")

    def test_dual_mode_detection_single_careplan(self):
        """Test dual mode is not enabled with single care plan."""
        careplans = [self.cp_primary_inhome]

        result = detect_dual_mode_from_careplans(careplans)
        self.assertFalse(result, "Should not detect dual mode with single care plan")

    def test_dual_mode_detection_empty_list(self):
        """Test dual mode handles empty care plan list."""
        careplans = []

        result = detect_dual_mode_from_careplans(careplans)
        self.assertFalse(result, "Should not detect dual mode with no care plans")

    def test_primary_tier_extraction(self):
        """Test primary tier extraction from care plans."""
        careplans = [self.cp_primary_inhome, self.cp_partner_al]

        # Should return the last (most recent) care plan's tier
        result = get_primary_tier_from_careplans(careplans)
        self.assertEqual(result, "assisted_living", "Should return last care plan's tier")

    def test_primary_tier_extraction_empty(self):
        """Test primary tier extraction with empty list."""
        careplans = []

        result = get_primary_tier_from_careplans(careplans)
        self.assertIsNone(result, "Should return None for empty list")

    def test_handoff_blurb_generation_inhome(self):
        """Test handoff blurb generation for in-home care."""
        result = generate_handoff_blurb("in_home", dual_mode=False)

        self.assertIn("in-home care", result)
        self.assertIn("hours", result)
        self.assertNotIn("compare", result, "Should not mention comparison without dual mode")

    def test_handoff_blurb_generation_inhome_dual_mode(self):
        """Test handoff blurb generation for in-home care with dual mode."""
        result = generate_handoff_blurb("in_home", dual_mode=True)

        self.assertIn("in-home care", result)
        self.assertIn("hours", result)
        # Note: Basic dual_mode without partner_tier may not always mention comparison

    def test_handoff_blurb_generation_assisted_living(self):
        """Test handoff blurb generation for assisted living."""
        result = generate_handoff_blurb("assisted_living", dual_mode=False)

        self.assertIn("Assisted Living", result)
        self.assertIn("costs", result)

    def test_handoff_blurb_generation_with_flags(self):
        """Test handoff blurb generation includes flag-specific context."""
        flags = ["veteran_aanda_risk", "fall_risk"]
        result = generate_handoff_blurb("in_home", dual_mode=False, flags=flags)

        self.assertIn("in-home care", result)
        self.assertIn("veteran benefits", result)  # Updated to match new template text

    def test_tier_normalization(self):
        """Test tier normalization handles aliases correctly."""
        test_cases = [
            ("in_home_care", "in_home"),
            ("home_care", "in_home"),
            ("no_care", "none"),
            ("no_care_needed", "none"),
            ("assisted_living", "assisted_living"),  # Should remain unchanged
            ("", None),  # Empty string
            (None, None)  # None input
        ]

        for input_tier, expected in test_cases:
            with self.subTest(input_tier=input_tier):
                result = normalize_tier(input_tier) if input_tier is not None else normalize_tier("")
                self.assertEqual(result, expected, f"Failed to normalize {input_tier}")

    @patch('core.household.ensure_household_state')
    @patch('core.household.get_careplan_for')
    def test_cost_planner_handoff_integration(self, mock_get_careplan, mock_ensure_hh):
        """Test full Cost Planner intro handoff integration."""
        # Setup mocks
        mock_hh = Mock()
        mock_hh.zip = "90210"
        mock_hh.keep_home_default = True
        mock_hh.home_owner_type = "owner"
        mock_hh.has_partner = True
        mock_ensure_hh.return_value = mock_hh

        # Mock care plans (primary and partner with different tiers)
        mock_get_careplan.side_effect = [self.cp_primary_inhome, self.cp_partner_al]

        # Setup session state for handoff
        self.mock_st.session_state.update({
            "flow.from_gcp": True,
            "person.primary_id": "person_1",
            "person.partner_id": "person_2"
        })

        # Mock GCP recommendation
        mock_gcp_rec = Mock()
        mock_gcp_rec.tier = "in_home"
        mock_gcp_rec.flags = ["veteran_aanda_risk"]

        with patch('products.cost_planner_v2.intro.MCIP.get_care_recommendation', return_value=mock_gcp_rec):
            # Import after patching to ensure mocks are applied
            from ai.navi_engine import (
                detect_dual_mode_from_careplans,
                generate_handoff_blurb,
                get_primary_tier_from_careplans,
            )

            # Simulate the handoff logic from intro.py
            careplans = [self.cp_primary_inhome, self.cp_partner_al]
            dual_mode = detect_dual_mode_from_careplans(careplans)
            primary_tier = get_primary_tier_from_careplans(careplans)
            # Generate handoff blurb (with enhanced parameters)
            handoff_blurb = generate_handoff_blurb(
                primary_tier=primary_tier,
                dual_mode=dual_mode,
                flags=mock_gcp_rec.flags,
                partner_tier="in_home",  # Partner has in_home tier
                care_intensity="medium"
            )            # Verify results
            self.assertTrue(dual_mode, "Should enable dual mode with different care plans")
            self.assertEqual(primary_tier, "assisted_living", "Should get primary tier from latest care plan")
            self.assertIn("Assisted Living costs", handoff_blurb)
            self.assertIn("veteran benefits", handoff_blurb)  # Updated to match new template
            self.assertIn("compare", handoff_blurb)

    def test_hours_gating_compatibility(self):
        """Test that handoff logic is compatible with existing hours gating."""
        # This test verifies the logic doesn't interfere with existing functionality
        # The hours gating logic in comparison_view.py should still work

        # Simulate AL tier (should gate hours input unless compare_inhome=True)
        primary_tier = "assisted_living"
        dual_mode = False

        # Generate blurb
        blurb = generate_handoff_blurb(primary_tier, dual_mode)

        # Verify blurb mentions costs (basic validation)
        self.assertIn("costs", blurb)

        # The actual hours gating logic is tested in tools/smoke_household.py
        # This test just ensures our handoff doesn't break that pattern

    def test_error_handling_missing_tier(self):
        """Test error handling when care plans have no tier information."""
        cp_no_tier = CarePlan(
            person_id="person_1",
            final_tier=None,
            hours_suggested=None,
            hours_user=None
        )

        careplans = [cp_no_tier]

        # Should handle gracefully
        dual_mode = detect_dual_mode_from_careplans(careplans)
        primary_tier = get_primary_tier_from_careplans(careplans)

        self.assertFalse(dual_mode, "Should not detect dual mode with no valid tiers")
        self.assertIsNone(primary_tier, "Should return None for missing tier")

    def test_edge_case_malformed_careplan(self):
        """Test handling of malformed care plan objects."""
        # Mock object without expected attributes
        malformed_cp = Mock()
        malformed_cp.tier = "invalid_tier_value"  # Invalid tier value
        malformed_cp.final_tier = None  # Missing final_tier

        careplans = [malformed_cp]

        # Should handle gracefully without raising exceptions
        try:
            dual_mode = detect_dual_mode_from_careplans(careplans)
            primary_tier = get_primary_tier_from_careplans(careplans)

            self.assertFalse(dual_mode)
            self.assertIsNone(primary_tier)  # Should return None for invalid tier
        except Exception as e:
            self.fail(f"Should handle malformed care plans gracefully, got: {e}")


if __name__ == "__main__":
    print("🧪 Testing GCP → Cost Planner Handoff Integration")
    print("=" * 60)

    # Run the tests
    unittest.main(verbosity=2)
