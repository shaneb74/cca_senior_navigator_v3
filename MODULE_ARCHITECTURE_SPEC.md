# Module Architecture Specification

## Executive Summary

A **Module** is a self-contained data collection workflow that gathers user inputs through a structured questionnaire, processes those inputs through domain-specific logic, and delivers a standardized data contract to both its Product Tile (for UI state management) and the Master Care Intelligence Protocol (MCIP) handoff system (for inter-product data sharing).

---

## Architecture Role

### Position in System Hierarchy
```
Application (Streamlit)
  └── Hub (e.g., Concierge Hub)
      └── Product Tile (e.g., GCP Tile)
          └── Product (e.g., products/gcp/product.py)
              └── MODULE (e.g., care_recommendation)
                  ├── manifest (module.json)
                  ├── logic (logic.py)
                  └── engine (core/modules/engine.py)
```

### Core Responsibilities
1. **Data Collection**: Present questions/fields to users in structured sections
2. **State Management**: Track user progress and answers in session state
3. **Business Logic**: Apply domain-specific rules to collected data
4. **Contract Delivery**: Publish standardized outcomes to Product and MCIP
5. **Progress Tracking**: Report completion status to parent Product for UI updates

---

## Data Gathering Process

### Input Structure: module.json Manifest

Every module defines its data collection workflow in a JSON manifest with three key sections:

#### 1. Module Metadata
```json
{
  "module": {
    "id": "gcp_care_recommendation",
    "name": "Guided Care Plan",
    "version": "v2025.10",
    "display": {
      "title": "Find the Right Senior Care",
      "subtitle": "We'll match you to the best living options...",
      "estimated_time": "≈2 min",
      "autosave": true,
      "progress_weight": 1.0
    }
  }
}
```

**Purpose**: Identifies the module, defines user-facing metadata, and sets autosave/progress behavior.

#### 2. Sections (Data Collection Steps)
```json
{
  "sections": [
    {
      "id": "about_you",
      "title": "About You",
      "type": "form",
      "description": "Tell us about the person's current situation.",
      "questions": [...]
    },
    {
      "id": "results",
      "title": "Your Care Recommendation",
      "type": "results"
    }
  ]
}
```

**Section Types**:
- `"form"`: Collects user input via questions
- `"info"`: Displays information/instructions (no data collection)
- `"results"`: Displays computed outcomes (must be last section)

#### 3. Questions (Field Definitions)
```json
{
  "id": "memory_changes",
  "type": "string",
  "select": "single",
  "label": "Memory or cognitive changes?",
  "required": true,
  "options": [
    { "label": "No concerns", "value": "none", "score": 0 },
    { "label": "Occasional forgetfulness", "value": "occasional", "score": 1, "flags": ["cognitive_concern"] },
    { "label": "Moderate decline", "value": "moderate", "score": 2, "flags": ["moderate_cognitive"] },
    { "label": "Severe decline or dementia", "value": "severe", "score": 3, "flags": ["severe_cognitive"] }
  ],
  "ui": { "widget": "chip", "orientation": "vertical" }
}
```

**Question Schema**:
- **id**: Unique key for storing answer in module state
- **type**: Data type (`string`, `number`, `boolean`, `date`, `currency`)
- **select**: Single-choice (`"single"`) or multi-choice (`"multi"`)
- **label**: User-facing question text
- **required**: Whether answer is mandatory for progression
- **options**: Array of choices with:
  - `label`: Display text
  - `value`: Stored value
  - `score`: Numeric weight for scoring logic (optional)
  - `flags`: Boolean flags to set when selected (optional)
- **ui**: Widget configuration:
  - `widget`: UI component (`chip`, `radio`, `multi_chip`, `checkbox`, `select`, `text`, `textarea`, `number`, `currency`, `date`)
  - `orientation`: Layout (`horizontal`, `vertical`)
  - `allow_custom`: Allow user-entered values (boolean)
- **visible_if**: Conditional display rules (object with `key`, `eq`/`in`/etc.)
- **help**: Additional context/tooltip text (optional)
- **default**: Pre-filled value (optional)

### Data Collection Flow

