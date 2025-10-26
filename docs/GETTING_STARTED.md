# Getting Started with Senior Navigator

## What is Senior Navigator?

**Senior Navigator** is an AI-powered care planning platform that helps families make informed decisions about senior care. The application guides users through a comprehensive assessment process to determine the appropriate level of care, estimate costs, and connect with resources.

### Core Purpose

Senior Navigator solves a critical problem: families facing senior care decisions often feel overwhelmed by complexity, uncertainty about costs, and lack of personalized guidance. Our platform provides:

1. **Guided Care Plan (GCP)** - A comprehensive assessment that determines the appropriate care level
2. **Cost Planning** - Realistic financial estimates with keep-home logic and regional adjustments
3. **Financial Assessment** - Detailed runway calculations to understand affordability
4. **AI Advisor** - Intelligent Q&A system with RAG-based knowledge retrieval
5. **Resource Connections** - Partner network and educational materials

---

## Key Features at a Glance

### 🎯 Guided Care Plan (GCP v4)
- **Question-driven assessment** across 5 sections: Demographics, Safety & Mobility, Cognitive & Emotional Health, Daily Living, Support System
- **Dynamic scoring engine** that computes care tier recommendations
- **Memory Care eligibility logic** with diagnosis confirmation flow
- **Hours/day suggestion** using baseline rules + optional LLM refinement
- **Navi AI assistant** providing contextual guidance throughout the flow

### 💰 Cost Planner v2
- **Quick Estimate** with 3-rule keep-home logic
- **Regional cost adjustments** based on location
- **Multi-module financial assessment**: assets, income, expenses, insurance, benefits
- **Runway calculations** showing months of affordability
- **Expert Review** with PDF export and MCIP integration

### 🤖 AI Advisor
- **Multi-tier retrieval**: Mini-FAQ (instant) → Corporate Knowledge → FAQ Database
- **RAG architecture** using TF-IDF + cosine similarity
- **LLM synthesis** with OpenAI GPT-4o for natural answers
- **Source citations** and recommended questions
- **Headerless immersive UI** with newest-first message ordering

### 🏠 Hub-and-Spoke Architecture
- **Concierge Hub** - Main product launcher
- **Learning Hub** - Educational resources
- **Partners Hub** - Trusted provider network
- **Professional Hub** - Tools for care advisors

---

## How the App Works: User Journey

### 1. Entry & Authentication
```
pages/welcome.py → pages/login.py or pages/signup.py
```
- User lands on welcome page
- Chooses to log in or sign up
- Session initialized with user context

### 2. Hub Navigation
```
hubs/concierge.py
```
- Product tiles displayed based on user role
- Progress tracking shows completion status
- Quick access to AI Advisor and resources

### 3. Guided Care Plan Flow
```
products/concierge_hub/gcp_v4/product.py → modules/care_recommendation/module.json
```

**Question Flow:**
1. **Demographics** - Age, living situation, zip code
2. **Safety & Mobility** - Falls, mobility aids, chronic conditions
3. **Cognitive & Emotional** - Memory changes, mood, behaviors
   - *If Severe cognitive:* Diagnosis confirmation question
4. **Daily Living** - BADLs, IADLs, help needed
   - *If FEATURE_GCP_HOURS enabled:* Hours/day suggestion
5. **Support System** - Caregiver availability, access to care

**Mid-Flow Computation (after Daily Living):**
```python
# products/concierge_hub/gcp_v4/modules/care_recommendation/logic.py
derive_outcome(answers, flags, module_data)
```
- Scoring engine computes tier: `no_care_needed`, `in_home`, `assisted_living`, `memory_care`, `memory_care_high_acuity`
- Cognitive gate checks if Memory Care criteria met
- Bands computed: cognition (none/mild/moderate/high), support (low/moderate/high/24h)
- Risky behaviors flagged
- Optional: Hours/day suggestion computed

**Results Page:**
```
core/modules/engine.py → _render_results_view()
```
- Navi panel announces recommendation
- Memory Care eligibility banner (conditional)
- Clean summary with "What this means for you"
- Three action buttons: Start Over, Explore Costs, Return to Hub

