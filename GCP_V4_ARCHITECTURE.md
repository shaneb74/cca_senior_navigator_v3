# GCP v4 Architecture - MCIP Integration

> **Guided Care Plan v4**: Declarative, JSON-driven care recommendation engine that publishes to MCIP v2

---

## Executive Summary

GCP v4 maintains its **proven JSON-driven architecture** (questions + logic in swappable JSON files) while adding **clean MCIP integration** for the v2 system. The module engine already exists and works well - we're just adding a publishing layer.

**Core Principle**: Don't rebuild what works. Extend GCP's existing module to publish `CareRecommendation` contracts to MCIP.

---

## Current GCP Architecture (What We Keep)

### ✅ What Works Well

```
products/gcp/
├── modules/
│   └── care_recommendation/
│       ├── module.json          # Questions schema (swappable)
│       ├── logic.py              # Scoring logic (swappable)
│       └── config.py             # Converts JSON to ModuleConfig
└── product.py                    # Product router
```

**Existing Strengths:**
1. **Declarative questions** - `module.json` defines all questions, types, options
2. **Swappable logic** - `logic.py` can be replaced without touching UI
3. **Module engine integration** - Already uses `core/modules/engine.py`
4. **Type-safe** - Questions schema enforces data contracts

### Current Flow (v3)

```
User answers questions
    ↓
Module engine collects answers
    ↓
logic.py computes recommendation
    ↓
Stores in st.session_state["gcp"]["care_recommendation"]
    ↓
Products read GCP state directly ❌ (This is the problem)
```

---

## GCP v4 Changes (Minimal, Focused)

### What Changes

**Only 2 things change:**

1. **`logic.py` output format** - Returns dict that matches `CareRecommendation` schema
2. **`product.py` integration** - Publishes `CareRecommendation` to MCIP after module completes

### What Stays the Same

✅ `module.json` structure (questions schema)  
✅ Module engine integration  
✅ Question rendering  
✅ Navigation flow  
✅ Progress tracking  
✅ User experience  

---

## 1. Updated Data Flow (v4)

```
User answers questions
    ↓
Module engine collects answers
    ↓
logic.py computes recommendation (returns dict)
    ↓
product.py builds CareRecommendation contract
    ↓
product.py publishes to MCIP ✅
    ↓
MCIP fires events (mcip.recommendation.updated)
    ↓
Hubs/Products read from MCIP (not GCP state)
```

**Key Change**: Products now read `MCIP.get_care_recommendation()` instead of `st.session_state["gcp"]`

---

## 2. logic.py Contract (Updated)

### Current logic.py Output (v3)

```python
# products/gcp/modules/care_recommendation/logic.py (current)

def derive_outcome(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Compute care recommendation from answers."""
    
    # ... scoring logic ...
    
    return {
        "recommended_tier": "assisted_living",
        "confidence": 0.92,
        "summary": "Based on daily ADL needs...",
        # ... other fields
    }
```

### New logic.py Output (v4)

```python
# products/gcp_v4/modules/care_recommendation/logic.py (new)

def derive_outcome(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Compute care recommendation from answers.
    
    Returns dict that maps to CareRecommendation dataclass fields.
    The product layer will build the full CareRecommendation object.
    """
    
    # ... scoring logic (same as before) ...
    
    # Return dict matching CareRecommendation schema
    return {
        # Core recommendation
        "tier": winning_tier,                    # str: independent | in_home | assisted_living | memory_care
        "tier_score": winning_score,             # float: 0-100
        "tier_rankings": tier_rankings,          # List[Tuple[str, float]]: all tiers with scores
        "confidence": confidence,                # float: 0.0-1.0
        
        # Flags and rationale
        "flags": flags,                          # List[Dict]: risk/support flags
        "rationale": rationale,                  # List[str]: key reasons
        
        # Next step suggestion (optional, product can override)
        "suggested_next_product": "cost_planner"  # str: next product key
    }
```

**Changes:**
- ✅ Renamed `recommended_tier` → `tier` (matches dataclass)
- ✅ Added `tier_rankings` (all tiers with scores)
- ✅ Added `flags` list (structured flag objects)
- ✅ Added `rationale` list (bullet points explaining recommendation)
- ✅ Confidence stays same (0.0-1.0)

---

## 3. Flag Schema

### Flag Structure

