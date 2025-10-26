# Architecture & Data Flow

## System Overview

This application follows a **hub-and-spoke** architecture where:
- **Products** are independent features (GCP, Cost Planner, etc.)
- **Core** provides shared services (navigation, state, flags)
- **Hubs** aggregate related products and resources
- **Data flows** through session state, not database persistence

---

## 📊 Data Flow Diagram

```mermaid
flowchart LR
  A[Module JSON (GCP)] --> B[logic.py: flags + derived]
  B --> C[Scoring Engine]
  C --> D[Recommendation + Reasons]
  D --> E[Cost Planner Intro]
  E --> F[Quick Estimate (monthly_adjusted)]
  F --> G[Financial Assessment]
  D --> H{FEATURE_LLM_NAVI?}
  H -->|assist| I[Navi messages (LLM)]
  H -->|off| I2[Stock copy]
```

### **Flow Explanation**

1. **GCP Question Flow** (`products/gcp_v4/`)
   - User answers questions defined in `module.json`
   - Answers stored in `st.session_state["gcp_answers"]`
   - Flags set (e.g., `has_partner`, `is_move_flexible`)

2. **Scoring & Recommendation** (`logic.py`)
   - Mid-flow computation after step 3 (Daily Living)
   - `compute_recommendation_category()` → derives `gcp_recommendation_category`
   - Categories: `in_home`, `assisted_living`, `memory_care`, etc.

3. **Cost Planner Handoff** (`products/cost_planner_v2/`)
   - Intro reads `gcp_recommendation_category` + `has_partner` flag
   - Applies 3-rule keep_home logic:
     - **Rule 1:** In-home → keep_home locked True
     - **Rule 2:** Facility + partner → default Yes (user can change)
     - **Rule 3:** Facility + no partner → default No (user can change)
   - Quick Estimate generates `monthly_adjusted` cost

4. **Financial Assessment** (`assessments.py`)
   - Multi-module flow (assets, income, expenses, insurance, etc.)
   - Stores financial profile in session state
   - Calculates runway, shortfall, recommendations

5. **Expert Review** (`expert_review.py`)
   - Aggregates GCP + Cost Planner + Financial Assessment
   - Generates summary PDF (optional)
   - Publishes to MCIP (if configured)

6. **Navi AI Assistant** (feature-flagged)
   - If `FEATURE_LLM_NAVI` enabled → LLM-generated guidance
   - Otherwise → Stock copy from config

---

## 🏗️ Component Architecture

### **Core Services** (`core/`)

| Module | Purpose | Used By |
|--------|---------|---------|
| `flags.py` | Feature flag definitions + registry | All products |
| `state.py` | Session state initialization | `app.py` (entry) |
| `nav.py` | Navigation engine (loads `config/nav.json`) | `app.py` |
| `ui.py` | HTML/CSS injection, image helpers | All pages |
| `paths.py` | Path resolution (static assets, configs) | All products |
| `mcip.py` | MCIP integration (external API) | Cost Planner, GCP |
| `events.py` | Event logging (optional) | All products |

### **Product Pattern** (`products/<name>/`)

```
product.py           # Entry point with render() function
├── modules/         # JSON configs (questions, assessments)
├── utils/           # Product-specific helpers
└── ui/              # Optional: UI components (future)
```

**Key Products:**
- **GCP v4:** Question flow → scoring → recommendation
- **Cost Planner v2:** Quick Estimate → Financial Assessment → Expert Review
- **Advisor Prep:** Duck badge gamification for advisor readiness
- **Senior Trivia:** Educational health trivia game
- **AI Advisor (FAQ):** RAG-based Q&A with FAQ retrieval, corporate knowledge, and LLM-generated answers

### **Hub Pattern** (`hubs/`)

Flat structure (no subdirectories):
- `concierge.py` → Main hub with product tiles
- `learning.py` → Educational resources
- `partners.py` → Partner ecosystem
- `professional.py` → Professional tools

### **Page Pattern** (`pages/`)

Flat structure (no subdirectories):
- `welcome.py` → Landing page
- `login.py`, `signup.py` → Auth flows
- `faq.py` → AI Advisor with RAG-based Q&A (headerless, immersive chat UI)
- `_stubs.py` → Shared page stubs (about, logout, etc.)

---

## 📜 Import Rules

### ✅ **ALLOWED**

1. **Products import core:**
   ```python
   from core.flags import get_flag
   from core.ui import render_header
   from core.paths import get_static
   ```

2. **Products import their own utils:**
   ```python
   # In products/cost_planner_v2/intro.py
   from products.cost_planner_v2.utils.cost_calculator import CostCalculator
   ```