### 4. Cost Planner Flow
```
products/cost_planner_v2/intro.py → prepare_quick_estimate.py → assessments.py
```

**Intro Page:**
- Reads GCP recommendation from session state
- Applies 3-rule keep-home logic:
  - **Rule 1:** In-home → keep_home locked `True`
  - **Rule 2:** Facility + partner → default `True` (changeable)
  - **Rule 3:** Facility + no partner → default `False` (changeable)

**Quick Estimate:**
- Regional cost lookup from CSV
- Base cost + adjustments (home, private room, acuity)
- Monthly adjusted cost calculated

**Financial Assessment (Multi-Module):**
1. Assets (liquid, real estate, vehicles)
2. Income (SS, pensions, investments)
3. Expenses (housing, healthcare, lifestyle)
4. Insurance (LTC, life insurance)
5. Benefits (VA, Medicaid screening)

**Expert Review:**
- Aggregates all data
- Calculates runway (months of affordability)
- Generates recommendations
- Optional: PDF export, MCIP publish

### 5. AI Advisor
```
pages/faq.py → ai/llm_mediator.py
```

**Query Processing:**
1. User asks question
2. Check Mini-FAQ (instant canonical answers)
3. If not found, route to:
   - Corporate Knowledge (company info)
   - FAQ Database (care planning)
4. Retrieve top K chunks via TF-IDF
5. LLM synthesizes answer with sources
6. Display with badges and citations

---

## How to Learn the Codebase

### 🗺️ Start Here: Essential Reading Order

#### 1. Architecture Overview (You Are Here!)
```
docs/ARCHITECTURE.md          - System design, data flow, component architecture
docs/GETTING_STARTED.md       - This document (high-level overview)
docs/REPO_STRUCTURE.md        - Directory layout and file conventions
```

#### 2. Core Services (Foundation Layer)
```
core/flags.py                 - Feature flag registry (centralized flag definitions)
core/state.py                 - Session state initialization
core/nav.py                   - Navigation engine (loads config/nav.json)
core/ui.py                    - HTML/CSS injection, image helpers
core/paths.py                 - Path resolution utilities
core/url_helpers.py           - URL-driven routing (NEW: browser back/forward support)
```

**Key Concepts:**
- **Feature Flags:** Central registry in `flags.py`, set via module.json or programmatically
- **Session State:** All data ephemeral in `st.session_state`, no database
- **Navigation:** Query params as source of truth, history stack for back button
- **Paths:** Never hardcode paths, always use `get_static()`, `get_gcp_module_path()`

#### 3. Module Engine (Question Flow System)
```
core/modules/engine.py        - Module orchestration (run_module, render, step navigation)
core/modules/schema.py        - Module config data structures (Pydantic models)
core/modules/components.py    - Reusable UI components (text input, select, multi-select)
core/modules/layout/          - Layout utilities (actions, containers)
```

**Read This Flow:**
1. `run_module()` - Main entry point (line ~95)
2. `_render_header()` - Progress bar and navigation (line ~150)
3. `_render_question()` - Question rendering dispatcher (line ~400)
4. `_render_results_view()` - Summary page with recommendation (line ~1244)

**Key Insight:** The module engine is product-agnostic. It reads `module.json` and renders questions dynamically. Products like GCP provide the JSON config and custom logic.

#### 4. GCP v4 Deep Dive
```
products/concierge_hub/gcp_v4/
├── product.py                          - Entry point, loads module config
├── modules/care_recommendation/
│   ├── module.json                     - Question definitions (5 sections, ~50 questions)
│   ├── logic.py                        - Scoring engine, tier derivation, gates
│   └── flags.py                        - Display metadata for flags
└── ui_helpers.py                       - GCP-specific UI components
```

**Critical Functions in logic.py:**
- `derive_outcome()` (line ~1038) - Main recommendation engine
- `cognitive_gate()` (line ~546) - Memory Care eligibility check
- `cognition_band()` (line ~578) - Cognitive severity classification
- `support_band()` (line ~607) - Support level classification
- `_build_hours_context()` (line ~939) - Hours/day suggestion input