1. **Engine Initialization** (`core/modules/engine.py:run_module()`):
   - Loads module manifest from `products/{product}/modules/{module_name}/module.json`
   - Converts JSON schema to `ModuleConfig` dataclass
   - Initializes module state at `st.session_state[state_key]` (e.g., `st.session_state["gcp"]`)

2. **Step Navigation**:
   - Engine tracks current step in `st.session_state[f"{state_key}._step"]`
   - Renders current section's questions via `core/modules/components.py` renderers
   - Validates required fields before allowing progression
   - Updates progress percentage based on completed fields

3. **Answer Storage**:
   - Each question answer stored at `st.session_state[state_key][question_id]`
   - Example: `st.session_state["gcp"]["memory_changes"] = "moderate"`
   - Multi-select answers stored as lists: `["diabetes", "chf", "copd"]`

4. **Progress Tracking**:
   - Engine calculates progress: `(completed_fields + current_step_fraction) / total_progress_steps`
   - Updates module state: `state["progress"] = 67.5` (percentage)
   - Updates tile state: `st.session_state["tiles"]["gcp"]["progress"] = 67.5`
   - Sets status: `"new"` (0%), `"doing"` (1-99%), `"done"` (100%)

5. **Resume Functionality**:
   - Last completed step saved to `st.session_state["tiles"][product]["last_step"]`
   - On module re-entry, engine resumes from saved step
   - "Save & Continue Later" button triggers return to hub with state preserved

---

## Business Logic Layer

### Logic File: logic.py

Each module implements domain-specific processing in `products/{product}/modules/{module_name}/logic.py`:

```python
from core.modules.schema import OutcomeContract

def derive_outcome(answers: Dict[str, Any], context: Dict[str, Any]) -> OutcomeContract:
    """
    Process collected answers to generate care recommendation.
    
    Args:
        answers: Dict of all question_id -> answer_value pairs
        context: Environment data (product, version, geo, auth)
    
    Returns:
        OutcomeContract with recommendation, flags, scores, and summary
    """
    # 1. Extract and normalize answers
    memory_changes = answers.get("memory_changes", "none")
    mobility = answers.get("mobility", "independent")
    
    # 2. Apply scoring rules
    score = 0
    score += MEMORY_SCORES.get(memory_changes, 0)
    score += MOBILITY_SCORES.get(mobility, 0)
    
    # 3. Determine recommendation
    if score >= 38:
        recommendation = "Memory Care"
    elif score >= 25:
        recommendation = "Assisted Living"
    elif score >= 11:
        recommendation = "In-Home Care"
    else:
        recommendation = "Independent / In-Home"
    
    # 4. Set flags for downstream products
    flags = {}
    if memory_changes in ["moderate", "severe"]:
        flags["cognitive_concern"] = True
    if mobility in ["bedbound", "wheelchair"]:
        flags["high_mobility_dependence"] = True
    
    # 5. Generate summary points
    summary_points = [
        f"Memory status: {memory_changes.replace('_', ' ').title()}",
        f"Mobility: {mobility.replace('_', ' ').title()}",
        f"Recommended care tier: {recommendation}"
    ]
    
    # 6. Return contract
    return OutcomeContract(
        recommendation=recommendation,
        confidence=0.85,
        flags=flags,
        tags=["senior_care", "care_assessment"],
        domain_scores={"cognitive": 3, "mobility": 2},
        summary={"points": summary_points},
        routing={"next_product": "cost"},
        audit={"logic_version": "v3.0", "total_score": score}
    )
```

### Outcome Computation Trigger

The engine calls the logic function when user reaches the results section:

```python
# In core/modules/engine.py:_ensure_outcomes()
if config.outcomes_compute:
    fn = _resolve_callable(config.outcomes_compute)  # "products.gcp.modules.care_recommendation.logic:derive_outcome"
    result = fn(answers=answers, context=context)
    outcome = OutcomeContract(**result) if isinstance(result, dict) else result
```

**Context Data Provided**:
```python
{
    "product": "gcp",
    "version": "v2025.10",
    "person_a_name": "John Doe",  # From module state or session profile
    "geo": "CA",  # User's state from profile
    "auth": True  # Whether user is authenticated
}
```

---

## Data Contract: OutcomeContract

### Contract Schema (core/modules/schema.py)