```python
# Each flag in the flags list
{
    "id": "falls_risk",                    # Unique identifier
    "label": "High Fall Risk",             # Display name
    "description": "Recent falls or mobility challenges detected",
    "tone": "warning",                     # info | warning | critical
    "priority": 1,                         # Lower = higher priority
    "cta": {                               # Call to action (optional)
        "label": "See Safety Resources",
        "route": "learning",
        "filter": "fall_prevention"
    }
}
```

### Common Flags

```python
# products/gcp_v4/modules/care_recommendation/flags.py

FLAGS_SCHEMA = {
    "falls_risk": {
        "id": "falls_risk",
        "label": "High Fall Risk",
        "description": "2+ falls in the past year or significant mobility challenges",
        "tone": "warning",
        "priority": 1,
        "cta": {
            "label": "See Fall Prevention Resources",
            "route": "learning",
            "filter": "fall_prevention"
        }
    },
    "memory_support": {
        "id": "memory_support",
        "label": "Memory Care Needed",
        "description": "Alzheimer's or dementia diagnosis requiring specialized care",
        "tone": "critical",
        "priority": 0,
        "cta": {
            "label": "Find Memory Care Facilities",
            "route": "partners",
            "filter": "memory_care"
        }
    },
    "behavioral_concerns": {
        "id": "behavioral_concerns",
        "label": "Behavioral Support Required",
        "description": "Wandering, aggression, or other behaviors requiring specialized care",
        "tone": "critical",
        "priority": 0,
        "cta": {
            "label": "Find Specialized Facilities",
            "route": "partners",
            "filter": "behavioral_support"
        }
    },
    "medication_management": {
        "id": "medication_management",
        "label": "Medication Management Needed",
        "description": "Complex medication regimen requiring professional oversight",
        "tone": "warning",
        "priority": 2,
        "cta": {
            "label": "Learn About Med Management",
            "route": "learning",
            "filter": "medication"
        }
    },
    "isolation_risk": {
        "id": "isolation_risk",
        "label": "Social Isolation Risk",
        "description": "Living alone with limited social interaction",
        "tone": "info",
        "priority": 3,
        "cta": {
            "label": "Explore Social Programs",
            "route": "learning",
            "filter": "social_engagement"
        }
    }
}


def build_flag(flag_id: str) -> Dict[str, Any]:
    """Build a flag object from schema.
    
    Args:
        flag_id: Flag identifier
    
    Returns:
        Flag dict with all metadata
    """
    return FLAGS_SCHEMA.get(flag_id, {
        "id": flag_id,
        "label": flag_id.replace("_", " ").title(),
        "description": "",
        "tone": "info",
        "priority": 99,
        "cta": None
    })
```

---

## 4. Updated logic.py Implementation

