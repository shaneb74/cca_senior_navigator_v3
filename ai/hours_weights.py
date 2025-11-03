"""
Time-based weights for ADLs and IADLs.

These weights represent realistic daily hours required for each care task,
based on task duration and frequency. Used for weighted hours calculation
instead of simple counts.

Sources:
- Clinical care planning standards
- Home health aide time studies
- Geriatric care management best practices
"""

# Basic Activities of Daily Living (BADLs)
# Values represent hours per day needed for assistance
BADL_TIME_WEIGHTS = {
    # Physical care tasks
    "bathing": 0.5,         # 30 min, 1x/day = 0.5h/day
    "showering": 0.5,       # Same as bathing
    "dressing": 0.6,        # 20 min, 2x/day (morning/evening) = 0.6h/day
    "toileting": 2.0,       # Requires availability 24/7, not just task time
    "transferring": 1.5,    # Multiple times daily, safety critical, slow
    "feeding": 1.0,         # 3 meals + snacks, setup + assistance = 1h total
    "eating": 1.0,          # Same as feeding
    "hygiene": 0.3,         # Tooth brushing, face washing, grooming = 0.3h/day
    "personal_hygiene": 0.3, # Same as hygiene
    "mobility": 1.5,        # Similar to transferring
    
    # Canonical forms (for deduplication)
    "Bathing/Showering": 0.5,
    "Bathing": 0.5,
    "Showering": 0.5,
    "Dressing": 0.6,
    "Toileting": 2.0,
    "Transferring": 1.5,
    "Eating": 1.0,
    "Feeding": 1.0,
    "Mobility": 1.5,
    "Personal Hygiene": 0.3,
    "Hygiene": 0.3,
}

# Instrumental Activities of Daily Living (IADLs)
# Values represent hours per day or week (converted to daily average)
IADL_TIME_WEIGHTS = {
    "medication_management": 0.5,   # Setup, prompting, monitoring daily
    "medications": 0.5,             # Same as above
    "meds": 0.5,                    # Same as above
    
    "meal_preparation": 1.0,        # Shopping, cooking, cleanup = 1h/day average
    "meals": 1.0,                   # Same as meal_preparation
    
    "housekeeping": 1.5,            # Varies, can be scheduled, 1.5h/day average
    "housework": 1.5,               # Same as housekeeping
    
    "laundry": 0.5,                 # 3-4h/week = ~0.5h/day average
    
    "transportation": 1.0,          # Appointments, errands, varies by week
    "driving": 1.0,                 # Same as transportation
    
    "financial_management": 0.3,    # Bills, statements, monthly tasks
    "finances": 0.3,                # Same as financial_management
    "money_management": 0.3,        # Same as financial_management
    
    "phone_use": 0.2,               # Minimal time but important for isolation
    "telephone": 0.2,               # Same as phone_use
    
    "shopping": 1.0,                # Weekly grocery + errands = ~1h/day average
}

# Cognitive supervision multipliers
# Applied to base hours when cognitive impairment present
COGNITIVE_SUPERVISION_MULTIPLIERS = {
    "none": 1.0,       # No cognitive impairment, no supervision overhead
    "mild": 1.2,       # Occasional prompting, forgetfulness (20% overhead)
    "moderate": 1.6,   # Frequent supervision, decision-making help (60% overhead)
    "severe": 2.2,     # Constant supervision, safety critical (120% overhead)
    "advanced": 2.5,   # Round-the-clock care likely needed (150% overhead)
}

# Behavior-specific multiplier additions (cumulative)
BEHAVIOR_MULTIPLIERS = {
    "wandering": 0.3,           # Requires door alarms, frequent location checks
    "elopement": 0.4,           # More severe than wandering
    "aggression": 0.2,          # De-escalation time, safety protocols
    "sundowning": 0.3,          # Evening/night supervision increases
    "repetitive_questions": 0.1, # Minor but adds to caregiver burden
    "hoarding": 0.1,            # Periodic cleaning, safety checks
    "inappropriate_behavior": 0.2, # Social supervision needs
}

# Medication complexity additions (cumulative hours per day)
MEDICATION_COMPLEXITY_HOURS = {
    "has_insulin": 0.5,                # Blood sugar monitoring, timing coordination
    "has_blood_thinners": 0.2,         # Watch for bruising, diet coordination
    "has_controlled_substances": 0.2,  # Security, documentation requirements
    "requires_injections": 0.3,        # Prep, administration, disposal
    "requires_monitoring": 0.5,        # Vitals checks, logging, response assessment
    "requires_crushing": 0.2,          # Extra prep time per administration
    "has_prn_meds": 0.5,              # Requires judgment, availability, monitoring
    "multiple_times_daily": 0.3,       # 4+ administration times adds complexity
}