```python
@dataclass
class OutcomeContract:
    recommendation: Optional[str] = None           # Primary outcome (e.g., "Memory Care")
    confidence: Optional[float] = None             # 0-1 confidence score
    flags: Dict[str, bool] = field(default_factory=dict)          # Boolean indicators
    tags: List[str] = field(default_factory=list)                 # Categorical labels
    domain_scores: Dict[str, Any] = field(default_factory=dict)   # Subscores by domain
    summary: Dict[str, Any] = field(default_factory=dict)         # Display data
    routing: Dict[str, Any] = field(default_factory=dict)         # Navigation hints
    audit: Dict[str, Any] = field(default_factory=dict)           # Metadata/versioning
```

### Contract Example: GCP Care Recommendation

```json
{
  "recommendation": "Memory Care",
  "confidence": 0.87,
  "flags": {
    "cognitive_concern": true,
    "high_mobility_dependence": true,
    "falls_multiple": true,
    "chronic_present": true
  },
  "tags": ["senior_care", "memory_support", "high_acuity"],
  "domain_scores": {
    "cognitive": 3,
    "adl_iadl": 8,
    "mobility": 2,
    "medication": 2,
    "health": 3,
    "isolation": 1
  },
  "summary": {
    "points": [
      "Severe memory decline requiring 24/7 supervision",
      "High mobility dependence (wheelchair user)",
      "Multiple falls in past 6 months",
      "Requires assistance with bathing, dressing, and meals"
    ]
  },
  "routing": {
    "next_product": "cost",
    "recommended_facilities": ["memory_care", "memory_care_high_acuity"]
  },
  "audit": {
    "logic_version": "v3.0",
    "total_score": 42,
    "timestamp": "2025-10-13T14:32:01Z"
  }
}
```

---

## Contract Delivery Mechanism

### 1. Module State Storage
Outcome stored in session state at `{state_key}._outcomes`:
```python
st.session_state["gcp._outcomes"] = asdict(outcome)
```

### 2. MCIP Handoff System
Critical data published to centralized handoff for downstream products:
```python
handoff = st.session_state.setdefault("handoff", {})
handoff[state_key] = {
    "recommendation": outcome.recommendation,           # Primary outcome
    "flags": dict(outcome.flags),                       # Boolean indicators
    "tags": list(outcome.tags),                         # Categorical labels
    "domain_scores": dict(outcome.domain_scores)        # Subscores
}
```

**Handoff Structure**:
```json
{
  "gcp": {
    "recommendation": "Memory Care",
    "flags": {
      "cognitive_concern": true,
      "high_mobility_dependence": true
    },
    "tags": ["senior_care", "memory_support"],
    "domain_scores": {
      "cognitive": 3,
      "mobility": 2
    }
  },
  "cost": {
    "recommendation": "memory_care",
    "estimated_monthly": 8500,
    "flags": {"medicaid_eligible": true}
  }
}
```

### 3. Product Tile Updates
Progress and status synced to tile state for hub display:
```python
tiles = st.session_state.setdefault("tiles", {})
tile_state = tiles.setdefault(config.product, {})
tile_state["progress"] = 100.0
tile_state["status"] = "done"
tile_state["last_step"] = len(config.steps) - 1  # Results page
```

### 4. Concierge Panel (MCIP Display)
For products that drive workflow routing, outcomes populate concierge panel:
```python
if outcome.recommendation:
    concierge_panel = {
        "reason": f"{person_name}'s care plan suggests {outcome.recommendation}",
        "next_step": "cost",  # Recommended next product
        "nudges": []  # Contextual alerts
    }
    if outcome.flags.get("emotional_followup"):
        concierge_panel["nudges"].append("Emotional wellbeing may need advisor check-in.")
    
    st.session_state.setdefault("mcip", {})["concierge"] = concierge_panel
```

---

## Contract Consumption by Downstream Products

### Cost Planner Module
Reads GCP handoff to pre-populate care tier:
```python
handoff = st.session_state.get("handoff", {})
gcp_data = handoff.get("gcp", {})
care_tier = gcp_data.get("recommendation", "").lower().replace(" ", "_")

# Map GCP recommendation to Cost Planner care levels
tier_mapping = {
    "independent_/_in-home": "no_care",
    "in-home_care": "in_home_care",
    "assisted_living": "assisted_living",
    "memory_care": "memory_care",
    "high-acuity_memory_care": "memory_care_high_acuity"
}
cost_care_tier = tier_mapping.get(care_tier, "assisted_living")
```