**module.json Structure:**
```json
{
  "sections": [
    {
      "id": "cognitive",
      "title": "Cognitive & Emotional Health",
      "questions": [
        {
          "id": "memory_changes",
          "type": "string",
          "select": "single",
          "options": [
            {
              "label": "Severe memory issues...",
              "value": "severe",
              "score": 3,
              "flags": ["severe_cognitive_risk", "cognitive_severe_any"]
            }
          ],
          "visible_if": { ... }  // Conditional rendering
        }
      ]
    }
  ]
}
```

#### 5. Cost Planner v2
```
products/cost_planner_v2/
├── intro.py                  - Intro page, reads GCP recommendation
├── prepare_quick_estimate.py - Keep-home logic, regional costs
├── assessments.py            - Multi-module financial assessment
├── expert_review.py          - Aggregation, PDF export, MCIP
└── utils/
    ├── cost_calculator.py    - Core cost computation
    ├── cost_data_loader.py   - CSV/JSON loaders
    └── regional_costs.py     - Regional lookup logic
```

**Follow This Path:**
1. `intro.py` → reads `st.session_state["gcp_recommendation_category"]`
2. `prepare_quick_estimate.py` → applies keep-home rules, calculates monthly cost
3. `assessments.py` → renders financial modules (assets, income, expenses, etc.)
4. `expert_review.py` → calculates runway, generates summary

**Key Data Structures:**
```python
st.session_state["cp_keep_home"] = True/False       # Whether home is kept
st.session_state["cp_monthly_adjusted"] = 8500.0    # Monthly cost estimate
st.session_state["fa_profile"] = {                  # Financial assessment data
    "assets": {...},
    "income": {...},
    "expenses": {...}
}
```

#### 6. AI Systems
```
ai/
├── llm_client.py             - OpenAI client wrapper
├── llm_mediator.py           - FAQ answering (answer_faq, answer_corp)
├── gcp_navi_engine.py        - GCP guidance generation
├── hours_engine.py           - Hours/day suggestion engine
└── schemas.py                - Pydantic models for validation
```

**AI Advisor Flow (pages/faq.py):**
1. User query arrives
2. Check `MINI_FAQ` dict (instant answers)
3. If not found, route to corp/faq based on keywords
4. Load embeddings, compute TF-IDF similarity
5. Retrieve top 5 chunks
6. Call `llm_mediator.answer_faq()` or `answer_corp()`
7. LLM synthesizes answer with sources
8. Insert at `chat[0]` (newest-first pattern)

**Hours Suggestion (Guarded Hybrid):**
- Flag: `FEATURE_GCP_HOURS` (off|shadow|assist)
- Baseline: Rule-based logic (ADLs, falls, mobility)
- LLM Refinement: Schema-validated adjustment (max ±1 step)
- Output: `<1h`, `1-3h`, `4-8h`, `24h` (only 4 allowed bands)

---

## Key Architectural Patterns

### 1. Hub-and-Spoke
```
Hub (concierge.py) → Product Tiles → Products → Modules
```
- **Products** are independent features (GCP, Cost Planner, Trivia, etc.)
- **Hubs** aggregate related products
- **Core** provides shared services (never import products in core)

### 2. Module-Driven Questions
```
module.json (config) → engine.py (renderer) → logic.py (business logic)
```
- **Declarative:** Questions defined in JSON, not Python
- **Dynamic:** Engine reads config and renders questions
- **Extensible:** Add new products by creating module.json + logic.py

### 3. Feature Flags
```
core/flags.py (registry) → module.json (set via options) → logic.py (use in business logic)
```
- **Centralized:** All flags defined in `FLAG_REGISTRY`
- **Declarative:** Set via question options `"flags": ["has_partner"]`
- **Programmatic:** Can also set with `set_flag("key", True)`

