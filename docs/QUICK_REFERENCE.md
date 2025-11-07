# Quick Reference: Core Patterns & Contracts

**Purpose**: Fast lookup for developers implementing Senior Navigator in new codebase.

---

## Contract Schemas (TypeScript/JSON)

### CareRecommendation (from GCP)

```typescript
interface CareRecommendation {
  // Core fields (REQUIRED)
  tier: "independent" | "in_home" | "assisted_living" | "memory_care" | "memory_care_high_acuity";
  tier_score: number;                          // 0-100 confidence
  confidence: number;                          // 0-1 (% questions answered)
  flags: Flag[];                               // Risk/support flags
  rationale: string[];                         // Human-readable reasons
  generated_at: string;                        // ISO 8601 timestamp
  status: "new" | "in_progress" | "complete";
  
  // Extended fields (OPTIONAL but recommended)
  tier_rankings?: Array<[string, number]>;     // All tiers with scores
  input_snapshot_id?: string;                  // Unique assessment ID
  allowed_tiers?: string[];                    // Post-gate allowed tiers
  hours_llm_band?: string;                     // "4-8h", "9-12h", etc.
  hours_calculated?: number;                   // Exact hours (6.5)
  badls?: string[];                            // Basic ADLs needing help
  iadls?: string[];                            // Instrumental ADLs
  cognition_level?: 0 | 1 | 2 | 3;            // None/Mild/Moderate/Severe
  behaviors?: string[];                        // Behavioral issues
  risky_behaviors?: boolean;                   // Gate flag
  spouse_or_partner_present?: boolean;
  rule_set?: string;                           // "v4.0"
  schema_version?: number;                     // 2
}

interface Flag {
  id: string;                                  // "falls_risk"
  label: string;                               // "Fall Risk"
  severity: "info" | "warning" | "critical";
  category: "health" | "safety" | "cognitive" | "support";
}
```

**Example**:
```json
{
  "tier": "assisted_living",
  "tier_score": 65,
  "confidence": 0.95,
  "flags": [
    {"id": "adl_assistance", "label": "ADL Assistance Needed", "severity": "warning", "category": "support"},
    {"id": "falls_risk", "label": "Fall Risk", "severity": "critical", "category": "safety"}
  ],
  "rationale": [
    "Needs help with 4 basic ADLs (bathing, dressing, toileting, transferring)",
    "History of falls in past 6 months",
    "Mild cognitive impairment (no memory care needed yet)"
  ],
  "generated_at": "2025-11-07T14:30:00Z",
  "status": "complete",
  "tier_rankings": [["assisted_living", 65], ["in_home", 52], ["memory_care", 30]],
  "allowed_tiers": ["assisted_living", "in_home"],
  "hours_llm_band": "12-16h",
  "badls": ["bathing", "dressing", "toileting", "transferring"],
  "cognition_level": 1,
  "schema_version": 2
}
```

---

### FinancialProfile (from Cost Planner)

```typescript
interface FinancialProfile {
  // Core fields (REQUIRED)
  estimated_monthly_cost: number;              // Total monthly cost
  coverage_percentage: number;                 // 0-100 (% covered)
  gap_amount: number;                          // Monthly shortfall (can be negative)
  runway_months: number;                       // Months until funds depleted
  confidence: number;                          // 0-1
  generated_at: string;                        // ISO 8601
  status: "new" | "in_progress" | "complete";
  
  // Extended fields (OPTIONAL)
  breakdown?: {
    base_cost: number;
    modifiers: number;
    region: string;
    tier: string;
    hours?: number;                            // For in-home care
  };
  coverage_sources?: {
    monthly_income: number;
    asset_liquidation: number;
    insurance: number;
    va_benefits: number;
    other: number;
  };
  recommendations?: string[];                  // Financial planning suggestions
}
```

**Example**:
```json
{
  "estimated_monthly_cost": 6800,
  "coverage_percentage": 65,
  "gap_amount": 2380,
  "runway_months": 48,
  "confidence": 0.92,
  "generated_at": "2025-11-07T15:00:00Z",
  "status": "complete",
  "breakdown": {
    "base_cost": 5500,
    "modifiers": 1300,
    "region": "Seattle Metro",
    "tier": "assisted_living"
  },
  "coverage_sources": {
    "monthly_income": 3200,
    "asset_liquidation": 1220,
    "insurance": 0,
    "va_benefits": 0,
    "other": 0
  },
  "recommendations": [
    "Consider applying for VA Aid & Attendance benefits",
    "Explore long-term care insurance options"
  ]
}
```

---

## JSON Configuration Patterns

### Module Configuration (Questions/Scoring)