### Product Tile (Visibility/Locking)
Tiles use handoff flags to control unlock requirements:
```python
# In core/product_tile.py:tile_requirements_satisfied()
def _evaluate_requirement(req: str, state: Mapping[str, Any]) -> bool:
    if req == "gcp:complete":
        return state.get("gcp", {}).get("progress", 0) >= 100
    
    if req == "flag:cognitive_concern":
        gcp_flags = state.get("gcp", {}).get("flags", {})
        return bool(gcp_flags.get("cognitive_concern", False))
```

**Example Tile Config**:
```python
tile = ProductTileHub(
    key="pfma",
    title="Plan for My Advisor",
    unlock_requires=["gcp:complete"],  # Only unlocks after GCP done
    lock_msg="Complete Guided Care Plan first"
)
```

### FAQ Dynamic Questions
FAQ page uses handoff flags to personalize question suggestions:
```python
gcp_handoff = st.session_state.get("handoff", {}).get("gcp", {})
gcp_flags = gcp_handoff.get("flags", {})

for question in QUESTION_BANK:
    score = question["priority"]
    
    # Boost score if question's tags match user's flags
    if question["tags"].get("cognitive_concern") and gcp_flags.get("cognitive_concern"):
        score += 3
    if question["tags"].get("fall_risk") and gcp_flags.get("falls_multiple"):
        score += 2

top_3_questions = sorted(questions, key=lambda q: q.score, reverse=True)[:3]
```

---

## Module Creation Requirements

### Minimum Required Files

1. **module.json** (Manifest)
   - Location: `products/{product}/modules/{module_name}/module.json`
   - Content: Metadata, sections, questions

2. **logic.py** (Business Logic)
   - Location: `products/{product}/modules/{module_name}/logic.py`
   - Required function: `derive_outcome(answers, context) -> OutcomeContract`

3. **product.py Integration**
   - Location: `products/{product}/product.py`
   - Must call `core.modules.engine.run_module(config)`

### Integration Checklist

#### 1. Manifest Validation
```python
from core.modules.schema import validate_manifest

with open("module.json") as f:
    manifest = json.load(f)
    validate_manifest(manifest)  # Raises ValueError if invalid
```

#### 2. Product Registration
In `products/{product}/product.py`:
```python
from core.modules.base import load_module_manifest
from core.modules.engine import run_module
from core.modules.schema import ModuleConfig

def render_product():
    config = _load_module_config()
    run_module(config)

def _load_module_config() -> ModuleConfig:
    manifest = load_module_manifest("product_key", "module_name")
    # Convert manifest to ModuleConfig
    return ModuleConfig(
        product="product_key",
        version=manifest["module"]["version"],
        steps=_convert_sections_to_steps(manifest["sections"]),
        state_key="product_key",
        outcomes_compute="products.product_key.modules.module_name.logic:derive_outcome",
        results_step_id="results"
    )
```

#### 3. Navigation Configuration
In `config/nav.json`:
```json
{
  "key": "product_key",
  "label": "Product Name",
  "icon": "📊",
  "module": "products.product_key.product:render_product",
  "requires_auth": false,
  "roles": ["user"]
}
```

#### 4. Tile Configuration
In hub (e.g., `hubs/concierge.py`):
```python
from core.product_tile import ProductTileHub

tile = ProductTileHub(
    key="product_key",
    title="Product Display Name",
    desc="Brief description",
    primary_label="Start",
    primary_route="?page=product_key",
    progress=st.session_state.get("tiles", {}).get("product_key", {}).get("progress", 0),
    status_text=None,  # Auto-computed from progress
    unlock_requires=[],  # Dependencies on other products
    image_square="/static/images/product_icon.svg"
)
tile.render()
```

---

## Data Flow Diagram

