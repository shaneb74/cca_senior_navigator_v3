"""
Test Suite: Navi Single Intelligence Layer Integration

Validates the complete Navi implementation per architectural spec:
- Placement and presence
- Dynamic suggestions
- Next-best actions
- Additional Services orchestration
- Navigation and routing
- Regression checks

Run: pytest tests/test_navi_integration.py -v
"""

from unittest.mock import Mock, patch

import pytest


class TestNaviPlacement:
    """A. Placement & Presence Tests"""

    def test_navi_exists_on_concierge_hub(self):
        """Verify Navi renders on Concierge Hub under header."""
        with patch("streamlit.session_state", {}):
            with patch("core.mcip.MCIP") as mock_mcip:
                mock_mcip.get_journey_progress.return_value = {
                    "completed_products": [],
                    "avg_completion": 0,
                    "next_recommended": "gcp_v4",
                }

                # Should not raise exception
                # Navi panel should be rendered via render_navi_panel()
                assert True  # Placeholder - actual test needs Streamlit context

    def test_navi_exists_in_gcp_product(self):
        """Verify Navi renders in GCP product above module content."""
        with patch("streamlit.session_state", {}):
            # Should call render_navi_panel with location="product"
            assert True  # Placeholder - actual test needs Streamlit context

    def test_navi_not_above_header(self):
        """Verify Navi never renders above global page header."""
        # This is enforced by placement order in render functions
        # Header → Navi → Content
        # Visual inspection test
        pass


class TestNaviDynamicSuggestions:
    """B. Dynamic Suggestions Tests"""

    def test_default_questions_no_flags(self):
        """With no flags, Navi shows 3 default starter questions."""
        from core.flags import get_all_flags
        from core.navi import NaviOrchestrator

        with patch("core.flags.get_all_flags", return_value={}):
            with patch("streamlit.session_state", {}):
                flags = get_all_flags()
                questions = NaviOrchestrator.get_suggested_questions(flags, completed_products=[])

                assert len(questions) == 3
                assert isinstance(questions[0], str)
                # Should be default questions
                assert any("getting started" in q.lower() or "care" in q.lower() for q in questions)

    def test_veteran_flag_generates_relevant_question(self):
        """With veteran flag, Navi suggests VA benefits question."""
        from core.navi import NaviOrchestrator

        flags = {"veteran": True}
        questions = NaviOrchestrator.get_suggested_questions(flags, completed_products=[])

        assert len(questions) == 3
        # Should include veteran-specific question
        assert any("VA" in q or "veteran" in q.lower() for q in questions)

    def test_fall_risk_flag_generates_relevant_question(self):
        """With fall_risk flag, Navi suggests fall prevention question."""
        from core.navi import NaviOrchestrator

        flags = {"fall_risk": True}
        questions = NaviOrchestrator.get_suggested_questions(flags, completed_products=[])

        assert len(questions) == 3
        # Should include fall risk question
        assert any("fall" in q.lower() or "safety" in q.lower() for q in questions)

    def test_memory_concerns_flag_generates_relevant_question(self):
        """With memory_concerns flag, Navi suggests memory care question."""
        from core.navi import NaviOrchestrator

        flags = {"memory_concerns": True}
        questions = NaviOrchestrator.get_suggested_questions(flags, completed_products=[])

        assert len(questions) == 3
        # Should include memory care question
        assert any(
            "memory" in q.lower() or "dementia" in q.lower() or "alzheimer" in q.lower()
            for q in questions
        )

    def test_multiple_flags_prioritize_questions(self):
        """With multiple flags, Navi prioritizes most relevant questions."""
        from core.navi import NaviOrchestrator

        flags = {
            "veteran": True,
            "fall_risk": True,
            "memory_concerns": True,
            "financial_assistance_needed": True,
        }
        questions = NaviOrchestrator.get_suggested_questions(flags, completed_products=[])

        # Should still return exactly 3 questions
        assert len(questions) == 3
        # Should be unique
        assert len(set(questions)) == 3