3. **Products import shared utilities:**
   ```python
   from products.resources_common.coming_soon import render_coming_soon
   ```

4. **Pages/hubs import products:**
   ```python
   # In pages/welcome.py
   from products.gcp_v4.product import render as render_gcp
   ```

### ❌ **DISCOURAGED**

1. **Cross-product imports** (creates coupling):
   ```python
   # DON'T DO THIS
   from products.gcp_v4.logic import compute_recommendation
   # Instead, store in session state and read via core helpers
   ```

2. **Hardcoded static paths:**
   ```python
   # DON'T DO THIS
   image_path = "static/images/logo.png"
   # Instead, use helper
   from core.paths import get_static
   image_path = get_static("images/logo.png")
   ```

3. **Importing from legacy paths:**
   ```python
   # BLOCKED BY PRE-COMMIT
   from products.gcp_v1 import ...
   from products.gcp_v2 import ...
   ```

### 🛡️ **Enforced by Pre-Commit**

- ❌ No imports from `products.gcp_v1/v2/v3`
- ❌ No more than 1 `module.json` under `products/`
- ❌ No backup files (`.bak*`) staged for commit

---

## 🗄️ State Management

### **Session State Keys** (Streamlit `st.session_state`)

| Key | Type | Owner | Purpose |
|-----|------|-------|---------|
| `gcp_answers` | dict | GCP | User's GCP question answers |
| `gcp_recommendation_category` | str | GCP | Derived recommendation (in_home, AL, MC, etc.) |
| `gcp_flags` | dict | GCP | Feature flags set by answers (has_partner, etc.) |
| `cp_keep_home` | bool | Cost Planner | Whether home is kept after move |
| `cp_monthly_adjusted` | float | Cost Planner | Adjusted monthly cost estimate |
| `fa_profile` | dict | Cost Planner | Financial assessment data |
| `mcip_published` | bool | Cost Planner | Whether results published to MCIP |
| `user_context` | dict | Core | Role, auth status, flags |

### **Persistence**

- **Session-based:** All data in `st.session_state` (ephemeral)
- **Local files:** `data/users/<username>.json` (gitignored except demo/)
- **External API:** MCIP integration (optional, configurable)

---

## 🎯 Feature Flag System

### **Flag Definition** (`core/flags.py`)

```python
FlagDefinition(
    key="has_partner",
    category=FlagCategory.CAREGIVER,
    severity=FlagSeverity.LOW,
    label="Has spouse or partner",
    description="User has a spouse or partner"
)
```

### **Flag Sources**

1. **GCP Questions:** Set via question options in `module.json`
   ```json
   {
     "value": "spouse",
     "label": "With a spouse or partner",
     "flags": ["has_partner"]
   }
   ```

2. **Manual:** Set programmatically in product logic
   ```python
   from core.flag_manager import set_flag
   set_flag("has_partner", True)
   ```

3. **Derived:** Computed from answers
   ```python
   if gcp_recommendation_category in ["assisted_living", "memory_care"]:
       set_flag("is_move_flexible", answers.get("move_preference") == "flexible")
   ```

### **Flag Usage**

```python
from core.flags import get_flag

if get_flag("has_partner"):
    # Show partner-specific UI
    render_keep_home_question(default=True)
else:
    render_keep_home_question(default=False)
```

---

## 🔌 External Integrations

### **MCIP (My Care Insights Platform)**
- **Module:** `core/mcip.py`
- **Purpose:** Publish financial assessment results
- **Usage:** Cost Planner Expert Review → Publish button
- **Config:** Environment vars or `config/mcip.json`

### **LLM/AI Assistant** (Feature-Flagged)
- **Flag:** `FEATURE_LLM_NAVI`
- **Module:** `core/navi.py`
- **Purpose:** AI-generated guidance messages
- **Fallback:** Stock copy if disabled

### **AI Advisor / FAQ System** (`pages/faq.py`)
- **Architecture:** Multi-tier retrieval + LLM synthesis with intelligent fallback
- **Components:**
  - **Mini-FAQ:** Curated identity questions (instant answers, no LLM)
  - **Corporate Knowledge:** RAG over company documentation (stored in `config/corp_knowledge.jsonl`, 3,110 chunks, 2.5 MB)
  - **FAQ Database:** RAG over care planning FAQs (stored in `config/faq.json`)
  - **Easter Eggs:** Hidden dev-mode responses for testing