```
User Interaction
      ↓
[Module Engine] ← module.json (questions)
      ↓
[Session State] {state_key: {q1: "answer", q2: 42, ...}}
      ↓
[Logic Function] ← answers + context
      ↓
[OutcomeContract] {recommendation, flags, scores, summary, routing, audit}
      ↓
      ├─→ [Module State] st.session_state["{state_key}._outcomes"]
      ├─→ [MCIP Handoff] st.session_state["handoff"][state_key]
      ├─→ [Tile State] st.session_state["tiles"][product] {progress, status}
      └─→ [Concierge Panel] st.session_state["mcip"]["concierge"] {reason, next_step, nudges}
            ↓
[Downstream Products] Read handoff to access flags/scores/recommendation
            ↓
[User Experience] Personalized routing, pre-filled forms, dynamic content
```

---

## Key Architectural Principles

### 1. Single Source of Truth
- Module manifest (`module.json`) is the definitive source for questions, options, and UI
- All question IDs, option values, and flags must match between manifest and logic.py

### 2. Stateless Logic
- `derive_outcome()` must be pure function (no side effects)
- All inputs come from `answers` dict (module state) and `context` dict (environment)
- No direct access to `st.session_state` inside logic functions

### 3. Immutable Contracts
- Once `OutcomeContract` is published, it should not be modified
- Re-computing outcomes requires clearing `{state_key}._outcomes` and re-running module
- Restart functionality clears module state, tile state, and handoff entry

### 4. Progressive Enhancement
- Modules must gracefully handle missing answers (default to safe values)
- Optional questions should not block progression
- Visible_if conditions prevent showing irrelevant questions

### 5. Auditable Logic
- All scoring/recommendation decisions must be documented in logic.py comments
- `audit` field in contract should include version, timestamp, and raw scores
- Domain scores allow debugging why specific recommendation was made

---

## Common Patterns

### Conditional Question Display
```json
{
  "id": "veteran_benefits",
  "label": "What VA benefits do you currently receive?",
  "visible_if": {
    "key": "is_veteran",
    "eq": true
  }
}
```

### Multi-Select with Custom Input
```json
{
  "id": "chronic_conditions",
  "type": "string",
  "select": "multi",
  "options": [
    {"label": "Diabetes", "value": "diabetes"},
    {"label": "Other", "value": "other"}
  ],
  "ui": {
    "widget": "multi_chip",
    "allow_custom": true,
    "placeholder": "Type and press Add"
  }
}
```

### Weighted Scoring with Flags
```json
{
  "id": "memory_changes",
  "options": [
    {
      "label": "Severe decline or dementia",
      "value": "severe",
      "score": 3,
      "flags": ["severe_cognitive", "memory_care_candidate"]
    }
  ]
}
```

### Override Logic (Priority Rules)
```python
def derive_outcome(answers, context):
    # Normal scoring
    total_score = calculate_total_score(answers)
    tier = determine_tier_by_score(total_score)
    
    # Override for safety-critical cases
    if answers.get("memory_changes") == "severe" and answers.get("wandering") == "frequent":
        tier = 4  # Force High-Acuity Memory Care
        flags["memory_care_override"] = True
    
    return OutcomeContract(recommendation=TIER_NAMES[tier], flags=flags, ...)
```

---

## Module Development Workflow

### 1. Design Phase
- Define domain model (what data drives the recommendation?)
- Identify questions needed to collect domain data
- Map answer options to scoring weights
- Define flags for downstream product integration

### 2. Manifest Creation
- Draft `module.json` with metadata, sections, and questions
- Validate JSON schema with `core.modules.schema.validate_manifest()`
- Test question rendering in UI (use `SN_DEBUG_TILES=1` for dev mode)

### 3. Logic Implementation
- Implement `derive_outcome()` in `logic.py`
- Write unit tests for scoring rules
- Test edge cases (all questions skipped, extreme values, etc.)

### 4. Integration Testing
- Register module in product.py and nav.json
- Test full flow: start → answer questions → see results
- Verify handoff data in `st.session_state["handoff"]`
- Confirm downstream products can read flags/recommendation

### 5. Validation
- Check progress tracking accuracy (should reach 100% at results)
- Test Save & Continue Later functionality
- Verify Restart clears all state correctly
- Confirm Back button navigation works

---

## Error Handling