```json
{
  "module_id": "care_recommendation",
  "version": "4.0",
  "metadata": {
    "title": "Care Needs Assessment",
    "description": "Comprehensive care level evaluation"
  },
  "sections": [
    {
      "section_id": "adls",
      "title": "Activities of Daily Living",
      "description": "Basic self-care tasks",
      "fields": [
        {
          "field_id": "adl_bathing",
          "type": "radio",
          "label": "How much help is needed with bathing?",
          "required": true,
          "options": [
            {
              "value": "independent",
              "label": "No help needed",
              "score": 0,
              "flags": []
            },
            {
              "value": "occasional",
              "label": "Occasional reminders",
              "score": 5,
              "flags": ["adl_supervision"]
            },
            {
              "value": "frequent",
              "label": "Frequent assistance",
              "score": 15,
              "flags": ["adl_assistance"]
            },
            {
              "value": "total",
              "label": "Complete help needed",
              "score": 25,
              "flags": ["adl_total_care"]
            }
          ]
        }
      ]
    }
  ],
  "tier_thresholds": {
    "independent": {"min": 0, "max": 20, "label": "Independent Living"},
    "in_home": {"min": 21, "max": 40, "label": "In-Home Care"},
    "assisted_living": {"min": 41, "max": 70, "label": "Assisted Living"},
    "memory_care": {"min": 71, "max": 100, "label": "Memory Care"}
  }
}
```

**Field Types**:
- `radio`: Single selection
- `checkbox`: Multiple selections
- `select`: Dropdown
- `text`: Free text
- `number`: Numeric input
- `scale`: Slider (1-10)

---

### Regional Pricing Configuration

```json
{
  "regions": {
    "98001": {
      "region_name": "Seattle Metro",
      "state": "WA",
      "cost_of_living_multiplier": 1.35,
      "assisted_living": {
        "base_monthly": 5500,
        "medical_addon": 800,
        "memory_addon": 1500
      },
      "memory_care": {
        "base_monthly": 7500,
        "high_acuity_addon": 2000
      },
      "in_home_care": {
        "hourly_rate": 28.50,
        "overnight_rate": 22.00,
        "live_in_daily": 320
      }
    },
    "900": {
      "region_name": "Los Angeles Area",
      "state": "CA",
      "cost_of_living_multiplier": 1.45,
      "assisted_living": {"base_monthly": 6200}
    }
  },
  "default_region": {
    "region_name": "National Average",
    "cost_of_living_multiplier": 1.0,
    "assisted_living": {"base_monthly": 4500},
    "in_home_care": {"hourly_rate": 25.00}
  }
}
```

**Lookup Strategy**:
1. Exact ZIP match (98001)
2. Prefix match (900xx → 900)
3. State match
4. Default fallback

---

## API Patterns (Pseudocode)

### Scoring Engine

**WHERE TO FIND IN PROTOTYPE CODE**:
- **File**: `products/gcp_v4/modules/care_recommendation/logic.py`
- **Main Function**: `derive_outcome()` (line 1081)
- **Adjudication**: `_choose_final_tier()` (line 83)

**How Answers Flow**:
1. **Deterministic** (lines 1115-1190): Answers → Score → Tier → Gates → `det_tier`
2. **LLM** (lines 1240-1280): Same `answers` + `det_tier` + `allowed_tiers` → LLM → `llm_tier`
3. **Adjudication** (line 83): Choose between `llm_tier` (if valid) or `det_tier` (fallback)

```python
def calculate_tier(answers: dict, config: ModuleConfig) -> CareRecommendation:
    """Calculate care tier from user answers.
    
    Args:
        answers: {field_id: selected_value, ...}
        config: Loaded module.json
        
    Returns:
        CareRecommendation with tier, score, flags
    """
    # 1. Calculate deterministic score
    total_score = 0
    flags = []
    
    for field_id, selected_value in answers.items():
        field = config.find_field(field_id)
        option = field.find_option(selected_value)
        
        total_score += option.score
        flags.extend(option.flags)
    
    # 2. Map score to tier
    deterministic_tier = None
    for tier, threshold in config.tier_thresholds.items():
        if threshold.min <= total_score <= threshold.max:
            deterministic_tier = tier
            break
    
    # 3. Apply behavior gates
    allowed_tiers = apply_gates(answers, deterministic_tier)
    
    # 4. Request LLM tier (if enabled)
    llm_tier = None
    if feature_flag("FEATURE_GCP_LLM_TIER") != "off":
        llm_tier = request_llm_tier(answers, deterministic_tier, allowed_tiers)
    
    # 5. Adjudicate final tier
    if llm_tier and llm_tier in allowed_tiers:
        final_tier = llm_tier
        source = "llm"
    else:
        final_tier = deterministic_tier
        source = "fallback" if llm_tier else "deterministic"
    
    # 6. Build contract
    return CareRecommendation(
        tier=final_tier,
        tier_score=calculate_confidence(final_tier, total_score),
        confidence=len(answers) / len(config.all_fields),
        flags=dedupe_flags(flags),
        rationale=generate_rationale(answers, final_tier),
        generated_at=now(),
        status="complete",
        allowed_tiers=allowed_tiers,
        tier_rankings=rank_all_tiers(total_score, config)
    )
```

