# Senior Trivia Architecture & Data Flow Verification

## Architecture Hierarchy

```
MCIP (App Brain)
├── Navi (Member Interaction Layer)
└── Hubs
    └── Waiting Room Hub
        └── Product Tiles (UI components)
            └── Senior Trivia Product Tile
                └── Senior Trivia Product
                    └── Modules (Individual Quiz Games)
                        ├── Truths & Myths Module
                        ├── Music Trivia Module
                        ├── Medicare Quiz Module
                        ├── Healthy Habits Module
                        └── Community Challenge Module
```

## Component Definitions

### **Hub** = Waiting Room
- **File:** `hubs/waiting_room.py`
- **Role:** Container for multiple product tiles, manages hub-level UI
- **Renders:** Multiple `ProductTileHub` instances
- **Data Responsibilities:**
  - Reads aggregate product progress
  - Displays product tiles with badges/progress
  - No direct module knowledge

### **Product Tile** = UI Component (ProductTileHub class)
- **File:** `core/product_tile.py` (class definition)
- **Role:** Visual representation of a product on hub page
- **Data Source:** Props passed from hub (progress, badges, status)
- **Rendered By:** Hub (waiting_room.py creates tile instances)
- **Example Usage:**
  ```python
  ProductTileHub(
      key="senior_trivia",
      progress=20,  # From hub calculation
      badges=["Gold", "Silver"],  # From hub retrieval
      ...
  )
  ```

### **Product** = Senior Trivia & Brain Games
- **File:** `products/senior_trivia/product.py`
- **Role:** Product-level logic, module selection hub, results rendering
- **Contains:** Multiple modules (quiz games)
- **Data Responsibilities:**
  - Aggregate module progress → product progress
  - Persist badges to shared state
  - Update both modern (product_tiles_v2) and legacy (tiles) structures

### **Modules** = Individual Quiz Games
- **Files:** `products/senior_trivia/modules/*.json`
- **Role:** Individual quiz content and configuration
- **Examples:**
  - `truths_myths` - Senior Living quiz
  - `music_trivia` - 1950s-1980s entertainment
  - `medicare_quiz` - Enrollment & coverage
  - `healthy_habits` - Longevity tips
  - `community_challenge` - Family trivia

### **MCIP** = Master Care Intelligence Panel
- **File:** `core/mcip.py`
- **Role:** App brain - orchestrates user journey across all products
- **Data Source:** Reads `st.session_state["tiles"]` for product status
- **Responsibilities:**
  - Track completed products
  - Determine next recommended action
  - Provide journey context to Navi

### **Navi** = Navigation Panel
- **File:** `core/navi.py`
- **Role:** Member interaction layer - shows progress, guidance, next steps
- **Data Source:** MCIP context + `st.session_state["tiles"]`
- **Rendered:** At product and hub levels
- **Responsibilities:**
  - Display journey progress
  - Show next recommended action
  - Provide contextual guidance

---

## Data Contract Flow

### 1. Module Completion → Product State

**Trigger:** User completes a trivia module
**Function:** `products/senior_trivia/product.py:_award_and_persist_badge()`

**Writes to TWO locations:**

#### A. Modern Structure (Detailed):
```python
st.session_state["product_tiles_v2"]["senior_trivia_hub"] = {
    "badges_earned": {
        "truths_myths": {"name": "Gold ⭐⭐⭐", "level": "gold", "score": "87"},
        "music_trivia": {"name": "Silver ⭐⭐", "level": "silver", "score": "62"}
    },
    "total_points": 149,
    "modules_completed": ["truths_myths", "music_trivia"]
}
```
**Purpose:** Detailed badge tracking, module-level data

#### B. Legacy Structure (Aggregate):
```python
st.session_state["tiles"]["senior_trivia"] = {
    "progress": 40,  # 2 of 5 modules = 40%
    "status": "doing",  # new | doing | done
    "badges_earned": {...},  # Copy of badge data
    "last_updated": "2025-10-16T10:30:00"
}
```
**Purpose:** MCIP/Navi compatibility, aggregate progress

