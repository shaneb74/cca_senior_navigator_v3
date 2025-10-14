"""
GCP v4 logic adapter - Wraps existing GCP v3 scoring logic for MCIP integration.

This module adapts the proven GCP v3 scoring engine to return CareRecommendation-compatible
output while preserving all existing scoring logic, overrides, and domain calculations.
"""

from typing import Dict, Any, List, Tuple
from .flags import build_flags


# Import the proven v3 scoring logic
import sys
from pathlib import Path

# Add parent gcp module to path to import v3 logic
gcp_v3_path = Path(__file__).parent.parent.parent.parent / "gcp" / "modules" / "care_recommendation"
sys.path.insert(0, str(gcp_v3_path))

try:
    from logic import derive_outcome as derive_outcome_v3
finally:
    sys.path.pop(0)


# Tier name mapping for MCIP
TIER_NAME_MAPPING = {
    "Independent / In-Home": "independent",
    "In-Home Care": "in_home",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "High-Acuity Memory Care": "memory_care"
}


def derive_outcome(answers: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Compute care recommendation using GCP v3 logic, output MCIP-compatible format.
    
    This function:
    1. Calls the proven GCP v3 scoring engine
    2. Transforms OutcomeContract to CareRecommendation-compatible dict
    3. Maps tier names to MCIP tier keys
    4. Converts flags to structured format with CTAs
    
    Args:
        answers: User responses from module.json questions
        config: Optional configuration (passed to v3 logic)
    
    Returns:
        Dict matching CareRecommendation dataclass schema:
        - tier: str (independent | in_home | assisted_living | memory_care)
        - tier_score: float
        - tier_rankings: List[Tuple[str, float]]
        - confidence: float
        - flags: List[Dict]
        - rationale: List[str]
        - suggested_next_product: str
    """
    
    # Call GCP v3 scoring engine
    outcome = derive_outcome_v3(answers, config or {})
    
    # Extract data from OutcomeContract
    recommendation = outcome.recommendation
    confidence = outcome.confidence
    flags_dict = outcome.flags
    domain_scores = outcome.domain_scores
    summary = outcome.summary
    
    # Map tier name to MCIP tier key
    tier = TIER_NAME_MAPPING.get(recommendation, "in_home")
    
    # Get tier score from summary
    tier_score = summary.get("total_score", 0.0)
    
    # Build tier rankings (all tiers with their scores)
    # For v4, we'll use domain scores as proxy since v3 doesn't rank all tiers
    tier_rankings = _build_tier_rankings(tier, tier_score, domain_scores)
    
    # Build rationale from summary points
    rationale = _build_rationale(summary, domain_scores, answers)
    
    # Convert flags to structured format
    flag_ids = _extract_flag_ids(flags_dict, answers, summary)
    flags = build_flags(flag_ids)
    
    # Determine suggested next product
    suggested_next = _determine_next_product(tier, confidence)
    
    return {
        "tier": tier,
        "tier_score": round(tier_score, 1),
        "tier_rankings": tier_rankings,
        "confidence": round(confidence, 2),
        "flags": flags,
        "rationale": rationale,
        "suggested_next_product": suggested_next
    }


def _build_tier_rankings(winning_tier: str, winning_score: float, domain_scores: Dict) -> List[Tuple[str, float]]:
    """Build tier rankings with all tiers scored.
    
    Since v3 logic doesn't score all tiers, we approximate based on domain scores
    and the winning tier. This provides context for why other tiers weren't recommended.
    
    Args:
        winning_tier: The recommended tier
        winning_score: Score for recommended tier
        domain_scores: Domain-level scores from v3
    
    Returns:
        List of (tier_name, score) tuples sorted by score
    """
    # Create scores for all tiers
    all_tiers = ["independent", "in_home", "assisted_living", "memory_care"]
    
    # Start with winning tier
    rankings = [(winning_tier, winning_score)]
    
    # Approximate other tier scores based on domain scores
    # This is a simplified heuristic for display purposes
    for tier in all_tiers:
        if tier != winning_tier:
            # Lower tiers get progressively lower scores
            if tier == "independent":
                score = winning_score * 0.3
            elif tier == "in_home":
                score = winning_score * 0.5 if winning_tier in ["assisted_living", "memory_care"] else winning_score * 0.7
            elif tier == "assisted_living":
                score = winning_score * 0.7 if winning_tier == "memory_care" else winning_score * 0.5
            else:  # memory_care
                score = winning_score * 0.8 if winning_tier == "assisted_living" else winning_score * 0.4
            
            rankings.append((tier, round(score, 1)))
    
    # Sort by score descending
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    return rankings


def _build_rationale(summary: Dict, domain_scores: Dict, answers: Dict) -> List[str]:
    """Build human-readable rationale from scoring summary.
    
    Args:
        summary: Summary dict from v3 outcome
        domain_scores: Domain scores from v3
        answers: User answers
    
    Returns:
        List of rationale strings (key drivers of recommendation)
    """
    rationale = []
    
    # Start with summary points if available
    if "points" in summary and isinstance(summary["points"], list):
        rationale.extend(summary["points"][:5])  # Top 5 points
    
    # Add high-scoring domains
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    for domain, score in sorted_domains[:3]:  # Top 3 domains
        if score > 5:  # Only significant domains
            domain_label = domain.replace("_", " ").title()
            rationale.append(f"{domain_label}: {score} points")
    
    # Add override reason if present
    if "override_reason" in summary and summary["override_reason"]:
        rationale.insert(0, summary["override_reason"])
    
    return rationale[:6]  # Keep top 6 items


def _extract_flag_ids(flags_dict: Dict, answers: Dict, summary: Dict) -> List[str]:
    """Extract flag IDs from v3 flags dict and answers.
    
    Args:
        flags_dict: Flags from v3 outcome
        answers: User answers
        summary: Summary from v3 outcome
    
    Returns:
        List of flag IDs
    """
    flag_ids = []
    
    # Extract from v3 flags dict
    for key, value in flags_dict.items():
        if value is True:
            # Map v3 flag keys to v4 flag IDs
            if "fall" in key.lower():
                flag_ids.append("falls_risk")
            elif "memory" in key.lower() or "cognitive" in key.lower():
                flag_ids.append("memory_support")
            elif "behavior" in key.lower():
                flag_ids.append("behavioral_concerns")
            elif "medication" in key.lower() or "med" in key.lower():
                flag_ids.append("medication_management")
            elif "isolation" in key.lower() or "alone" in key.lower():
                flag_ids.append("isolation_risk")
            elif "adl" in key.lower():
                flag_ids.append("adl_support_high")
            elif "mobility" in key.lower():
                flag_ids.append("mobility_limited")
            elif "chronic" in key.lower() or "health" in key.lower():
                flag_ids.append("chronic_conditions")
            elif "safety" in key.lower():
                flag_ids.append("safety_concerns")
            elif "caregiver" in key.lower():
                flag_ids.append("caregiver_stress")
    
    # Deduplicate
    return list(set(flag_ids))


def _determine_next_product(tier: str, confidence: float) -> str:
    """Determine suggested next product based on tier and confidence.
    
    Args:
        tier: Recommended care tier
        confidence: Recommendation confidence
    
    Returns:
        Product key for suggested next step
    """
    if confidence < 0.7:
        return "gcp"  # Need more information
    else:
        return "cost_planner"  # Ready for cost estimation


# Backward compatibility alias
compute = derive_outcome