---

### LLM Integration

```python
def request_llm_tier(
    answers: dict,
    deterministic_tier: str,
    allowed_tiers: list[str],
    timeout: int = 15
) -> Optional[str]:
    """Request tier suggestion from LLM with timeout.
    
    Returns:
        Tier string or None on timeout/error
    """
    # 1. Build context
    context = build_narrative_context(answers)
    
    # 2. Construct prompt
    prompt = f"""
    Based on this care assessment:
    {context}
    
    Deterministic recommendation: {deterministic_tier}
    Allowed options: {allowed_tiers}
    
    Suggest the most appropriate care tier from the allowed options.
    Respond with JSON: {{"tier": "...", "confidence": 0.0-1.0, "reasoning": "..."}}
    """
    
    # 3. Call LLM with timeout
    try:
        response = llm_client.complete(
            prompt=prompt,
            model="gpt-4o-mini",
            timeout=timeout,
            temperature=0.3  # Low temp for consistency
        )
        
        result = parse_json_response(response)
        
        # 4. Validate response
        if result["tier"] not in allowed_tiers:
            log_warning(f"LLM suggested blocked tier: {result['tier']}")
            return None
        
        if result["confidence"] < 0.5:
            log_info(f"LLM low confidence: {result['confidence']}")
            # Still return it, adjudication will decide
        
        return result["tier"]
        
    except TimeoutError:
        log_warning("LLM timeout, falling back to deterministic")
        return None
    except Exception as e:
        log_error(f"LLM error: {e}")
        return None
```

---

### Cost Calculator

```python
def calculate_monthly_cost(
    tier: str,
    zip_code: str,
    hours: Optional[float] = None,
    modifiers: dict = None
) -> dict:
    """Calculate monthly care cost with regional pricing.
    
    Args:
        tier: Care tier (in_home, assisted_living, etc.)
        zip_code: User's ZIP code
        hours: For in-home care (hours per day)
        modifiers: {medical_needs: bool, memory_addon: bool, ...}
        
    Returns:
        {monthly_total, breakdown, region_name}
    """
    # 1. Load regional pricing
    region = lookup_region(zip_code)
    if not region:
        region = load_default_region()
    
    # 2. Calculate base cost
    if tier == "in_home":
        if not hours:
            raise ValueError("hours required for in-home care")
        
        hourly_rate = region.in_home_care.hourly_rate
        base_cost = hourly_rate * hours * 30  # 30 days
        
    else:
        base_cost = region[tier].base_monthly
    
    # 3. Apply modifiers
    modifier_cost = 0
    
    if modifiers and modifiers.get("medical_needs"):
        modifier_cost += region[tier].medical_addon
    
    if modifiers and modifiers.get("memory_addon") and tier == "assisted_living":
        modifier_cost += region[tier].memory_addon
    
    # 4. Apply regional multiplier
    subtotal = base_cost + modifier_cost
    total = subtotal * region.cost_of_living_multiplier
    
    return {
        "monthly_total": round(total, 2),
        "breakdown": {
            "base_cost": base_cost,
            "modifiers": modifier_cost,
            "regional_adjustment": total - subtotal,
            "region": region.region_name,
            "tier": tier,
            "hours": hours
        }
    }
```

---

### MCIP Publishing