**Code Implementation:**
```python
# Write to modern structure (product_tiles_v2)
tiles_v2["senior_trivia_hub"]["badges_earned"][module_key] = badge_data

# Calculate aggregate progress
completed_count = len(badges_earned)
progress_pct = (completed_count / 5) * 100

# Write to legacy structure (tiles) for MCIP/Navi
tiles_legacy["senior_trivia"]["progress"] = progress_pct
tiles_legacy["senior_trivia"]["status"] = "doing" if progress_pct < 100 else "done"
```

---

### 2. Hub Reads Product State

**File:** `hubs/waiting_room.py`
**Functions:** `_get_trivia_badges()`, `_get_trivia_progress()`

**Reads from:** Modern structure (`product_tiles_v2`)

```python
def _get_trivia_badges():
    tiles = st.session_state.get("product_tiles_v2", {})
    progress = tiles.get("senior_trivia_hub", {})
    badges_earned = progress.get("badges_earned", {})
    return [clean_badge_names...]

def _get_trivia_progress():
    tiles = st.session_state.get("product_tiles_v2", {})
    progress = tiles.get("senior_trivia_hub", {})
    completed = len(progress.get("badges_earned", {}))
    return (completed / 5) * 100  # Percentage
```

**Passes to:** `ProductTileHub` component

```python
ProductTileHub(
    key="senior_trivia",
    progress=_get_trivia_progress(),  # e.g., 40
    badges=_get_trivia_badges(),      # e.g., ["Gold", "Silver"]
    ...
)
```

---

### 3. ProductTileHub Renders Tile

**File:** `core/product_tile.py`
**Class:** `ProductTileHub`

**Receives:** Props from hub
- `progress` (0-100 percentage)
- `badges` (list of badge names)
- `status_text` (optional status override)

**Renders:**
- Progress pill if progress > 0
- Badge chips if badges provided
- Completion badge if progress >= 100

**Does NOT read session_state directly** - purely presentational

---

### 4. MCIP Reads Product Status

**File:** `core/mcip.py`
**Method:** `get_next_action()`, `initialize()`

**Reads from:** Legacy structure (`st.session_state["tiles"]`)

```python
tiles = st.session_state.get("tiles", {})
trivia_tile = tiles.get("senior_trivia", {})
trivia_progress = float(trivia_tile.get("progress", 0))
```

**Uses for:**
- Journey orchestration
- Determining next recommended product
- Tracking completed products

**Note:** MCIP currently focuses on GCP, Cost Planner, PFMA. Trivia is Waiting Room entertainment, not part of core journey flow.

---

### 5. Navi Reads Context

**File:** `core/navi.py`
**Function:** `render_navi_panel()`, `render_navi_panel_v2()`

**Data Sources:**
1. MCIP context (via `get_context()`)
2. Direct read from `tiles` for specific checks

```python
tiles = st.session_state.get("tiles", {})
gcp_tile = tiles.get("gcp_v4") or tiles.get("gcp", {})
cost_tile = tiles.get("cost_v2") or tiles.get("cost_planner", {})
```

**Uses for:**
- Showing incomplete GCP alerts
- Displaying journey progress
- Next action recommendations

---

## Current Implementation Status

### ✅ Correct Architecture

1. **Module Engine** writes to individual module tiles
   - `tiles["senior_trivia_truths_myths"]`
   - `tiles["senior_trivia_music_trivia"]`
   - Each has its own progress/state

2. **Product** aggregates module data
   - Reads individual module states
   - Writes aggregate to `product_tiles_v2["senior_trivia_hub"]`
   - Writes aggregate to `tiles["senior_trivia"]` (legacy)

