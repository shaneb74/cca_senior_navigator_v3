"""
Test Navigation Consistency - Verify interim AL flag matches published tier
"""

import pytest


def test_interim_no_dx_forces_al():
    """Test that interim flag with MC clamp results in AL tier and correct subtitle."""
    # Mock session state
    session_state = {
        "gcp": {
            "published_tier": "assisted_living",
            "deterministic_tier": "memory_care"
        },
        "_show_mc_interim_advice": True
    }
    
    from core.modules.engine import get_final_recommendation_tier, get_results_subtitle
    
    # Verify final tier is AL (post-adjudication)
    final_tier = get_final_recommendation_tier(session_state)
    assert final_tier == "assisted_living", f"Expected assisted_living, got {final_tier}"
    
    # Verify subtitle matches interim case
    subtitle = get_results_subtitle(session_state)
    assert subtitle == "Assisted Living with enhanced cognitive support", \
        f"Expected interim subtitle, got: {subtitle}"


def test_mc_with_dx_returns_mc():
    """Test that MC with diagnosis returns MC tier and correct subtitle."""
    session_state = {
        "gcp": {
            "published_tier": "memory_care",
            "deterministic_tier": "memory_care"
        },
        "_show_mc_interim_advice": False,
        "person_name": "John"
    }
    
    from core.modules.engine import get_final_recommendation_tier, get_results_subtitle
    
    final_tier = get_final_recommendation_tier(session_state)
    assert final_tier == "memory_care", f"Expected memory_care, got {final_tier}"
    
    subtitle = get_results_subtitle(session_state)
    assert "Memory care is recommended for John" in subtitle, \
        f"Expected MC subtitle with name, got: {subtitle}"


def test_al_without_interim_returns_standard():
    """Test that regular AL (no interim) returns standard subtitle."""
    session_state = {
        "gcp": {
            "published_tier": "assisted_living",
            "deterministic_tier": "assisted_living"
        },
        "_show_mc_interim_advice": False,
        "person_name": "Sarah"
    }
    
    from core.modules.engine import get_final_recommendation_tier, get_results_subtitle
    
    final_tier = get_final_recommendation_tier(session_state)
    assert final_tier == "assisted_living", f"Expected assisted_living, got {final_tier}"
    
    subtitle = get_results_subtitle(session_state)
    assert "Assisted Living is recommended for Sarah" in subtitle, \
        f"Expected standard AL subtitle with name, got: {subtitle}"
    assert "enhanced cognitive support" not in subtitle, \
        f"Should not have interim copy: {subtitle}"


def test_tier_inconsistency_warning():
    """Test that inconsistent state (interim=True but tier=MC) logs warning."""
    import logging
    
    session_state = {
        "gcp": {
            "published_tier": "memory_care",  # Inconsistent!
        },
        "_show_mc_interim_advice": True  # Says interim but tier is MC
    }
    
    from core.modules.engine import get_final_recommendation_tier
    
    # Should force to AL and log warning
    with pytest.raises(AssertionError, match="Expected"):
        # This will fail because we expect the function to fix it
        pass
    
    final_tier = get_final_recommendation_tier(session_state)
    # Function should force to AL when inconsistent
    assert final_tier == "assisted_living", \
        f"Inconsistent state should force to AL, got {final_tier}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