```python
# products/gcp_v4/modules/care_recommendation/logic.py

from typing import Dict, Any, List, Tuple
from .flags import build_flag


def derive_outcome(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Compute care recommendation from user answers.
    
    This function:
    1. Scores each care tier based on answers
    2. Detects risk/support flags
    3. Generates rationale (key drivers)
    4. Returns dict matching CareRecommendation schema
    
    Args:
        answers: User responses from module.json questions
    
    Returns:
        Dict with tier, scores, confidence, flags, rationale
    """
    
    # Extract key answers
    adl_support = answers.get("adl_support_level")  # none | sometimes | daily | constant
    adl_tasks = answers.get("adl_tasks_needing_help", [])  # List of tasks
    falls_count = answers.get("falls_last_year", 0)
    mobility_level = answers.get("mobility_level")  # independent | walker | wheelchair
    memory_diagnosis = answers.get("memory_diagnosis")  # none | mild | moderate | severe
    behavioral_issues = answers.get("behavioral_issues", [])
    lives_alone = answers.get("lives_alone", False)
    supervision_hours = answers.get("supervision_hours_needed", 0)
    medication_count = answers.get("medication_count", 0)
    
    # Initialize tier scores
    scores = {
        "independent": 10,
        "in_home": 10,
        "assisted_living": 10,
        "memory_care": 10
    }
    
    rationale = []
    flag_ids = []
    
    # =========================================================================
    # ADL SUPPORT SCORING
    # =========================================================================
    
    if adl_support == "none":
        scores["independent"] += 30
        scores["in_home"] += 5
    elif adl_support == "sometimes":
        scores["independent"] += 15
        scores["in_home"] += 25
        scores["assisted_living"] += 10
        rationale.append("Needs occasional help with daily activities")
    elif adl_support == "daily":
        scores["in_home"] += 20
        scores["assisted_living"] += 35
        rationale.append("Needs help with daily activities")
    elif adl_support == "constant":
        scores["assisted_living"] += 40
        scores["memory_care"] += 30
        rationale.append("Requires around-the-clock support")
    
    # Specific ADL task analysis
    if len(adl_tasks) >= 3:
        scores["assisted_living"] += 15
        rationale.append(f"Needs help with {len(adl_tasks)} daily tasks")
    
    # =========================================================================
    # MOBILITY SCORING
    # =========================================================================
    
    if mobility_level == "wheelchair":
        scores["assisted_living"] += 20
        scores["memory_care"] += 15
        rationale.append("Requires wheelchair accessibility")
    elif mobility_level == "walker":
        scores["in_home"] += 10
        scores["assisted_living"] += 15
        rationale.append("Uses mobility aids")
    
    # Falls risk
    if falls_count >= 2:
        scores["assisted_living"] += 25
        scores["memory_care"] += 15
        flag_ids.append("falls_risk")
        rationale.append(f"{falls_count} falls in the past year")
    
    # =========================================================================
    # MEMORY/COGNITIVE SCORING
    # =========================================================================
    
    if memory_diagnosis in ["moderate", "severe", "alzheimers", "dementia"]:
        scores["memory_care"] += 50
        scores["assisted_living"] += 25
        flag_ids.append("memory_support")
        rationale.append("Memory care diagnosis requiring specialized support")
    elif memory_diagnosis == "mild":
        scores["assisted_living"] += 20
        scores["memory_care"] += 20
        rationale.append("Early-stage memory challenges")
    
    # =========================================================================
    # BEHAVIORAL SCORING
    # =========================================================================
    
    if behavioral_issues and len(behavioral_issues) > 0:
        if "wandering" in behavioral_issues or "aggression" in behavioral_issues:
            scores["memory_care"] += 40
            flag_ids.append("behavioral_concerns")
            rationale.append("Behavioral concerns requiring specialized care")
        else:
            scores["assisted_living"] += 15
    
    # =========================================================================
    # SUPERVISION & SAFETY SCORING
    # =========================================================================
    
    if supervision_hours >= 16:
        scores["assisted_living"] += 30
        scores["memory_care"] += 25
        rationale.append("Requires extensive daily supervision")
    elif supervision_hours >= 8:
        scores["in_home"] += 20
        scores["assisted_living"] += 20
    
    if lives_alone and supervision_hours > 0:
        scores["assisted_living"] += 20
        flag_ids.append("isolation_risk")
        rationale.append("Lives alone requiring supervision")
    
    # =========================================================================
    # MEDICATION MANAGEMENT SCORING
    # =========================================================================
    
    if medication_count >= 5:
        scores["assisted_living"] += 15
        flag_ids.append("medication_management")
        rationale.append(f"Manages {medication_count} medications daily")
    
    # =========================================================================
    # COMPUTE FINAL RECOMMENDATION
    # =========================================================================
    
    # Rank all tiers by score
    tier_rankings = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Winning tier
    winning_tier = tier_rankings[0][0]
    winning_score = tier_rankings[0][1]
    
    # Compute confidence (based on question coverage)
    required_questions = [
        "adl_support_level",
        "falls_last_year",
        "mobility_level",
        "memory_diagnosis",
        "lives_alone",
        "supervision_hours_needed"
    ]
    answered = sum(1 for q in required_questions if answers.get(q) is not None)
    confidence = answered / len(required_questions)
    
    # Build flags
    flags = [build_flag(flag_id) for flag_id in flag_ids]
    
    # Sort rationale by importance (keep top 5)
    rationale = rationale[:5]
    
    # Determine next step
    if confidence < 0.7:
        suggested_next = "gcp"  # Need more info
    else:
        suggested_next = "cost_planner"
    
    # =========================================================================
    # RETURN OUTCOME
    # =========================================================================
    
    return {
        "tier": winning_tier,
        "tier_score": winning_score,
        "tier_rankings": tier_rankings,
        "confidence": confidence,
        "flags": flags,
        "rationale": rationale,
        "suggested_next_product": suggested_next
    }
```

---

## 5. Product Integration (product.py)

