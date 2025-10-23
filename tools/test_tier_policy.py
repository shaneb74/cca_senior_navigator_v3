#!/usr/bin/env python3
"""
Quick test of the guarded LLM tier replacement policy.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from products.gcp_v4.modules.care_recommendation.logic import _choose_final_tier

def test_tier_policy():
    """Test various scenarios of the tier replacement policy."""
    
    # Test 1: LLM tier not in allowed set -> keep deterministic
    det_tier = "memory_care"
    allowed = {"assisted_living", "in_home"}
    llm_tier = "memory_care"
    llm_conf = 0.85
    bands = {"cog": "moderate", "sup": "high"}
    risky = False
    
    final, info = _choose_final_tier(det_tier, allowed, llm_tier, llm_conf, bands, risky)
    assert final == det_tier, f"Expected {det_tier}, got {final}"
    assert info["reason"] == "llm_tier_not_allowed"
    print(f"✓ Test 1 passed: LLM tier not allowed -> keep det")
    
    # Test 2: Risky behaviors + MC det -> keep MC even if LLM says AL
    det_tier = "memory_care"
    allowed = {"memory_care", "memory_care_high_acuity", "assisted_living"}
    llm_tier = "assisted_living"
    llm_conf = 0.85
    bands = {"cog": "severe", "sup": "high"}
    risky = True
    
    final, info = _choose_final_tier(det_tier, allowed, llm_tier, llm_conf, bands, risky)
    assert final == det_tier, f"Expected {det_tier}, got {final}"
    assert info["reason"] == "risky_behaviors_keep_det"
    print(f"✓ Test 2 passed: Risky behaviors -> keep MC")
    
    # Test 3: De-overscore scenario: moderate×high, no risky, det=MC, llm=AL with conf≥0.80
    det_tier = "memory_care"
    allowed = {"assisted_living", "in_home"}  # Gates removed MC
    llm_tier = "assisted_living"
    llm_conf = 0.85
    bands = {"cog": "moderate", "sup": "high"}
    risky = False
    
    final, info = _choose_final_tier(det_tier, allowed, llm_tier, llm_conf, bands, risky)
    assert final == llm_tier, f"Expected {llm_tier}, got {final}"
    assert info["reason"] == "de_overscore_accept_al"
    print(f"✓ Test 3 passed: De-overscore accepts AL")
    
    # Test 4: General confident acceptance
    det_tier = "in_home"
    allowed = {"in_home", "assisted_living"}
    llm_tier = "assisted_living"
    llm_conf = 0.90
    bands = {"cog": "mild", "sup": "moderate"}
    risky = False
    
    final, info = _choose_final_tier(det_tier, allowed, llm_tier, llm_conf, bands, risky)
    assert final == llm_tier, f"Expected {llm_tier}, got {final}"
    assert info["reason"] == "confident_llm_accept"
    print(f"✓ Test 4 passed: Confident LLM accepted")
    
    # Test 5: Low confidence -> keep deterministic
    det_tier = "in_home"
    allowed = {"in_home", "assisted_living"}
    llm_tier = "assisted_living"
    llm_conf = 0.65
    bands = {"cog": "mild", "sup": "moderate"}
    risky = False
    
    final, info = _choose_final_tier(det_tier, allowed, llm_tier, llm_conf, bands, risky)
    assert final == det_tier, f"Expected {det_tier}, got {final}"
    assert info["reason"] == "deterministic"
    print(f"✓ Test 5 passed: Low confidence -> keep det")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_tier_policy()
