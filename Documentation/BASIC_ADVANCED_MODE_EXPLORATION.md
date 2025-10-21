# Basic/Advanced Mode Exploration & Implementation Plan

**Date:** October 19, 2025  
**Branch:** feature/basic-advanced-mode-exploration  
**Purpose:** Design and implement proper Basic/Advanced mode system with clean architecture

---

## Table of Contents
1. [Why Explore This Again?](#why-explore-this-again)
2. [Design Goals](#design-goals)
3. [Architecture Options](#architecture-options)
4. [Recommended Approach](#recommended-approach)
5. [Implementation Plan](#implementation-plan)
6. [Testing Strategy](#testing-strategy)

---

## Why Explore This Again?

### What We Removed
We previously removed the Basic/Advanced mode system because it was:
- ❌ Causing double-counting bugs
- ❌ Complex and hard to maintain
- ❌ Had sanitization issues during mode transitions
- ❌ Minimal UX benefit for the complexity cost

### Why Reconsider?
However, Basic/Advanced modes CAN provide value:
- ✅ **Reduces cognitive load** for users with simple finances
- ✅ **Progressive disclosure** - show complexity only when needed
- ✅ **Faster data entry** for common scenarios
- ✅ **Professional flexibility** - detailed breakdown for advisors

### The Key Question
**Can we implement Basic/Advanced modes WITHOUT the previous bugs and complexity?**

---

## Design Goals

### Must-Have Features
1. **No Double-Counting** - Only one data set used in calculations at a time
2. **Clean Mode Switching** - Seamless transition without data loss
3. **Clear User Feedback** - Users understand which mode they're in
4. **Maintainable Code** - Simple, predictable architecture
5. **Accurate Calculations** - Net Assets always correct

### Nice-to-Have Features
1. **Allocation Helper** - Convert Basic aggregate to Advanced breakdown
2. **Mode Memory** - Remember user's preference across sessions
3. **Smart Defaults** - Pre-fill common values in Advanced mode
4. **Progress Indicator** - Show % complete in each mode

---

## Architecture Options

### Option A: Single Source of Truth (Recommended)
**Concept:** Only store detail fields, calculate aggregates on-the-fly

**How It Works:**
```
Basic Mode:
- Show only aggregate fields (e.g., "Total Liquid Assets")
- User enters: $50,000
- Behind the scenes: Split evenly across detail fields
  - checking_balance: $25,000
  - savings_cds_balance: $25,000
- Aggregate is calculated, not stored

Advanced Mode:
- Show detail fields (checking, savings)
- User enters: checking=$30,000, savings=$20,000
- Aggregate displays as calculated label: $50,000
- Only detail fields stored
```

**Pros:**
- ✅ No double-counting (only detail fields stored)
- ✅ Mode switching is just UI change
- ✅ Calculations always use same data structure

**Cons:**
- ⚠️ Basic mode inputs need to be "distributed" to detail fields
- ⚠️ Distribution logic needed (even split, proportional, manual)

---

### Option B: Separate Data Sets with Mode Flag
**Concept:** Store both basic and advanced data, use mode flag to determine which to use

**How It Works:**
```
State Structure:
{
  "calculation_mode": "basic",  // or "advanced"
  
  // Basic mode data
  "cash_liquid_total": 50000,
  "brokerage_total": 100000,
  
  // Advanced mode data
  "checking_balance": 30000,
  "savings_cds_balance": 20000,
  "brokerage_mf_etf": 60000,
  "brokerage_stocks_bonds": 40000
}

Calculation:
if mode == "basic":
    use cash_liquid_total + brokerage_total
else:
    use (checking + savings) + (mf_etf + stocks)
```

**Pros:**
- ✅ Clear separation of data sets
- ✅ Easy to understand

**Cons:**
- ❌ Risk of data drift (both sets populated)
- ❌ Sanitization needed on mode switch
- ❌ Calculations must check mode flag

---

### Option C: Progressive Disclosure (No Mode)
**Concept:** Show basic fields first, expand to advanced on demand

**How It Works:**
```
Initial View:
- Cash & Savings: [$50,000] [+ Show Breakdown]

When "Show Breakdown" clicked:
- Cash & Savings: $50,000 (calculated)
  └─ Checking: [$30,000]
  └─ Savings/CDs: [$20,000]
  └─ [Hide Breakdown]

Always stores detail fields:
- checking_balance: 30000
- savings_cds_balance: 20000
```

**Pros:**
- ✅ Best UX (gradual complexity reveal)
- ✅ Single data model (only detail fields)
- ✅ No mode switching logic needed

**Cons:**
- ⚠️ Requires UI rework (collapsible sections)
- ⚠️ Still needs initial distribution logic

---

## Recommended Approach

### **Option A: Single Source of Truth** ✅

This is the cleanest architecture that solves all previous problems.

### Key Principles

1. **Always Store Detail Fields**
   - Never store aggregate totals in state
   - Aggregates are always calculated on render

2. **Basic Mode = Simplified Input**
   - Show aggregate input field
   - On blur/submit: distribute to detail fields using chosen strategy
   - Aggregate label immediately shows calculated sum

3. **Advanced Mode = Direct Input**
   - Show all detail fields
   - Aggregate displays as calculated label
   - No distribution needed

4. **Mode Toggle = UI Change Only**
   - Switching modes just changes field visibility
   - No data migration/sanitization needed
   - Same calculation logic always

5. **"Unallocated" Field = Informational Only** ⭐ NEW
   - When switching Basic → Advanced, show difference between original estimate and allocated detail
   - **Never included in financial calculations** (calculations only use detail fields)
   - User can: ignore it, clear original estimate, or move to "Other" category
   - Eliminates phantom money problem (over-estimates don't inflate Net Assets)

---

## Implementation Plan

### Phase 1: Core Infrastructure (2-3 hours)

#### 1.1 Update State Model
```python
# Session state structure
st.session_state["{assessment_key}_mode"] = "basic"  # or "advanced"

# Assessment state structure
state = {
    # Detail fields (ONLY source of truth for calculations)
    "checking_balance": 30000,
    "savings_cds_balance": 20000,
    
    # Original Basic mode entry (for Unallocated display only)
    "liquid_assets_total_entered": 100000,  # NOT used in calculations
    
    # Calculated aggregate (never stored, always computed)
    # "liquid_assets_total": 50000  # = checking + savings
}
```

**Critical Rule:** Calculations MUST only use detail fields. The `_entered` suffix indicates "user's original estimate" which is purely informational.

#### 1.2 Add Mode Toggle UI
```python
def render_mode_toggle(assessment_key: str) -> str:
    """Render mode toggle, return current mode."""
    mode_key = f"{assessment_key}_mode"
    current_mode = st.session_state.get(mode_key, "basic")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_mode = st.radio(
            label="Detail Level",
            options=["basic", "advanced"],
            format_func=lambda x: "⚡ Basic (Quick)" if x == "basic" else "📊 Advanced (Detailed)",
            index=0 if current_mode == "basic" else 1,
            horizontal=True,
        )
    
    st.session_state[mode_key] = selected_mode
    return selected_mode
```

#### 1.3 Update Field Type: `aggregate_input`
New field type that behaves differently in Basic vs Advanced mode:

```json
{
  "key": "cash_liquid_total",
  "label": "Checking & Savings (Total)",
  "type": "aggregate_input",
  "aggregate_from": ["checking_balance", "savings_cds_balance"],
  "distribution_strategy": "even",  // or "proportional", "manual"
  "help": "In Basic mode: enter total here. In Advanced mode: enter details below."
}
```

---

### Phase 2: Field Rendering Logic (3-4 hours)

#### 2.1 Update `_render_fields()` Function
```python
def _render_fields(section, state, mode="basic"):
    new_values = {}
    
    for field in section.get("fields", []):
        field_type = field.get("type")
        
        if field_type == "aggregate_input":
            # Render based on mode
            if mode == "basic":
                # Show as editable input
                value = _render_aggregate_input_basic(field, state)
                if value is not None:
                    # Store original entry for Unallocated calculation
                    new_values[f"{field['key']}_entered"] = value
                    # Distribute to detail fields
                    distributed = _distribute_aggregate(field, value, state)
                    new_values.update(distributed)
            else:
                # Show as calculated label
                aggregate_total = _calculate_aggregate(field, state)
                _render_aggregate_label(field, aggregate_total)
                
                # Show Unallocated field if switching from Basic
                _render_unallocated_field(field, state)
                
                # Don't store aggregate, only detail fields matter
        
        elif field.get("level") == "advanced":
            # Only show in advanced mode
            if mode == "advanced":
                value = _render_field(field, state)
                new_values[field["key"]] = value
        
        else:
            # Regular field, show in both modes
            value = _render_field(field, state)
            new_values[field["key"]] = value
    
    return new_values
```

#### 2.2 Distribution Strategies
```python
def _distribute_aggregate(field, total_value, state):
    """Distribute aggregate value to detail fields."""
    detail_fields = field.get("aggregate_from", [])
    strategy = field.get("distribution_strategy", "even")
    
    if strategy == "even":
        # Split evenly
        per_field = total_value / len(detail_fields)
        return {key: per_field for key in detail_fields}
    
    elif strategy == "proportional":
        # Split based on existing proportions
        current_total = sum(state.get(key, 0) for key in detail_fields)
        if current_total == 0:
            # No existing data, fall back to even split
            per_field = total_value / len(detail_fields)
            return {key: per_field for key in detail_fields}
        else:
            # Maintain proportions
            return {
                key: total_value * (state.get(key, 0) / current_total)
                for key in detail_fields
            }
    
    elif strategy == "manual":
        # Show modal for manual distribution
        return _show_distribution_modal(field, total_value, state)
```

#### 2.3 Unallocated Field Implementation ⭐
```python
def _render_unallocated_field(field, state):
    """
    Display Unallocated amount when user has original estimate from Basic mode.
    
    CRITICAL: Unallocated is NEVER included in calculations. It's purely informational.
    """
    aggregate_key = field["key"]
    detail_fields = field.get("aggregate_from", [])
    
    # Check if user has original estimate from Basic mode
    original_key = f"{aggregate_key}_entered"
    if original_key not in state:
        return  # No original estimate, nothing to show
    
    # Calculate allocated amount from detail fields
    original_estimate = state.get(original_key, 0)
    allocated_total = sum(state.get(field_key, 0) for field_key in detail_fields)
    unallocated = original_estimate - allocated_total
    
    # Only show if non-zero
    if abs(unallocated) < 0.01:
        return
    
    # Render informational display
    st.markdown(f"""
    <div style="background: #f0f7ff; padding: 12px; border-radius: 4px; margin: 12px 0;">
        <strong>📊 Unallocated:</strong> {format_currency(unallocated)}
        <br/>
        <small style="color: #666;">
            Your original estimate was {format_currency(original_estimate)}. 
            You've allocated {format_currency(allocated_total)} in the detail fields above.
            <br/>
            <em>Note: This amount is not included in calculations—only your detail entries matter.</em>
        </small>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Clear Original", key=f"clear_{aggregate_key}", help="Remove the original estimate"):
            del state[original_key]
            st.rerun()
    
    with col2:
        if st.button("Move to 'Other'", key=f"other_{aggregate_key}", help="Add unallocated to 'Other' category"):
            # Find the "other" field in this section
            other_field_key = _find_other_field(detail_fields)
            if other_field_key:
                state[other_field_key] = state.get(other_field_key, 0) + unallocated
                del state[original_key]
                st.rerun()
            else:
                st.error("No 'Other' category found in this section.")
    
    # Optional: Show warning if negative (user allocated MORE than original estimate)
    if unallocated < 0:
        st.warning(f"""
        ⚠️ Your detail entries total {format_currency(allocated_total)}, 
        which exceeds your original estimate of {format_currency(original_estimate)}.
        This is fine—your detail entries are what will be used in calculations.
        """)


def format_currency(value):
    """Format value as currency."""
    return f"${value:,.2f}" if value >= 0 else f"-${abs(value):,.2f}"


def _find_other_field(detail_fields):
    """Find the 'other' field in a list of detail fields."""
    for field_key in detail_fields:
        if "other" in field_key.lower():
            return field_key
    return None
```

**Key Design Decision:** Unallocated = 0 in all calculations. This means:
- ✅ User can over-estimate in Basic mode without inflating Net Assets
- ✅ User can under-estimate in Basic mode and correct in Advanced
- ✅ No urgency to resolve—calculations are always correct
- ✅ User controls cleanup (clear vs move to other vs ignore)


---

### Phase 3: Calculation Updates (1-2 hours)

#### 3.1 Ensure Calculations Use Detail Fields Only
No changes needed! Calculations already use detail fields:

```python
def calculate_total_asset_value(assets_data):
    """
    Always uses detail breakdown fields.
    
    CRITICAL: Never use aggregate fields or "_entered" fields in calculations.
    Only sum detail fields (checking_balance, savings_cds_balance, etc.)
    """
    liquid_assets = (
        assets_data.get("checking_balance", 0.0) +
        assets_data.get("savings_cds_balance", 0.0)
    )
    # ... etc
    return total
```

**Verification Checklist:**
- ✅ No `_total` fields referenced in calculations
- ✅ No `_entered` fields referenced in calculations
- ✅ Only detail fields (e.g., `checking_balance`, `savings_cds_balance`) summed
- ✅ Unallocated field never included

**Example of WRONG calculation:**
```python
# ❌ WRONG - includes aggregate
total = assets_data.get("liquid_assets_total", 0)  # Don't do this!
```

**Example of CORRECT calculation:**
```python
# ✅ CORRECT - only detail fields
total = (
    assets_data.get("checking_balance", 0) +
    assets_data.get("savings_cds_balance", 0)
)
```

#### 3.2 Verify No Aggregate Fields in MCIP Output
```python
# MCIP should only contain detail fields, never aggregates
{
  "financial_profile": {
    "assets": {
      "checking_balance": 30000,
      "savings_cds_balance": 20000,
      # NOT: "cash_liquid_total": 50000
    }
  }
}
```

---

### Phase 4: User Experience Enhancements (2-3 hours)

#### 4.1 Mode Guidance
Show clear messaging about current mode:

```python
if mode == "basic":
    st.info("""
    ⚡ **Basic Mode**: Enter totals for quick estimates.
    - Faster data entry
    - Good for simple finances
    - Switch to Advanced for detailed breakdown
    """)
else:
    st.info("""
    📊 **Advanced Mode**: Enter detailed values for accurate planning.
    - Granular tracking
    - Better for complex finances
    - Totals calculate automatically
    """)
```

#### 4.2 Mode Switching Feedback
```python
if st.session_state.get(f"{assessment_key}_mode_just_changed"):
    if mode == "advanced":
        st.success("""
        ✅ Switched to Advanced Mode
        Your total has been split evenly across detail fields.
        Adjust individual amounts below.
        """)
    else:
        st.success("""
        ✅ Switched to Basic Mode
        Your detail fields have been summed into totals.
        """)
    
    # Clear flag
    del st.session_state[f"{assessment_key}_mode_just_changed"]
```

#### 4.3 Distribution Preview (Advanced)
When user enters aggregate in Basic mode, show preview:

```python
if mode == "basic" and aggregate_value_changed:
    with st.expander("📋 Distribution Preview", expanded=True):
        st.write("This total will be split as:")
        distributed = _distribute_aggregate(field, aggregate_value, state)
        for key, value in distributed.items():
            label = _get_field_label(key)
            st.write(f"- {label}: ${value:,.2f}")
```

---

### Phase 5: Testing & Documentation (2-3 hours)

#### 5.1 Test Scenarios
1. **Basic Mode Entry**
   - Enter $50,000 in liquid assets
   - Verify checking = $25,000, savings = $25,000
   - Verify Net Assets = $50,000

2. **Advanced Mode Entry**
   - Enter checking = $30,000, savings = $20,000
   - Verify aggregate label shows $50,000
   - Verify Net Assets = $50,000

3. **Mode Switching: Basic → Advanced**
   - Start in Basic, enter $50,000
   - Switch to Advanced
   - Verify fields show $25,000 each (even distribution)
   - Verify "Unallocated: $0.00" (all allocated)
   - Edit checking to $40,000
   - Verify aggregate updates to $65,000
   - Verify "Unallocated: -$15,000" (over-allocated)
   - Verify Net Assets = $65,000 (NOT $50,000—uses detail fields only)

4. **Mode Switching: Advanced → Basic**
   - Start in Advanced, enter checking=$30k, savings=$20k
   - Switch to Basic
   - Verify aggregate shows $50,000
   - Edit aggregate to $60,000
   - Switch back to Advanced
   - Verify fields updated (e.g., checking=$36k, savings=$24k proportional)
   - Verify "Unallocated: $0.00"

5. **Calculation Consistency**
   - Enter same values in both modes
   - Verify Net Assets identical
   - Verify MCIP output identical
   - **CRITICAL:** Verify Net Assets uses detail fields only (ignores _entered and unallocated)

6. **Unallocated Field Behavior** ⭐ NEW
   - Enter $100k in Basic mode
   - Switch to Advanced, adjust to $70k total in detail fields
   - Verify "Unallocated: $30,000" displayed
   - Verify Net Assets = $70k (NOT $100k—unallocated ignored)
   - Click "Clear Original"
   - Verify Unallocated field disappears
   - Verify Net Assets still = $70k

7. **Over-Allocation Handling** ⭐ NEW
   - Enter $50k in Basic mode
   - Switch to Advanced, enter $80k total in detail fields
   - Verify "Unallocated: -$30,000" with warning message
   - Verify Net Assets = $80k (uses detail fields)
   - Click "Clear Original"
   - Verify warning disappears

---

## Implementation Checklist

### Core Infrastructure
- [ ] Add mode toggle component
- [ ] Update session state structure
- [ ] Add `aggregate_input` field type
- [ ] Implement distribution strategies (even, proportional)
- [ ] Implement Unallocated field display ⭐ NEW
- [ ] Add "Clear Original" and "Move to Other" buttons ⭐ NEW

### Field Rendering
- [ ] Update `_render_fields()` to respect mode
- [ ] Implement `_render_aggregate_input_basic()`
- [ ] Implement `_render_aggregate_label()`
- [ ] Implement `_render_unallocated_field()` ⭐ NEW
- [ ] Update field visibility logic

### JSON Configuration
- [ ] Update assets.json with `aggregate_input` fields
- [ ] Add `distribution_strategy` to aggregate fields
- [ ] Remove old `display_currency_aggregate` type

### Calculations
- [ ] Verify calculations use detail fields only ⭐ CRITICAL
- [ ] Verify calculations ignore `_entered` fields ⭐ NEW
- [ ] Verify calculations ignore Unallocated ⭐ NEW
- [ ] Add tests for both modes
- [ ] Ensure MCIP output excludes aggregates and `_entered` fields

### User Experience
- [ ] Add mode guidance messages
- [ ] Add mode switching feedback
- [ ] Add distribution preview
- [ ] Add help tooltips
- [ ] Add Unallocated explanation text ⭐ NEW
- [ ] Add over-allocation warning ⭐ NEW

### Testing
- [ ] Test Basic mode entry
- [ ] Test Advanced mode entry
- [ ] Test Basic → Advanced switching
- [ ] Test Advanced → Basic switching
- [ ] Test calculation consistency
- [ ] Test data persistence
- [ ] Test MCIP output
- [ ] Test Unallocated field display ⭐ NEW
- [ ] Test "Clear Original" button ⭐ NEW
- [ ] Test "Move to Other" button ⭐ NEW
- [ ] Test over-allocation warning ⭐ NEW
- [ ] Test that Unallocated = 0 in calculations ⭐ CRITICAL

### Documentation
- [ ] Update user guide
- [ ] Document architecture decisions
- [ ] Add code comments
- [ ] Create troubleshooting guide

---

## Success Criteria

### Technical
- ✅ No double-counting in any scenario
- ✅ Mode switching is seamless (no errors)
- ✅ Calculations consistent across modes
- ✅ Only detail fields stored in state/MCIP
- ✅ No data loss on mode switch

### User Experience
- ✅ Clear indication of current mode
- ✅ Helpful guidance for each mode
- ✅ Smooth mode transitions
- ✅ Aggregate values always accurate
- ✅ Distribution preview useful

### Code Quality
- ✅ Clean, maintainable architecture
- ✅ Single source of truth (detail fields)
- ✅ No complex sanitization logic
- ✅ Comprehensive test coverage
- ✅ Well-documented

---

## Timeline Estimate

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| 1 | Core Infrastructure | 2-3 hours | None |
| 2 | Field Rendering | 3-4 hours | Phase 1 |
| 3 | Calculation Updates | 1-2 hours | Phase 2 |
| 4 | UX Enhancements | 2-3 hours | Phase 3 |
| 5 | Testing & Docs | 2-3 hours | Phase 4 |
| **Total** | **Full Implementation** | **10-15 hours** | Sequential |

**Recommended Approach:** Implement in phases, test after each phase.

---

## Risk Assessment

### Low Risk ✅
- Mode toggle UI (simple component)
- Distribution strategies (straightforward math)
- Mode guidance messages (UI only)

### Medium Risk ⚠️
- Field rendering updates (multiple touch points)
- Mode switching UX (needs polish)
- Distribution preview (UI complexity)

### High Risk 🔴
- Complex distribution strategies (manual allocation)
- Edge cases in mode switching (data migration)
- Performance with many fields

**Mitigation:** Start with simple even distribution, add complexity later.

---

## Alternative: Progressive Disclosure

If Basic/Advanced modes prove too complex, consider **Progressive Disclosure**:

```
Initial View:
┌─────────────────────────────────┐
│ 💰 Liquid Assets        $50,000 │
│    [+ Show Details]             │
└─────────────────────────────────┘

Expanded View:
┌─────────────────────────────────┐
│ 💰 Liquid Assets        $50,000 │
│    [- Hide Details]             │
│                                 │
│    Checking:         [$30,000]  │
│    Savings/CDs:      [$20,000]  │
└─────────────────────────────────┘
```

**Pros:**
- Same single-source-of-truth architecture
- No "mode" concept to explain
- Natural progressive complexity
- Simpler implementation

**Cons:**
- Less clear "beginner vs advanced" distinction
- Still needs distribution logic for initial entry

---

## Next Steps

1. **Review this document** with stakeholders
2. **Choose approach**: Full Basic/Advanced OR Progressive Disclosure
3. **Create prototype** of Phase 1 (mode toggle)
4. **Test with users** to validate UX
5. **Iterate** based on feedback
6. **Implement** remaining phases

---

## Questions to Answer

1. **Distribution Strategy**: Even split or proportional? ✅ **Answered: Even split default, proportional option**
2. **Default Mode**: Start in Basic or Advanced? ⚠️ **Needs decision**
3. **Mode Memory**: Remember user's preference? ⚠️ **Needs decision**
4. **Manual Distribution**: Include manual allocation modal? ⚠️ **Needs decision** (Low priority)
5. **Progressive Disclosure**: Consider as alternative? ⚠️ **Deferred** (Can revisit if mode system too complex)
6. **Unallocated Field**: How to handle over/under estimates? ✅ **ANSWERED: Unallocated = 0 in calculations** ⭐

---

## Design Decision: Unallocated Field Architecture ⭐

### Problem Statement
When users switch from Basic to Advanced mode, they may have entered an aggregate estimate (e.g., $100k total) that doesn't match the sum of their detail fields after correction (e.g., $70k actual). How do we handle this discrepancy?

### Solution: "Unallocated = Zero in Calculations"

**Core Principle:** The Unallocated field is purely informational—it's NEVER included in financial calculations.

### Why This Works (Rating: 10/10)

#### ✅ Eliminates Phantom Money Problem
- User guesses $100k in Basic mode
- Corrects to $70k actual in Advanced mode
- Unallocated shows $30k (informational)
- **Net Assets = $70k** (NOT $100k—uses detail fields only)
- No risk of double-counting or inflated calculations

#### ✅ No Urgency to Resolve
User can:
- **Ignore it** → Calculations are already correct
- **Clear original estimate** → Makes Unallocated disappear from UI
- **Move to "Other" category** → Adds to a catch-all field
- **Think about it overnight** → No pressure

#### ✅ Handles Both Over and Under Estimates
- **Over-estimate:** Unallocated = +$30k → "You have $30k unaccounted for"
- **Under-estimate:** Unallocated = -$30k → "Your details exceed original by $30k (this is fine)"

#### ✅ Transparent Feedback
User sees exactly what's happening:
```
📊 Unallocated: $30,000.00
Your original estimate was $100,000. You've allocated $70,000 in the detail fields above.
Note: This amount is not included in calculations—only your detail entries matter.
```

#### ✅ User Control
Two clear action options:
- **Clear Original** → Remove the $100k estimate, Unallocated disappears
- **Move to 'Other'** → Add $30k to "Other Assets" field

### Implementation Details

**State Structure:**
```python
{
    # Original Basic mode input (for display only)
    "liquid_assets_total_entered": 100000,  # NOT in calculations
    
    # Detail fields (ONLY source for calculations)
    "checking_balance": 30000,  # ✅ In calculations
    "savings_cds_balance": 40000,  # ✅ In calculations
}
```

**Calculation Logic:**
```python
def calculate_total_asset_value(assets_data):
    # ONLY sum detail fields, ignore _entered
    total = (
        assets_data.get("checking_balance", 0) +
        assets_data.get("savings_cds_balance", 0)
        # ... other detail fields
    )
    # Unallocated is NOT added here!
    return total
```

**Display Logic:**
```python
original = state.get("liquid_assets_total_entered", 0)
allocated = checking + savings
unallocated = original - allocated  # Calculated, not stored

if unallocated != 0:
    st.info(f"Unallocated: {unallocated} (informational only)")
```

### Comparison with Alternatives

| Approach | Calc Correct? | User Pressure | Flexibility | Rating |
|----------|---------------|---------------|-------------|--------|
| **Unallocated = 0 in calcs** ⭐ | Always | None | High | 10/10 |
| Include Unallocated in calcs | No (inflates) | High | Low | 3/10 |
| Auto-clear after 30s | Always | Medium | Medium | 7/10 |
| Force immediate resolution | Always | Very high | Low | 5/10 |

### User Scenarios

**Scenario 1: Over-Estimate**
1. Basic mode: Enter $100k
2. Advanced mode: Actual is $70k
3. Result: Unallocated = $30k, Net Assets = $70k ✅
4. Action: User can clear or move to "Other"

**Scenario 2: Under-Estimate**
1. Basic mode: Enter $50k
2. Advanced mode: Actual is $80k
3. Result: Unallocated = -$30k (warning), Net Assets = $80k ✅
4. Action: User can clear (removes warning)

**Scenario 3: Ignore**
1. Basic mode: Enter $100k
2. Advanced mode: Actual is $70k
3. User ignores Unallocated field
4. Result: Net Assets = $70k (still correct!) ✅

### Success Criteria
- ✅ Calculations always use detail fields only
- ✅ Unallocated never inflates Net Assets
- ✅ User has clear, optional actions
- ✅ Over-estimates don't break anything
- ✅ Under-estimates show helpful warning
- ✅ Can ignore Unallocated forever with no consequences

---

**Ready to proceed?** Start with Phase 1 prototype! 🚀