```python
# products/gcp_v4/product.py

import streamlit as st
from datetime import datetime
from core.mcip import MCIP, CareRecommendation
from core.modules.engine import run_module


def render():
    """Render GCP product using module engine + MCIP integration."""
    
    # Run care_recommendation module
    module_state = run_module("gcp", "care_recommendation")
    
    # If module is complete, publish to MCIP
    if module_state and module_state.get("status") == "complete":
        _publish_to_mcip(module_state)
        
        # Show success message
        _render_completion_screen()
    
    # Module engine handles all rendering, navigation, progress


def _publish_to_mcip(module_state: dict) -> None:
    """Compute recommendation and publish to MCIP.
    
    Args:
        module_state: Completed module state with answers
    """
    
    # Get outcome from module (already computed by logic.py)
    outcome = module_state.get("outcome", {})
    
    if not outcome:
        st.error("❌ Unable to generate recommendation")
        return
    
    # Build CareRecommendation contract
    recommendation = CareRecommendation(
        # Core recommendation
        tier=outcome["tier"],
        tier_score=outcome["tier_score"],
        tier_rankings=outcome["tier_rankings"],
        confidence=outcome["confidence"],
        flags=outcome.get("flags", []),
        rationale=outcome.get("rationale", []),
        
        # Provenance
        generated_at=datetime.utcnow().isoformat() + "Z",
        version="4.0.0",
        input_snapshot_id=_generate_snapshot_id(),
        rule_set="standard_2025_q4",
        
        # Next step
        next_step={
            "product": outcome.get("suggested_next_product", "cost_planner"),
            "route": outcome.get("suggested_next_product", "cost"),
            "label": "See Cost Estimate",
            "reason": f"Calculate financial impact of {outcome['tier'].replace('_', ' ')}"
        },
        
        # Status
        status="complete",
        last_updated=datetime.utcnow().isoformat() + "Z",
        needs_refresh=False
    )
    
    # Publish to MCIP (single source of truth)
    MCIP.publish_care_recommendation(recommendation)
    
    # Mark GCP as complete
    MCIP.mark_product_complete("gcp")


def _generate_snapshot_id() -> str:
    """Generate unique snapshot ID for this recommendation.
    
    Returns:
        Snapshot ID string
    """
    user_id = st.session_state.get("user_id", "anon")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"gcp_{user_id}_{timestamp}"


def _render_completion_screen() -> None:
    """Render completion screen after recommendation published."""
    
    # Get recommendation from MCIP
    recommendation = MCIP.get_care_recommendation()
    
    if not recommendation:
        return
    
    st.success("✅ **Your Care Plan is Ready!**")
    
    # Show recommendation
    tier_label = recommendation.tier.replace("_", " ").title()
    st.markdown(f"### Recommended: {tier_label}")
    
    st.progress(recommendation.confidence)
    st.caption(f"Confidence: {int(recommendation.confidence * 100)}%")
    
    # Show rationale
    if recommendation.rationale:
        st.markdown("**Key Factors:**")
        for reason in recommendation.rationale:
            st.markdown(f"• {reason}")
    
    # Show flags
    if recommendation.flags:
        st.markdown("---")
        st.markdown("**Important Considerations:**")
        for flag in recommendation.flags:
            tone_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
            emoji = tone_emoji.get(flag["tone"], "ℹ️")
            
            with st.expander(f"{emoji} {flag['label']}"):
                st.markdown(flag["description"])
                
                if flag.get("cta"):
                    if st.button(flag["cta"]["label"], key=f"flag_{flag['id']}"):
                        from core.nav import route_to
                        route_to(flag["cta"]["route"])
    
    # Next steps
    st.markdown("---")
    st.markdown("### 📋 Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💰 See Cost Estimate", type="primary", use_container_width=True):
            from core.nav import route_to
            route_to("cost")
    
    with col2:
        if st.button("🏠 Return to Hub", use_container_width=True):
            from core.nav import route_to
            route_to("hub_concierge")
```

---

## 6. Migration Strategy

### Phase 1: Add MCIP Publishing (Non-Breaking)

1. **Keep existing GCP working** - Don't touch current `products/gcp/`
2. **Create `products/gcp_v4/`** - New directory with MCIP integration
3. **Update `logic.py`** - Return new schema (backward compatible)
4. **Add `product.py`** - Publish to MCIP after completion
5. **Test in parallel** - Both v3 and v4 can coexist

### Phase 2: Update Consumers

1. **Update Cost Planner** - Read from `MCIP.get_care_recommendation()` instead of `st.session_state["gcp"]`
2. **Update Concierge Hub** - Read from MCIP for tile unlocking
3. **Update PFMA** - Read from MCIP for context

### Phase 3: Cutover

1. **Route `?page=gcp` to v4** - Update nav.json
2. **Remove v3 code** - Archive old `products/gcp/`
3. **Celebrate** - Clean architecture achieved! 🎉

---

## 7. File Structure