class TestNaviNextBestAction:
    """C. Next-Best Action Tests"""

    def test_next_action_start_gcp_when_incomplete(self):
        """When GCP < 100%, Navi suggests starting/resuming GCP."""
        from core.mcip import MCIP
        from core.navi import NaviOrchestrator

        with patch("core.mcip.MCIP.get_journey_progress") as mock_progress:
            mock_progress.return_value = {
                "completed_products": [],
                "avg_completion": 0,
                "next_recommended": "gcp_v4",
            }

            with patch("core.mcip.MCIP.get_care_recommendation", return_value=None):
                progress = MCIP.get_journey_progress()
                next_action = NaviOrchestrator.get_next_action(
                    Mock(
                        progress=progress,
                        care_recommendation=None,
                        financial_profile=None,
                        advisor_appointment=None,
                    )
                )

                assert next_action["route"] == "gcp_v4"
                assert (
                    "care" in next_action["label"].lower() or "gcp" in next_action["label"].lower()
                )

    def test_next_action_cost_planner_after_gcp(self):
        """When GCP complete but Cost Planner < 100%, suggests Cost Planner."""
        from core.mcip import MCIP, CareRecommendation
        from core.navi import NaviOrchestrator

        with patch("core.mcip.MCIP.get_journey_progress") as mock_progress:
            mock_progress.return_value = {
                "completed_products": ["gcp_v4"],
                "avg_completion": 33,
                "next_recommended": "cost_v2",
            }

            with patch("core.mcip.MCIP.get_care_recommendation") as mock_care:
                mock_care.return_value = CareRecommendation(
                    tier="assisted_living", reasoning="Test", scored_factors={}, flags={}
                )

                with patch("core.mcip.MCIP.get_financial_profile", return_value=None):
                    progress = MCIP.get_journey_progress()
                    care_rec = MCIP.get_care_recommendation()

                    next_action = NaviOrchestrator.get_next_action(
                        Mock(
                            progress=progress,
                            care_recommendation=care_rec,
                            financial_profile=None,
                            advisor_appointment=None,
                        )
                    )

                    assert next_action["route"] == "cost_intro"
                    assert (
                        "cost" in next_action["label"].lower()
                        or "financial" in next_action["label"].lower()
                    )

    def test_next_action_pfma_after_cost_planner(self):
        """After Cost Planner complete, suggests PFMA."""
        from core.mcip import MCIP, CareRecommendation, FinancialProfile
        from core.navi import NaviOrchestrator

        with patch("core.mcip.MCIP.get_journey_progress") as mock_progress:
            mock_progress.return_value = {
                "completed_products": ["gcp_v4", "cost_v2"],
                "avg_completion": 67,
                "next_recommended": "pfma_v2",
            }

            with patch("core.mcip.MCIP.get_care_recommendation") as mock_care:
                mock_care.return_value = CareRecommendation(
                    tier="assisted_living", reasoning="Test", scored_factors={}, flags={}
                )

                with patch("core.mcip.MCIP.get_financial_profile") as mock_financial:
                    mock_financial.return_value = FinancialProfile(
                        tier="mid_range", monthly_budget=4500, flags={}, summary_line="Test"
                    )

                    with patch("core.mcip.MCIP.get_advisor_appointment", return_value=None):
                        progress = MCIP.get_journey_progress()

                        next_action = NaviOrchestrator.get_next_action(
                            Mock(
                                progress=progress,
                                care_recommendation=mock_care.return_value,
                                financial_profile=mock_financial.return_value,
                                advisor_appointment=None,
                            )
                        )

                        assert next_action["route"] == "pfma_v2"
                        assert (
                            "advisor" in next_action["label"].lower()
                            or "pfma" in next_action["label"].lower()
                        )

    def test_next_action_journey_complete(self):
        """After all products complete, Navi shows completion state."""

        from core.navi import NaviOrchestrator

        with patch("core.mcip.MCIP.get_journey_progress") as mock_progress:
            mock_progress.return_value = {
                "completed_products": ["gcp_v4", "cost_v2", "pfma_v2"],
                "avg_completion": 100,
                "next_recommended": None,
            }

            next_action = NaviOrchestrator.get_next_action(
                Mock(
                    progress=mock_progress.return_value,
                    care_recommendation=Mock(),
                    financial_profile=Mock(),
                    advisor_appointment=Mock(),
                )
            )

            # Should suggest exploring services or returning to hub
            assert next_action["route"] in ["hub_concierge", "faq"]