# Fall risk adjustments
FALL_RISK_MULTIPLIERS = {
    "none": 1.0,       # No fall history
    "once": 1.1,       # Single fall, some caution
    "multiple": 1.3,   # Multiple falls, extra caution, slower pace
    "frequent": 1.5,   # Very high risk, constant vigilance
}

# Mobility aid adjustments (additive hours for transfer assistance)
MOBILITY_AID_HOURS = {
    "independent": 0.0,    # No additional time
    "cane": 0.2,           # Minimal assistance, standby
    "walker": 0.5,         # More assistance, slower pace
    "wheelchair": 1.0,     # Transfers, positioning, mobility
    "bedbound": 2.0,       # All transfers, repositioning
}


def get_badl_hours(badl: str) -> float:
    """Get time weight for a BADL, with fallback for unknown items.
    
    Args:
        badl: BADL name (any casing/format)
        
    Returns:
        Hours per day (default: 0.5 for unknown BADLs)
    """
    # Try exact match
    if badl in BADL_TIME_WEIGHTS:
        return BADL_TIME_WEIGHTS[badl]
    
    # Try lowercase
    badl_lower = badl.lower().strip()
    if badl_lower in BADL_TIME_WEIGHTS:
        return BADL_TIME_WEIGHTS[badl_lower]
    
    # Try canonical forms
    for canonical, weight in BADL_TIME_WEIGHTS.items():
        if badl_lower in canonical.lower() or canonical.lower() in badl_lower:
            return weight
    
    # Default fallback
    return 0.5


def get_iadl_hours(iadl: str) -> float:
    """Get time weight for an IADL, with fallback for unknown items.
    
    Args:
        iadl: IADL name (any casing/format)
        
    Returns:
        Hours per day (default: 0.3 for unknown IADLs)
    """
    # Try exact match
    if iadl in IADL_TIME_WEIGHTS:
        return IADL_TIME_WEIGHTS[iadl]
    
    # Try lowercase
    iadl_lower = iadl.lower().strip()
    if iadl_lower in IADL_TIME_WEIGHTS:
        return IADL_TIME_WEIGHTS[iadl_lower]
    
    # Try partial matches
    for canonical, weight in IADL_TIME_WEIGHTS.items():
        if iadl_lower in canonical.lower() or canonical.lower() in iadl_lower:
            return weight
    
    # Default fallback
    return 0.3


def get_cognitive_multiplier(
    cognitive_level: str | None,
    has_wandering: bool = False,
    has_aggression: bool = False,
    has_sundowning: bool = False,
    has_repetitive_questions: bool = False
) -> float:
    """Calculate total cognitive supervision multiplier.
    
    Args:
        cognitive_level: "none", "mild", "moderate", "severe", "advanced"
        has_wandering: Elopement risk
        has_aggression: Aggressive behaviors
        has_sundowning: Evening confusion
        has_repetitive_questions: Memory issues
        
    Returns:
        Multiplier (1.0 = no overhead, 2.5 = max overhead before 24h needed)
    """
    # Base multiplier from level
    base = COGNITIVE_SUPERVISION_MULTIPLIERS.get(cognitive_level or "none", 1.0)
    
    # Add behavior-specific adjustments
    adjustments = 0.0
    if has_wandering:
        adjustments += BEHAVIOR_MULTIPLIERS["wandering"]
    if has_aggression:
        adjustments += BEHAVIOR_MULTIPLIERS["aggression"]
    if has_sundowning:
        adjustments += BEHAVIOR_MULTIPLIERS["sundowning"]
    if has_repetitive_questions:
        adjustments += BEHAVIOR_MULTIPLIERS["repetitive_questions"]
    
    # Total multiplier (cap at 2.5 to prevent unrealistic escalation)
    total = base + adjustments
    return min(total, 2.5)


def get_fall_risk_multiplier(falls: str | None) -> float:
    """Get multiplier for fall risk.
    
    Args:
        falls: "none", "once", "multiple", "frequent"
        
    Returns:
        Multiplier for task duration
    """
    return FALL_RISK_MULTIPLIERS.get(falls or "none", 1.0)


def get_mobility_hours(mobility: str | None) -> float:
    """Get additional hours needed for mobility assistance.
    
    Args:
        mobility: "independent", "cane", "walker", "wheelchair", "bedbound"
        
    Returns:
        Additional hours per day
    """
    return MOBILITY_AID_HOURS.get(mobility or "independent", 0.0)