- **Retrieval:** TF-IDF + cosine similarity (sklearn)
- **LLM Integration:** OpenAI GPT-4o-mini for answer synthesis
- **Routing Logic:**
  - **Identity Keywords:** "cca", "leadership", "about", "founded" → Corp first
  - **Geographic Keywords:** "seattle", "washington state", "pacific northwest" → Corp first
  - **Care Type Keywords:** "senior living", "assisted living", "memory care" → Corp first
  - **Service Keywords:** "how do you", "advisory", "consultation", "free service" → Corp first
  - **Post-Move Keywords:** "after moving", "follow-up", "adjustment", "transition support" → Corp first
  - **Fallback Path:** FAQ retrieval fails → Try corp corpus → Final fallback message
- **UI Features:**
  - Headerless design (custom nav hidden, Streamlit controls preserved)
  - Newest-first message ordering (typical chat pattern)
  - Recommended question chips for quick access
  - Input repositioned below recommended questions
  - CSS spacing utilities for visual polish
- **Message Flow:**
  1. User query → Mini-FAQ check (instant canonical answers)
  2. If not found → Route to corporate knowledge (identity/care/geo queries) or FAQ (care planning)
  3. Retrieve top K chunks → LLM synthesis with sources
  4. **If FAQ fails** → Fallback to corp corpus retrieval (with "Based on our guides:" prefix)
  5. **If both fail** → Show "not in FAQ yet" with GCP CTA
  6. Display with badges (canonical, instant, fallback, easter egg markers)
  7. Insert at chat[0] for newest-first display
- **Session State:**
  - `faq_chat`: List of message dicts (role, text, sources, CTAs)
  - `faq_processing`: Boolean flag for disable-during-response
  - `faq_composer_input`: Input field value (managed by Streamlit)

### **Hours/Day Suggestion** (Guarded Hybrid)
- **Flag:** `FEATURE_GCP_HOURS` (`off` | `shadow` | `assist`)
- **Modules:** `ai/hours_schemas.py`, `ai/hours_engine.py`
- **Purpose:** Suggest hours/day of care support using baseline + LLM refinement
- **Architecture:**
  - **Baseline:** Transparent rule-based logic (ADLs, falls, mobility, safety)
    - `<1h`: Minimal support (0-1 BADLs, independent)
    - `1-3h`: Moderate support (2 BADLs or 3+ IADLs or mobility aid)
    - `4-8h`: Substantial support (3+ BADLs or multiple falls or risky behaviors)
    - `24h`: Round-the-clock care (only via LLM escalation from 4-8h floor)
  - **LLM Refinement:** Schema-validated adjustment (max ±1 step from baseline)
    - Pydantic v2 validation ensures only 4 allowed bands
    - Off-menu outputs (e.g., "2-4h", "6h") rejected
    - Provides 1-3 short reasons + confidence score
  - **Modes:**
    - `off`: No suggestion (default)
    - `shadow`: Compute suggestion, log to console, no UI
    - `assist`: Show suggestion to user (non-binding hint)
- **Integration Points:**
  - `logic.py`: Builds `HoursContext` from answers/flags, calls engine
  - `product.py`: Renders suggestion UI on daily_living section (assist only)
  - `ui_helpers.py`: Formats suggestion as compact hint above question
- **Guardrails:**
  - User always in control (suggestion is NON-BINDING)
  - Baseline rules documented and tunable
  - LLM cannot invent bands outside 4 allowed values
  - Shadow mode enables safe A/B testing before assist rollout

---

## 🧪 Testing Strategy

### **Smoke Tests** (`tests/smoke_imports.py`)
- Basic import checks (no runtime execution)
- Catches missing dependencies, syntax errors

### **Unit Tests** (`tests/test_*.py`)
- GCP logic tests (scoring, recommendation)
- Cost calculator tests
- Flag manager tests

### **Integration Tests** (Future)
- Full GCP → Cost Planner flow
- MCIP publication

---

## 📦 Deployment

### **Streamlit Cloud**
- Entry point: `app.py`
- Secrets: `.streamlit/secrets.toml` (gitignored)
- Static assets: Deployed with app

### **Docker** (Optional)
```dockerfile
FROM python:3.13-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["streamlit", "run", "app.py"]
```

---

## 🎨 UI Architecture & Patterns

### **Header System**
- **Global Header:** `ui/header_simple.py` - Navigation header with logo and nav links
- **Per-Page Control:** Pages can hide header for immersive experiences
- **CSS Override Pattern:** Use `.sn-header { display: none !important; }` to hide custom nav while preserving Streamlit controls