### 4. URL-Driven Routing (NEW)
```
Query Params (?page=X&product=Y) → url_helpers.py → Navigation Stack → Browser Back Button
```
- **Source of Truth:** Query params, not session state
- **History:** Navigation stack tracks user path
- **Browser Native:** Back/forward buttons work correctly

### 5. State Management
```
st.session_state (ephemeral) → session_store.py (persistence helpers) → data/users/*.json (optional)
```
- **Session-Based:** All data in `st.session_state`
- **No Database:** Files for demo users only
- **Handoffs:** Products communicate via session state keys

---

## Configuration Files

### Navigation
```
config/nav.json               - Product definitions, routes, modules
```

### UI
```
config/ui_config.json         - Theme, colors, branding
```

### Cost Planning
```
config/regional_cost_config.json              - Regional multipliers
data/cost_data/home_care_costs_by_zip.csv     - Regional cost lookup
config/va_disability_rates_2025.json          - VA benefits tables
```

### AI
```
config/navi_dialogue.json     - Navi guidance messages
data/training/faq/*.json      - FAQ knowledge base
data/training/corp_chunks/*.json - Corporate knowledge
```

---

## Development Workflow

### 1. Local Setup
```bash
# Clone and setup
git clone <repo-url>
cd cca_senior_navigator_v3
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run app
streamlit run app.py
```

### 2. Create a New Product

**Step 1:** Create product directory
```bash
mkdir -p products/my_product/modules/my_module
```

**Step 2:** Create module.json
```json
{
  "id": "my_module",
  "title": "My Module",
  "sections": [
    {
      "id": "section1",
      "title": "Section 1",
      "questions": [
        {
          "id": "question1",
          "type": "string",
          "select": "single",
          "label": "Question text?",
          "options": [
            { "label": "Option 1", "value": "opt1", "score": 1 }
          ]
        }
      ]
    }
  ]
}
```

**Step 3:** Create product.py
```python
import streamlit as st
from core.modules.engine import run_module
from core.modules.schema import ModuleConfig

def render():
    config = ModuleConfig(
        product="my_product",
        module_id="my_module",
        state_key="my_product_state"
    )
    state = run_module(config)
    # Product-specific logic here
```

**Step 4:** Add to nav.json
```json
{
  "products": [
    {
      "id": "my_product",
      "title": "My Product",
      "route": "my_product",
      "module": "products.my_product.product:render"
    }
  ]
}
```

### 3. Add a New Question to GCP

**Edit:** `products/concierge_hub/gcp_v4/modules/care_recommendation/module.json`

```json
{
  "id": "new_question",
  "type": "string",
  "select": "single",
  "label": "Question text?",
  "required": true,
  "options": [
    {
      "label": "Option 1",
      "value": "opt1",
      "score": 2,
      "flags": ["my_new_flag"]
    }
  ],
  "visible_if": { "key": "other_question", "eq": "some_value" }
}
```

**Register flag:** `core/flags.py`
```python
FLAG_REGISTRY = {
    "my_new_flag": {
        "category": "cognitive",
        "severity": "moderate",
        "description": "Flag description"
    }
}
```

**Use in logic:** `logic.py`
```python
def derive_outcome(answers, flags, module_data):
    if "my_new_flag" in flags:
        # Do something
        pass
```

### 4. Pre-Commit Checks
```bash
make lint    # Ruff linting
make type    # Mypy type checking (optional)
make smoke   # Import smoke tests
```

**Pre-commit hook enforces:**
- No imports from legacy GCP versions (v1/v2/v3)
- Only 1 module.json per product
- No backup files (*.bak) staged

---

## Testing

### Smoke Tests
```bash
python -m pytest tests/smoke_imports.py
```
- Validates all imports resolve
- Fast sanity check

### Unit Tests
```bash
python -m pytest tests/test_*.py
```
- GCP logic tests
- Cost calculator tests
- Flag manager tests

### Navigation Tests
```bash
python -m pytest tests/test_nav_resolve.py
```
- Validates all nav.json modules resolve

### Manual Testing Flows