### Manifest Validation Errors
```python
# Missing required field
ValueError: Manifest error: missing 'id' in manifest.sections[0].questions[2].

# Invalid question type
ValueError: Manifest error: invalid type 'textarea' in manifest.sections[1].questions[0].
```

### Logic Execution Errors
If `derive_outcome()` raises exception, engine displays error to user:
```python
try:
    result = fn(answers=answers, context=context)
except Exception as e:
    st.error(f"❌ Error computing outcomes: {type(e).__name__}: {str(e)}")
    outcome = OutcomeContract()  # Empty contract as fallback
```

### Missing Dependencies
If downstream product expects flag that module doesn't set:
```python
# Defensive programming in consuming products
gcp_flags = st.session_state.get("handoff", {}).get("gcp", {}).get("flags", {})
if gcp_flags.get("cognitive_concern", False):  # Default to False if missing
    show_memory_care_options()
```

---

## Performance Considerations

### State Size
- Module state grows with number of questions (typically 10-30 KB)
- Large multi-select answers or custom text can increase size
- Session state is in-memory; no persistence beyond browser session

### Computation Cost
- `derive_outcome()` called only once (when reaching results)
- Cached in `{state_key}._outcomes` to avoid re-computation
- Keep logic.py functions under 100ms for responsive UX

### Rendering Optimization
- Engine renders only current step's questions
- Progress calculation is incremental (not full re-scan)
- Tile updates are batched (single write to `st.session_state["tiles"]`)

---

## Testing Strategy

### Unit Tests (logic.py)
```python
def test_derive_outcome_memory_care():
    answers = {
        "memory_changes": "severe",
        "mobility": "wheelchair",
        "help_overall": "extensive",
        "falls": "multiple"
    }
    context = {"product": "gcp", "version": "v3.0"}
    
    outcome = derive_outcome(answers, context)
    
    assert outcome.recommendation == "Memory Care"
    assert outcome.flags["severe_cognitive"] is True
    assert outcome.domain_scores["cognitive"] == 3
```

### Integration Tests (full flow)
```python
def test_module_complete_flow():
    # Simulate user filling out questionnaire
    st.session_state["gcp"] = {
        "age_range": "85_plus",
        "living_situation": "alone",
        "memory_changes": "moderate",
        ...
    }
    st.session_state["gcp._step"] = len(module_config.steps) - 1  # Results page
    
    # Run engine
    run_module(module_config)
    
    # Verify handoff populated
    assert "gcp" in st.session_state["handoff"]
    assert st.session_state["handoff"]["gcp"]["recommendation"] is not None
```

---

## Future Extensions

### Planned Enhancements
- **Multi-page modules**: Support sub-modules with their own manifests
- **Branching logic**: Allow sections to conditionally route based on answers
- **Live validation**: Real-time feedback on answer constraints
- **Data export**: Allow users to download their answers as PDF/JSON
- **Version migration**: Auto-upgrade old module state to new manifest versions

### Extensibility Points
- **Custom widgets**: Register new UI components in `core/modules/components.py`
- **Plugin logic**: Allow external modules to contribute to outcomes (e.g., 3rd-party risk calculators)
- **Event hooks**: Trigger external actions on module completion (e.g., CRM integration)

---

## Summary

A module is a **self-contained assessment workflow** that:
1. Collects structured user input via JSON-defined questions
2. Processes answers through domain-specific business logic
3. Outputs a standardized `OutcomeContract` with recommendations, flags, and scores
4. Delivers contract to Product Tile (for UI state) and MCIP handoff (for inter-product data sharing)
5. Enables downstream products to personalize experiences based on user's assessment results

**Key files for new module creation**:
- `products/{product}/modules/{module_name}/module.json` (data collection workflow)
- `products/{product}/modules/{module_name}/logic.py` (business rules)
- `products/{product}/product.py` (integration with engine)
- `config/nav.json` (navigation registration)
- Hub tile configuration (product visibility and locking)

**Data contract delivery targets**:
- `st.session_state["{state_key}._outcomes"]` (full contract for product)
- `st.session_state["handoff"][state_key]` (critical data for MCIP)
- `st.session_state["tiles"][product]` (progress/status for hub UI)
- `st.session_state["mcip"]["concierge"]` (workflow routing hints)