### **Chat Interface Pattern** (AI Advisor)
- **Message Ordering:** Newest-first (insert at index 0)
- **Component Hierarchy:**
  1. Recommended question chips
  2. Input composer (text field + send button)
  3. Chat transcript (scrollable message list)
  4. Controls (clear chat, back to hub)
- **Spacing Utilities:**
  - `.ai-rec-wrapper` - Recommended questions spacing
  - `.ai-chip-row` - Chip button row spacing
  - `.ai-input-wrap` - Input composer spacing
- **Visual Design:**
  - Gradient background: `radial-gradient(circle at 10% -20%, #eef3ff 0%, #ffffff 58%)`
  - Rounded containers with subtle shadows
  - User messages: dark background (#0f172a)
  - Assistant messages: light gradient (#ffffff → #f5f7ff)
  - Badges for message types (instant, canonical, easter egg)

### **Responsive Design**
- Mobile-first approach with breakpoints at 640px, 1024px
- Flexbox layouts for adaptive spacing
- Container max-width: 1080px (centered)

---

## 📝 Recent Architectural Changes

### **Hub Reorganization (Oct 2025)**
- Consolidated duplicate product shims into canonical hub-based paths
- Created `products/global/` for shared utilities
- Removed 13+ duplicate product directories
- Fixed 26+ import path references
- Normalized all helper imports to canonical locations
- Result: Cleaner dependency graph, no circular imports

### **AI Advisor UI Polish (Oct 2025)**
- Implemented newest-first message ordering (chat.insert(0) pattern)
- Repositioned input composer below recommended questions for better UX flow
- Added CSS spacing utilities for visual polish
- Hidden custom navigation header while preserving Streamlit developer controls
- Fixed Python 3.9 type hint compatibility (str | None → Optional[str])
- Fixed Streamlit widget state management (removed problematic input clearing)

### **Type System Improvements (Oct 2025)**
- Migrated from Python 3.10+ union syntax to typing.Optional for 3.9 compatibility
- Updated core/ui.py with proper type hints
- Ensured venv uses Python 3.11.14 for development

### **Data Loader Enhancements (Oct 2025)**
- Added robust path resolution for home costs CSV and VA rates JSON
- Improved error handling with fallback mechanisms
- Automatic file discovery for latest VA rates

---

## 🔧 Development Workflow

1. **Local Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Run App:**
   ```bash
   streamlit run app.py
   ```

3. **Pre-Commit Checks:**
   ```bash
   make lint    # Ruff linting
   make type    # Mypy type checking
   make smoke   # Import smoke tests
   ```

4. **Commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit hook runs automatically
   ```

---

## 🔄 Data Flow Examples

### **Example 1: GCP → Cost Planner**

```python
# 1. User completes GCP (products/gcp_v4/product.py)
st.session_state["gcp_answers"] = {
    "living_situation": "spouse",
    "daily_living": {"bathing": 3, "dressing": 2},
    # ... other answers
}
st.session_state["gcp_recommendation_category"] = "assisted_living"
st.session_state["gcp_flags"] = {"has_partner": True}

# 2. Cost Planner Intro reads recommendation (products/cost_planner_v2/intro.py)
recommendation = st.session_state.get("gcp_recommendation_category")
has_partner = st.session_state.get("gcp_flags", {}).get("has_partner", False)

# 3. Apply keep_home logic (prepare_quick_estimate.py)
if recommendation == "in_home":
    st.session_state["cp_keep_home"] = True  # Locked
elif recommendation in ["assisted_living", "memory_care"]:
    if has_partner:
        st.session_state["cp_keep_home"] = True  # Default, changeable
    else:
        st.session_state["cp_keep_home"] = False  # Default, changeable

# 4. Calculate costs
monthly_cost = calculate_quick_estimate(
    recommendation=recommendation,
    keep_home=st.session_state["cp_keep_home"]
)
st.session_state["cp_monthly_adjusted"] = monthly_cost
```

### **Example 2: Feature Flag Usage**

```python
# Set flag via GCP question (module.json)
# User selects "With a spouse or partner" → flag "has_partner" set

# Use flag in Cost Planner (prepare_quick_estimate.py)
from core.flags import get_flag

if get_flag("has_partner"):
    st.info("🏠 A spouse or partner may remain at home...")
    default_keep_home = True
else:
    st.info("🏠 Will the home continue to be maintained...")
    default_keep_home = False
```

---

## 📚 Further Reading

- [REPO_STRUCTURE.md](./REPO_STRUCTURE.md) - Directory layout and conventions
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Development guidelines
- [Streamlit Docs](https://docs.streamlit.io/) - Framework reference
