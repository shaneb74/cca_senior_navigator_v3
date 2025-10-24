#!/usr/bin/env python3
"""
Test GCP Adjudication Simplification — LLM-First, Deterministic Fallback Only

Tests the new LLM-first adjudication policy where:
1) LLM tier is used if valid and in allowed set
2) Deterministic tier is fallback only 
3) Confidence is logged but not used for override

Run: python test_gcp_adjudication.py
"""

import sys
import unittest
from unittest.mock import patch

sys.path.append('.')

from core.models import CarePlan
from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier


class TestGCPAdjudication(unittest.TestCase):
    """Test suite for LLM-first GCP adjudication."""

    def setUp(self):
        """Set up test fixtures."""
        self.bands = {"cog": "moderate", "sup": "high"}
        self.allowed_tiers = {"assisted_living", "memory_care", "in_home"}

    def test_llm_valid_wins(self):
        """Test LLM recommendation wins when valid and allowed."""
        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers=self.allowed_tiers,
            llm_tier="memory_care",  # Different from det
            llm_conf=0.85,
            bands=self.bands,
            risky=False
        )

        self.assertEqual(final_tier, "memory_care", "LLM tier should win when valid")
        self.assertEqual(decision["source"], "llm")
        self.assertEqual(decision["adjudication_reason"], "llm_valid")
        self.assertEqual(decision["llm"], "memory_care")
        self.assertEqual(decision["det"], "assisted_living")

    def test_llm_invalid_guard_fallback(self):
        """Test fallback to deterministic when LLM tier not in allowed set."""
        # LLM suggests memory_care but it's not in allowed set
        allowed_no_mc = {"assisted_living", "in_home"}

        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers=allowed_no_mc,
            llm_tier="memory_care",  # Not in allowed set
            llm_conf=0.90,
            bands=self.bands,
            risky=False
        )

        self.assertEqual(final_tier, "assisted_living", "Should fallback to deterministic")
        self.assertEqual(decision["source"], "fallback")
        self.assertEqual(decision["adjudication_reason"], "llm_invalid_guard")
        self.assertEqual(decision["llm"], "memory_care")
        self.assertEqual(decision["det"], "assisted_living")

    def test_llm_timeout_fallback(self):
        """Test fallback to deterministic when LLM is missing/timeout."""
        final_tier, decision = _choose_final_tier(
            det_tier="in_home",
            allowed_tiers=self.allowed_tiers,
            llm_tier=None,  # LLM timeout/missing
            llm_conf=None,
            bands=self.bands,
            risky=False
        )

        self.assertEqual(final_tier, "in_home", "Should fallback to deterministic")
        self.assertEqual(decision["source"], "fallback")
        self.assertEqual(decision["adjudication_reason"], "llm_timeout")
        self.assertIsNone(decision["llm"])
        self.assertEqual(decision["det"], "in_home")

    def test_llm_and_det_same(self):
        """Test when LLM and deterministic agree."""
        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers=self.allowed_tiers,
            llm_tier="assisted_living",  # Same as det
            llm_conf=0.75,
            bands=self.bands,
            risky=False
        )

        self.assertEqual(final_tier, "assisted_living", "Should use LLM tier even when same")
        self.assertEqual(decision["source"], "llm", "Source should be LLM when LLM is valid")
        self.assertEqual(decision["adjudication_reason"], "llm_valid")
        self.assertEqual(decision["llm"], "assisted_living")
        self.assertEqual(decision["det"], "assisted_living")

    def test_confidence_ignored(self):
        """Test that confidence does not affect decision - only validity."""
        # Low confidence but valid LLM tier should still win
        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers=self.allowed_tiers,
            llm_tier="in_home",
            llm_conf=0.20,  # Very low confidence
            bands=self.bands,
            risky=False
        )

        self.assertEqual(final_tier, "in_home", "LLM should win regardless of low confidence")
        self.assertEqual(decision["source"], "llm")
        self.assertEqual(decision["adjudication_reason"], "llm_valid")

    def test_edge_case_double_missing(self):
        """Test edge case where both LLM and deterministic are missing."""
        final_tier, decision = _choose_final_tier(
            det_tier=None,  # Missing
            allowed_tiers=self.allowed_tiers,
            llm_tier=None,  # Missing
            llm_conf=None,
            bands=self.bands,
            risky=False
        )

        self.assertEqual(final_tier, "assisted_living", "Should default to safe fallback")
        self.assertEqual(decision["source"], "fallback")
        self.assertEqual(decision["adjudication_reason"], "double_missing_default")

    def test_unrecognized_llm_tier(self):
        """Test LLM returning unrecognized tier label."""
        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers=self.allowed_tiers,
            llm_tier="skilled_nursing",  # Not a recognized tier
            llm_conf=0.85,
            bands=self.bands,
            risky=False
        )

        self.assertEqual(final_tier, "assisted_living", "Should fallback when LLM tier unrecognized")
        self.assertEqual(decision["source"], "fallback")
        self.assertEqual(decision["adjudication_reason"], "llm_invalid_guard")

    @patch('streamlit.session_state', {})
    def test_partner_independent_llm_first(self):
        """Test partner adjudication is independent and follows LLM-first."""

        # Test primary person - LLM valid
        primary_tier, primary_decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers={"assisted_living", "memory_care"},
            llm_tier="memory_care",  # Valid LLM
            llm_conf=0.80,
            bands=self.bands,
            risky=False
        )

        # Test partner - LLM invalid (not in allowed)
        partner_tier, partner_decision = _choose_final_tier(
            det_tier="in_home",
            allowed_tiers={"in_home", "assisted_living"},  # No memory_care allowed
            llm_tier="memory_care",  # Invalid for partner
            llm_conf=0.85,
            bands=self.bands,
            risky=False
        )

        # Verify primary uses LLM
        self.assertEqual(primary_tier, "memory_care")
        self.assertEqual(primary_decision["source"], "llm")

        # Verify partner falls back to deterministic
        self.assertEqual(partner_tier, "in_home")
        self.assertEqual(partner_decision["source"], "fallback")
        self.assertEqual(partner_decision["adjudication_reason"], "llm_invalid_guard")

    def test_careplan_metadata_fields(self):
        """Test that CarePlan model accepts new adjudication metadata fields."""
        cp = CarePlan(
            person_id="test_person",
            det_tier="assisted_living",
            llm_tier="memory_care",
            final_tier="memory_care",
            source="llm",
            alt_tier="assisted_living",
            llm_confidence=0.85,
            adjudication_reason="llm_valid"
        )

        # Verify all fields are set correctly
        self.assertEqual(cp.source, "llm")
        self.assertEqual(cp.alt_tier, "assisted_living")
        self.assertEqual(cp.llm_confidence, 0.85)
        self.assertEqual(cp.adjudication_reason, "llm_valid")
        self.assertEqual(cp.det_tier, "assisted_living")
        self.assertEqual(cp.llm_tier, "memory_care")
        self.assertEqual(cp.final_tier, "memory_care")

    def test_careplan_metadata_optional(self):
        """Test that new CarePlan fields are optional (non-breaking)."""
        # Should work without new fields
        cp = CarePlan(
            person_id="test_person",
            det_tier="assisted_living",
            final_tier="assisted_living"
        )

        # New fields should be None by default
        self.assertIsNone(cp.source)
        self.assertIsNone(cp.alt_tier)
        self.assertIsNone(cp.llm_confidence)
        self.assertIsNone(cp.adjudication_reason)

    def test_decision_info_structure(self):
        """Test that decision info contains all required fields."""
        final_tier, decision = _choose_final_tier(
            det_tier="assisted_living",
            allowed_tiers=self.allowed_tiers,
            llm_tier="memory_care",
            llm_conf=0.85,
            bands=self.bands,
            risky=True
        )

        # Verify all required fields are present
        required_fields = ["det", "llm", "conf", "allowed", "bands", "risky",
                          "reason", "source", "adjudication_reason"]

        for field in required_fields:
            self.assertIn(field, decision, f"Decision missing required field: {field}")

        # Verify field types and values
        self.assertIsInstance(decision["allowed"], list)
        self.assertIsInstance(decision["bands"], dict)
        self.assertIsInstance(decision["risky"], bool)
        self.assertIn(decision["source"], ["llm", "fallback"])


if __name__ == "__main__":
    print("🧪 Testing GCP Adjudication Simplification — LLM-First, Deterministic Fallback")
    print("=" * 80)

    # Run the tests
    unittest.main(verbosity=2)