3. **Hub** reads product-level data
   - Sources from `product_tiles_v2` (modern)
   - Calculates progress, retrieves badges
   - Passes props to `ProductTileHub` component

4. **ProductTileHub** receives props
   - Pure presentational component
   - No direct state reading
   - Renders progress/badges from props

5. **MCIP** reads legacy structure
   - Sources from `tiles` (aggregate)
   - Works with product-level progress
   - Compatible with existing system

6. **Navi** reads from multiple sources
   - MCIP context for journey state
   - Direct `tiles` reads for specific checks
   - Shows contextualized guidance

---

## Data Contract Summary

### Product → Hub Contract
```python
# Product writes (on badge award):
product_tiles_v2["senior_trivia_hub"] = {
    "badges_earned": {...},
    "total_points": int,
    "modules_completed": [...]
}

tiles["senior_trivia"] = {
    "progress": 0-100,
    "status": "new|doing|done",
    "badges_earned": {...}
}

# Hub reads (for tile rendering):
badges = _get_trivia_badges()  # from product_tiles_v2
progress = _get_trivia_progress()  # from product_tiles_v2

# Hub passes to component:
ProductTileHub(progress=progress, badges=badges)
```

### Product → MCIP Contract
```python
# Product writes:
tiles["senior_trivia"] = {
    "progress": int (0-100),
    "status": str ("new"|"doing"|"done")
}

# MCIP reads:
trivia_tile = tiles.get("senior_trivia", {})
trivia_progress = trivia_tile.get("progress", 0)
```

### MCIP → Navi Contract
```python
# MCIP provides context:
MCIPContext(
    next_action: dict,  # {'action', 'reason', 'route', 'status'}
    care_recommendation: CareRecommendation | None,
    financial_profile: FinancialProfile | None,
    ...
)

# Navi receives and displays:
render_navi_panel_v2(
    title=from_context,
    reason=from_context,
    encouragement=from_context,
    context_chips=from_context
)
```

---

## Verification Checklist

### ✅ Hub Level (waiting_room.py)
- [x] Reads from `product_tiles_v2` (modern)
- [x] Calculates progress from badge count
- [x] Passes props to `ProductTileHub`
- [x] Does not read individual module tiles

### ✅ Product Level (senior_trivia/product.py)
- [x] Aggregates module completions
- [x] Writes to both `product_tiles_v2` (modern) and `tiles` (legacy)
- [x] Each module has unique `config.product` key
- [x] Badge awards update aggregate progress

### ✅ Component Level (ProductTileHub)
- [x] Receives progress/badges as props
- [x] Pure presentational - no state reads
- [x] Renders progress pill when progress > 0
- [x] Displays badge chips from props

### ✅ MCIP Level (mcip.py)
- [x] Reads from `tiles` (legacy structure)
- [x] Works with product-level aggregates
- [x] Journey orchestration for core products
- [x] Trivia visible but not part of journey flow

### ✅ Navi Level (navi.py)
- [x] Reads MCIP context
- [x] Reads `tiles` for specific checks
- [x] Displays contextualized guidance
- [x] Compatible with product progress data

---

## Known Working Flow

1. User completes "Truths & Myths" quiz (module)
2. Product awards badge → writes to:
   - `product_tiles_v2["senior_trivia_hub"]["badges_earned"]["truths_myths"]`
   - `tiles["senior_trivia"]["progress"] = 20` (1/5 = 20%)
3. Hub reads from `product_tiles_v2`
4. Hub passes `progress=20, badges=["Gold"]` to `ProductTileHub`
5. Tile renders with 20% progress pill and Gold badge chip
6. MCIP reads `tiles["senior_trivia"]["progress"] = 20`
7. Navi can display trivia progress if needed

---

## Architecture Compliance: ✅ VERIFIED

All components follow the correct hierarchy and data contracts are properly communicated through the appropriate channels.

**Date:** October 16, 2025
**Branch:** demo-temp
**Status:** Architecture verified and compliant