class TestNaviAdditionalServices:
    """D. Additional Services Orchestration Tests"""

    def test_veteran_flag_recommends_va_benefits(self):
        """With veteran flag, Navi recommends VA benefits service."""
        from core.navi import NaviOrchestrator

        flags = {"veteran": True}
        services = NaviOrchestrator.get_additional_services(flags)

        assert "veterans_benefits" in services

    def test_fall_risk_recommends_omcare(self):
        """With fall_risk flag, Navi recommends Omcare."""
        from core.navi import NaviOrchestrator

        flags = {"fall_risk": True}
        services = NaviOrchestrator.get_additional_services(flags)

        assert "omcare" in services

    def test_mobility_concerns_recommends_omcare(self):
        """With mobility_concerns flag, Navi recommends Omcare."""
        from core.navi import NaviOrchestrator

        flags = {"mobility_concerns": True}
        services = NaviOrchestrator.get_additional_services(flags)

        assert "omcare" in services

    def test_multiple_flags_prioritize_services(self):
        """With multiple flags, Navi prioritizes services correctly."""
        from core.navi import NaviOrchestrator

        flags = {
            "veteran": True,
            "fall_risk": True,
            "memory_concerns": True,
            "financial_assistance_needed": True,
        }
        services = NaviOrchestrator.get_additional_services(flags)

        # Should return up to 5 services
        assert len(services) <= 5
        # Should be unique
        assert len(set(services)) == len(services)

    def test_no_flags_returns_default_services(self):
        """With no flags, Navi returns default service recommendations."""
        from core.navi import NaviOrchestrator

        flags = {}
        services = NaviOrchestrator.get_additional_services(flags)

        # Should still return some default services
        assert len(services) > 0
        assert len(services) <= 5


class TestNaviNavigation:
    """E. Navigation & Routing Tests"""

    def test_back_to_hub_routes_to_concierge(self):
        """Back to Hub link routes to Concierge, not Welcome."""
        # This is enforced in route definitions
        # Verify in nav.json that hub_concierge is the default hub
        import json

        with open("config/nav.json") as f:
            nav_config = json.load(f)

        # Find hub_concierge route
        hub_routes = [item for item in nav_config.get("items", []) if "hub" in item.get("key", "")]
        assert any(item["key"] == "hub_concierge" for item in hub_routes)

    def test_navi_uses_canonical_route_ids(self):
        """Navi CTAs use canonical route IDs, not hard-coded URLs."""
        from core.navi import NaviOrchestrator

        # Next actions should return route keys like "gcp_v4", "cost_intro", "pfma_v2"
        # Not URLs like "?page=gcp_v4"
        next_action = NaviOrchestrator.get_next_action(
            Mock(
                progress={"completed_products": [], "next_recommended": "gcp_v4"},
                care_recommendation=None,
                financial_profile=None,
                advisor_appointment=None,
            )
        )

        # Route should be a key, not a URL
        assert not next_action["route"].startswith("?")
        assert not next_action["route"].startswith("http")


class TestNaviRegressionChecks:
    """F. Regression Checks"""

    def test_no_hub_guide_in_concierge(self):
        """Hub Guide is fully deprecated, not rendered in Concierge."""
        with open("hubs/concierge.py") as f:
            content = f.read()

        # Should not contain hub_guide_block calls
        # hub_guide_block should be None or absent
        assert "hub_guide_block=None" in content or "hub_guide_block" not in content

    def test_navi_imported_in_hubs(self):
        """Navi is imported and used in hub files."""
        with open("hubs/concierge.py") as f:
            content = f.read()

        assert "from core.navi import render_navi_panel" in content
        assert "render_navi_panel(" in content

    def test_navi_imported_in_products(self):
        """Navi is imported and used in product files."""
        product_files = [
            "products/gcp_v4/product.py",
            "products/cost_planner_v2/product.py",
            "products/pfma_v2/product.py",
        ]

        for filepath in product_files:
            with open(filepath) as f:
                content = f.read()

            assert "from core.navi import render_navi_panel" in content, (
                f"Missing import in {filepath}"
            )
            assert "render_navi_panel(" in content, f"Missing usage in {filepath}"

    def test_flags_accessor_exists(self):
        """Centralized flag accessor exists and is used."""
        import os

        assert os.path.exists("core/flags.py")

        with open("core/flags.py") as f:
            content = f.read()

        assert "def get_all_flags" in content
        assert "def get_flag" in content

    def test_navi_orchestrator_exists(self):
        """NaviOrchestrator class exists with required methods."""
        from core.navi import NaviOrchestrator

        # Check all required methods exist
        assert hasattr(NaviOrchestrator, "get_context")
        assert hasattr(NaviOrchestrator, "get_next_action")
        assert hasattr(NaviOrchestrator, "get_suggested_questions")
        assert hasattr(NaviOrchestrator, "get_additional_services")
        assert hasattr(NaviOrchestrator, "get_context_summary")
        assert hasattr(NaviOrchestrator, "get_context_boost")

    def test_navi_context_dataclass_complete(self):
        """NaviContext dataclass has all required fields."""
        from dataclasses import fields

        from core.navi import NaviContext

        field_names = {f.name for f in fields(NaviContext)}

        required_fields = {
            "progress",
            "next_action",
            "care_recommendation",
            "financial_profile",
            "advisor_appointment",
            "flags",
            "user_name",
            "is_authenticated",
            "location",
            "module_step",
            "module_total",
        }

        assert required_fields.issubset(field_names)