**GCP Flow:**
1. Start GCP from hub
2. Answer questions through all 5 sections
3. Verify recommendation renders
4. Check Memory Care banner logic (if applicable)
5. Click "Explore Costs" → should route to Cost Planner

**Cost Planner Flow:**
1. Complete GCP first (provides recommendation)
2. Start Cost Planner from hub or GCP results
3. Review keep-home logic
4. Complete financial assessment modules
5. Verify Expert Review shows correct runway

**AI Advisor:**
1. Click "Ask Navi" from hub
2. Try canonical questions (instant answers)
3. Try care planning questions (FAQ retrieval)
4. Try company questions (corporate knowledge)
5. Verify sources displayed

---

## Common Tasks

### Add a New Feature Flag
1. Define in `core/flags.py` FLAG_REGISTRY
2. Set in `module.json` options array OR programmatically
3. Use in logic: `if "flag_name" in flags:`
4. Add display metadata to product `flags.py` (optional)

### Change GCP Scoring
1. Edit `products/concierge_hub/gcp_v4/modules/care_recommendation/logic.py`
2. Modify `derive_outcome()` function
3. Update tier thresholds or band logic
4. Test with various answer combinations

### Add Regional Cost Data
1. Update `data/cost_data/home_care_costs_by_zip.csv`
2. Add row: `zip_code,region,base_cost,private_room_premium`
3. Loader automatically picks up new data

### Change Navi Messages
1. Edit `config/navi_dialogue.json`
2. Update messages for specific steps
3. Messages display based on step_id match

### Add FAQ Content
1. Create JSON file in `data/training/faq/`
2. Format: `[{"question": "...", "answer": "..."}]`
3. Loader automatically indexes new content

---

## Debugging Tips

### Enable Debug Mode
```python
# Set in session state or environment
st.session_state["dev_mode"] = True
```
- Shows debug info in UI
- Logs more verbose output
- Displays flag states

### Check Session State
```python
# Add to any page
if st.session_state.get("dev_mode"):
    st.write("Session State:", st.session_state)
```

### Trace Navigation
```python
# Look for console logs
print(f"[NAV] Routing to: {route}")
```

### Check Flags
```python
from core.flags import get_all_flags
flags = get_all_flags()
st.write("Active Flags:", flags)
```

### Verify Module Config
```python
# In product.py
config = ModuleConfig(...)
st.write("Config:", config.dict())
```

---

## Key Documentation

- **ARCHITECTURE.md** - System design, data flow diagrams
- **REPO_STRUCTURE.md** - Directory layout
- **CONTRIBUTING.md** - Development guidelines
- **FLAG_REGISTRY.md** - Complete flag definitions
- **NAVIGATION_HARDENING.md** - URL routing system (NEW)

---

## Getting Help

### Internal Resources
1. Read the code! It's well-commented
2. Check `docs/` directory for design docs
3. Look at existing products as examples
4. Search for patterns: `grep -r "pattern" --include="*.py"`

### Code Patterns to Search For
```bash
# How to set a flag
grep -r "set_flag" --include="*.py"

# How to read session state
grep -r "st.session_state\[" --include="*.py"

# How to route
grep -r "route_to" --include="*.py"

# How to render questions
grep -r "run_module" --include="*.py"
```

### Common Issues

**"Module not found"**
- Check `config/nav.json` has correct path
- Verify module file exists
- Check Python import path

**"Flag not defined"**
- Add to `core/flags.py` FLAG_REGISTRY
- Flags must be registered before use

**"Navigation broken"**
- Check query params in URL
- Verify `_nav_stack` in session state
- Review `core/url_helpers.py` for routing logic

**"Costs not calculating"**
- Verify GCP completed and recommendation set
- Check `st.session_state["gcp_recommendation_category"]`
- Ensure regional data exists for zip code

---

## Next Steps

1. **Read ARCHITECTURE.md** - Understand system design
2. **Run the app locally** - See it in action
3. **Explore core/modules/engine.py** - Learn question rendering
4. **Study GCP v4** - Understand a complete product
5. **Try creating a simple product** - Apply what you learned

**Welcome to Senior Navigator! 🎉**