```python
class MCIP:
    """Master Care Intelligence Panel - Central coordinator."""
    
    def __init__(self):
        self.contracts = {}
        self.journey_state = {
            "completed_products": [],
            "unlocked_products": ["gcp"]  # GCP always unlocked
        }
    
    def publish_care_recommendation(self, rec: CareRecommendation):
        """Publish care recommendation contract."""
        # Validate contract
        validate_contract(rec, CareRecommendation)
        
        # Store in memory
        self.contracts["care_recommendation"] = rec
        
        # Persist to storage
        self._persist_contract("care_recommendation", rec)
        
        # Emit event
        self._emit_event("contract.published", "care_recommendation")
    
    def get_care_recommendation(self) -> Optional[CareRecommendation]:
        """Get published care recommendation."""
        return self.contracts.get("care_recommendation")
    
    def mark_product_complete(self, product_key: str):
        """Mark product as complete and update journey.
        
        Args:
            product_key: Any version (gcp_v4, gcp, guided_care_plan)
        """
        # Normalize key
        canonical_key = self._normalize_key(product_key)
        
        # Add to completed
        if canonical_key not in self.journey_state["completed_products"]:
            self.journey_state["completed_products"].append(canonical_key)
        
        # Update unlocked products based on journey rules
        self._update_unlocked_products(canonical_key)
        
        # Persist journey state
        self._persist_journey_state()
        
        # Emit event
        self._emit_event("product.completed", canonical_key)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize product key to canonical form."""
        KEY_MAP = {
            "gcp_v4": "gcp",
            "gcp": "gcp",
            "guided_care_plan": "gcp",
            "cost_v2": "cost_planner",
            "cost_planner_v2": "cost_planner",
            "pfma_v3": "pfma"
        }
        return KEY_MAP.get(key, key)
    
    def _update_unlocked_products(self, completed_key: str):
        """Update unlocked products based on journey rules."""
        UNLOCK_RULES = {
            "gcp": ["cost_planner"],
            "cost_planner": ["pfma"],
            "pfma": ["partner_connection"]
        }
        
        unlocks = UNLOCK_RULES.get(completed_key, [])
        for product in unlocks:
            if product not in self.journey_state["unlocked_products"]:
                self.journey_state["unlocked_products"].append(product)
```

---

## Feature Flags

### Global Flags

```python
# Global LLM control
FEATURE_LLM_NAVI = "off" | "shadow" | "assist" | "adjust"

# off: No LLM, pure deterministic
# shadow: LLM runs but doesn't affect outcome (logging only)
# assist: LLM provides suggestions, can be overridden
# adjust: LLM can modify deterministic results (with fallback)
```

### Product-Specific Flags

```python
# GCP flags
FEATURE_GCP_LLM_TIER = "off" | "shadow" | "replace"
FEATURE_GCP_HOURS = "off" | "shadow" | "assist"
FEATURE_GCP_MC_BEHAVIOR_GATE = True | False

# Cost Planner flags
FEATURE_COST_LLM_NARRATIVE = "off" | "on"
```

### Flag Checking Pattern

```python
def get_flag(flag_name: str) -> str:
    """Get feature flag value with fallback to 'off'."""
    return os.environ.get(flag_name, "off")

def is_llm_enabled() -> bool:
    """Check if LLM features are enabled globally."""
    return get_flag("FEATURE_LLM_NAVI") not in ["off", ""]

def should_use_llm_tier() -> bool:
    """Check if GCP should use LLM for tier suggestions."""
    if not is_llm_enabled():
        return False
    return get_flag("FEATURE_GCP_LLM_TIER") in ["shadow", "replace"]
```

---

## Common Calculations

### Hours Band Conversion

```python
HOURS_BAND_MAP = {
    "1-3h": 2.0,
    "4-8h": 6.0,
    "9-12h": 10.5,
    "12-16h": 14.0,
    "16-24h": 20.0,
    "24h": 24.0
}

def convert_band_to_hours(band: str) -> float:
    """Convert hours band to scalar hours per day."""
    return HOURS_BAND_MAP.get(band, 6.0)  # Default to 6h

def convert_hours_to_band(hours: float) -> str:
    """Convert scalar hours to band."""
    if hours <= 3:
        return "1-3h"
    elif hours <= 8:
        return "4-8h"
    elif hours <= 12:
        return "9-12h"
    elif hours <= 16:
        return "12-16h"
    elif hours < 24:
        return "16-24h"
    else:
        return "24h"
```

### Confidence Scoring

```python
def calculate_confidence(answers: dict, config: ModuleConfig) -> float:
    """Calculate assessment confidence (0-1).
    
    Based on:
    - % of required questions answered
    - % of total questions answered
    - Presence of key high-weight questions
    """
    required_fields = [f for f in config.all_fields if f.required]
    all_fields = config.all_fields
    
    required_answered = sum(1 for f in required_fields if f.id in answers)
    total_answered = len(answers)
    
    # Weight required questions higher
    required_score = required_answered / len(required_fields) if required_fields else 1.0
    total_score = total_answered / len(all_fields)
    
    # 70% weight to required, 30% to total
    return 0.7 * required_score + 0.3 * total_score
```

### Coverage Calculation