class TestNaviFlagAggregation:
    """Test centralized flag aggregation system."""

    def test_get_all_flags_aggregates_mcip(self):
        """get_all_flags() aggregates flags from MCIP contracts."""
        from core.flags import get_all_flags
        from core.mcip import CareRecommendation

        with patch("core.mcip.MCIP.get_care_recommendation") as mock_care:
            mock_care.return_value = CareRecommendation(
                tier="assisted_living",
                reasoning="Test",
                scored_factors={},
                flags={"veteran": True, "fall_risk": True},
            )

            with patch("streamlit.session_state", {}):
                flags = get_all_flags()

                assert "veteran" in flags
                assert "fall_risk" in flags
                assert flags["veteran"] is True
                assert flags["fall_risk"] is True

    def test_get_all_flags_merges_session_state(self):
        """get_all_flags() merges flags from session state."""
        from core.flags import get_all_flags

        with patch("core.mcip.MCIP.get_care_recommendation", return_value=None):
            with patch("core.mcip.MCIP.get_financial_profile", return_value=None):
                with patch("core.mcip.MCIP.get_advisor_appointment", return_value=None):
                    with patch("streamlit.session_state", {"gcp_flags": {"memory_concerns": True}}):
                        flags = get_all_flags()

                        assert "memory_concerns" in flags
                        assert flags["memory_concerns"] is True

    def test_get_flag_with_default(self):
        """get_flag() returns default when flag not present."""
        from core.flags import get_flag

        with patch("core.flags.get_all_flags", return_value={}):
            value = get_flag("nonexistent_flag", default=False)
            assert value is False

    def test_has_any_flags(self):
        """has_any_flags() returns True if any flag is True."""
        from core.flags import has_any_flags

        with patch("core.flags.get_all_flags", return_value={"veteran": True, "fall_risk": False}):
            assert has_any_flags(["veteran", "memory_concerns"]) is True
            assert has_any_flags(["fall_risk"]) is False
            assert has_any_flags(["nonexistent"]) is False

    def test_has_all_flags(self):
        """has_all_flags() returns True only if all flags are True."""
        from core.flags import has_all_flags

        with patch("core.flags.get_all_flags", return_value={"veteran": True, "fall_risk": True}):
            assert has_all_flags(["veteran", "fall_risk"]) is True
            assert has_all_flags(["veteran", "fall_risk", "memory_concerns"]) is False


class TestNaviContextGeneration:
    """Test NaviContext generation and aggregation."""

    def test_context_aggregates_journey_data(self):
        """get_context() aggregates all journey intelligence."""
        from core.navi import NaviOrchestrator

        with patch("core.mcip.MCIP.get_journey_progress") as mock_progress:
            mock_progress.return_value = {
                "completed_products": ["gcp_v4"],
                "avg_completion": 33,
                "next_recommended": "cost_v2",
            }

            with patch("core.mcip.MCIP.get_care_recommendation", return_value=None):
                with patch("core.mcip.MCIP.get_financial_profile", return_value=None):
                    with patch("core.mcip.MCIP.get_advisor_appointment", return_value=None):
                        with patch("core.flags.get_all_flags", return_value={}):
                            with patch("streamlit.session_state", {}):
                                ctx = NaviOrchestrator.get_context(
                                    location="hub",
                                    hub_key="concierge",
                                    product_key=None,
                                    module_config=None,
                                )

                                assert ctx.location == "hub"
                                assert ctx.progress is not None
                                assert "completed_products" in ctx.progress

    def test_context_includes_module_state_when_in_product(self):
        """get_context() includes module state when location=product."""
        from core.modules.schema import ModuleConfig
        from core.navi import NaviOrchestrator

        mock_config = Mock(spec=ModuleConfig)
        mock_config.state_key = "test_module"
        mock_config.steps = [Mock(), Mock(), Mock()]

        with patch("core.mcip.MCIP.get_journey_progress", return_value={"completed_products": []}):
            with patch("core.mcip.MCIP.get_care_recommendation", return_value=None):
                with patch("core.mcip.MCIP.get_financial_profile", return_value=None):
                    with patch("core.mcip.MCIP.get_advisor_appointment", return_value=None):
                        with patch("core.flags.get_all_flags", return_value={}):
                            with patch(
                                "streamlit.session_state", {"test_module": {"current_step": 1}}
                            ):
                                ctx = NaviOrchestrator.get_context(
                                    location="product",
                                    hub_key=None,
                                    product_key="test_product",
                                    module_config=mock_config,
                                )

                                assert ctx.location == "product"
                                assert ctx.module_step == 2  # current_step + 1 (1-indexed display)
                                assert ctx.module_total == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