```
products/gcp_v4/
├── __init__.py
├── product.py                    # Router with MCIP publishing
├── modules/
│   └── care_recommendation/
│       ├── __init__.py
│       ├── module.json           # Questions schema (swappable)
│       ├── config.py             # Converts JSON to ModuleConfig
│       ├── logic.py              # Scoring logic (swappable) ✨ Updated output
│       └── flags.py              # Flag schema definitions
└── README.md                     # Migration guide
```

---

## 8. Example module.json (Unchanged)

```json
{
  "id": "care_recommendation",
  "title": "Guided Care Plan",
  "version": "4.0.0",
  "steps": [
    {
      "id": "intro",
      "title": "Let's find the right care level",
      "type": "intro",
      "content": "This takes about 5 minutes..."
    },
    {
      "id": "adl_support",
      "title": "Daily Living Support",
      "questions": [
        {
          "id": "adl_support_level",
          "type": "single_choice",
          "prompt": "How often does someone need help with daily activities?",
          "options": [
            {"value": "none", "label": "No help needed"},
            {"value": "sometimes", "label": "Occasionally (1-2 times a week)"},
            {"value": "daily", "label": "Every day"},
            {"value": "constant", "label": "Around-the-clock"}
          ],
          "required": true
        }
      ]
    }
  ]
}
```

**No changes needed** - Module engine already handles this format!

---

## 9. Testing Strategy

### Unit Tests

```python
# tests/test_gcp_v4_logic.py

def test_independent_recommendation():
    """Test independent living recommendation."""
    answers = {
        "adl_support_level": "none",
        "falls_last_year": 0,
        "mobility_level": "independent",
        "memory_diagnosis": "none",
        "lives_alone": False,
        "supervision_hours_needed": 0
    }
    
    outcome = derive_outcome(answers)
    
    assert outcome["tier"] == "independent"
    assert outcome["confidence"] >= 0.8
    assert len(outcome["flags"]) == 0


def test_assisted_living_recommendation():
    """Test assisted living recommendation."""
    answers = {
        "adl_support_level": "daily",
        "falls_last_year": 2,
        "mobility_level": "walker",
        "memory_diagnosis": "mild",
        "lives_alone": True,
        "supervision_hours_needed": 8
    }
    
    outcome = derive_outcome(answers)
    
    assert outcome["tier"] == "assisted_living"
    assert "falls_risk" in [f["id"] for f in outcome["flags"]]
    assert outcome["confidence"] >= 0.8
```

### Integration Tests

```python
# tests/test_gcp_mcip_integration.py

def test_gcp_publishes_to_mcip():
    """Test that GCP publishes CareRecommendation to MCIP."""
    
    # Complete GCP module
    # ... simulate module completion ...
    
    # Verify MCIP has recommendation
    rec = MCIP.get_care_recommendation()
    assert rec is not None
    assert rec.tier in ["independent", "in_home", "assisted_living", "memory_care"]
    assert 0.0 <= rec.confidence <= 1.0
    
    # Verify Cost Planner is unlocked
    assert MCIP.is_product_unlocked("cost_planner")
```

---

## 10. Success Metrics

### Code Quality
- ✅ Minimal changes to existing module.json structure
- ✅ logic.py output updated (~50 lines changed)
- ✅ product.py adds MCIP publishing (~100 lines new)
- ✅ Backward compatible during migration

### Integration
- ✅ Publishes to MCIP after completion
- ✅ Unlocks Cost Planner automatically
- ✅ Fires events for hub updates
- ✅ No direct state reads from other products

### User Experience
- ✅ Identical UX (module engine unchanged)
- ✅ Same questions and flow
- ✅ Enhanced completion screen with flags
- ✅ Clear next steps

---

## Summary

**GCP v4 = Self-Contained Module + MCIP Publishing Layer**

GCP v4 is a complete rewrite that:

### What We Keep
✅ JSON-driven questions (`module.json`)  
✅ Swappable logic (`logic.py`)  
✅ Module engine integration  
✅ User experience  

### What We Add
✨ MCIP publishing (`product.py`)  
✨ Structured flags (risk/support)  
✨ Detailed rationale  
✨ Event-driven updates  

### Migration Path
1. Create `products/gcp_v4/` alongside existing GCP
2. Update `logic.py` output schema
3. Add `product.py` with MCIP publishing
4. Test in parallel with feature flag
5. Update consumers to read from MCIP
6. Cutover routing to v4
7. Archive v3

**Result**: Clean architecture with minimal disruption! 🎯

---

**Ready to implement?** Start with updating `logic.py` output format and adding `flags.py` schema.