```python
def calculate_coverage(monthly_cost: float, income_sources: dict) -> dict:
    """Calculate financial coverage and runway.
    
    Args:
        monthly_cost: Total monthly care cost
        income_sources: {monthly_income, assets, insurance, va_benefits}
        
    Returns:
        {coverage_percentage, gap_amount, runway_months}
    """
    # Calculate total monthly coverage
    monthly_income = income_sources.get("monthly_income", 0)
    insurance = income_sources.get("insurance", 0)
    va_benefits = income_sources.get("va_benefits", 0)
    
    monthly_coverage = monthly_income + insurance + va_benefits
    
    # Calculate asset liquidation potential
    total_assets = income_sources.get("assets", 0)
    safe_liquidation_rate = 0.05  # 5% per year
    monthly_asset_coverage = (total_assets * safe_liquidation_rate) / 12
    
    # Total coverage
    total_monthly_coverage = monthly_coverage + monthly_asset_coverage
    
    # Calculate gap
    gap_amount = monthly_cost - total_monthly_coverage
    coverage_percentage = min(100, (total_monthly_coverage / monthly_cost) * 100)
    
    # Calculate runway (months until assets depleted)
    if gap_amount > 0:
        runway_months = total_assets / gap_amount if gap_amount > 0 else float('inf')
    else:
        runway_months = float('inf')  # Fully covered
    
    return {
        "coverage_percentage": round(coverage_percentage, 1),
        "gap_amount": round(gap_amount, 2),
        "runway_months": int(runway_months) if runway_months != float('inf') else -1
    }
```

---

## Error Handling Patterns

### Try-Catch-Fallback

```python
def robust_operation(primary_fn, fallback_fn, error_msg="Operation failed"):
    """Execute primary function with fallback on error."""
    try:
        return primary_fn()
    except Exception as e:
        log_error(f"{error_msg}: {e}")
        return fallback_fn()

# Usage
tier = robust_operation(
    primary_fn=lambda: get_llm_tier(answers),
    fallback_fn=lambda: get_deterministic_tier(answers),
    error_msg="LLM tier request failed"
)
```

### Timeout Wrapper

```python
import signal

def with_timeout(timeout_seconds: int):
    """Decorator to add timeout to function calls."""
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutError(f"Operation timed out after {timeout_seconds}s")
        
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout_seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # Disable alarm
            return result
        
        return wrapper
    return decorator

# Usage
@with_timeout(15)
def call_llm_api(prompt: str):
    return openai.complete(prompt)
```

---

## Testing Patterns

### Contract Validation Tests

```python
def test_care_recommendation_contract():
    """Test CareRecommendation contract validation."""
    # Valid contract
    valid_rec = CareRecommendation(
        tier="assisted_living",
        tier_score=65,
        confidence=0.95,
        flags=[],
        rationale=["Reason 1"],
        generated_at="2025-11-07T14:30:00Z",
        status="complete"
    )
    assert validate_contract(valid_rec) == True
    
    # Invalid: missing required field
    invalid_rec = CareRecommendation(
        tier="assisted_living",
        # Missing tier_score
        confidence=0.95,
        ...
    )
    assert validate_contract(invalid_rec) == False
    
    # Invalid: wrong type
    invalid_rec = CareRecommendation(
        tier="invalid_tier",  # Not in allowed values
        ...
    )
    assert validate_contract(invalid_rec) == False
```

### LLM Fallback Tests

```python
def test_llm_fallback():
    """Test that system works without LLM."""
    # Disable LLM
    os.environ["FEATURE_GCP_LLM_TIER"] = "off"
    
    # Run assessment
    rec = calculate_tier(sample_answers, config)
    
    # Should use deterministic tier
    assert rec.tier == "assisted_living"
    assert rec.tier_score > 0
    
    # Simulate LLM timeout
    with patch('llm_client.complete', side_effect=TimeoutError):
        rec = calculate_tier(sample_answers, config)
        assert rec.tier == "assisted_living"  # Fallback works
```

---

## Performance Considerations

### Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def load_module_config(module_path: str) -> ModuleConfig:
    """Load and cache module configuration."""
    with open(module_path) as f:
        return parse_module_json(f.read())

@lru_cache(maxsize=1)
def load_regional_pricing() -> dict:
    """Load and cache regional pricing (single instance)."""
    with open("regional_cost_config.json") as f:
        return json.load(f)
```

### Lazy Loading

```python
class MCIP:
    _instance = None
    
    def __new__(cls):
        """Singleton pattern for MCIP."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Lazy load contracts from storage
        self.contracts = {}
        self._initialized = True
```

---

**Document Version**: 1.0  
**Companion To**: ARCHITECTURE_FOR_REPLATFORM.md, SEQUENCE_DIAGRAMS.md  
**Last Updated**: 2025-11-07
