# Navi Intelligence Enhancement - Testing Guide

## Quick Start

### Enable the Enhancement

**Option 1: Environment Variable**
```bash
export FEATURE_NAVI_INTELLIGENCE=on
python -m streamlit run app.py
```

**Option 2: In-App (Admin)**
```python
# In app.py or settings page
st.session_state["flag_FEATURE_NAVI_INTELLIGENCE"] = "on"
```

**Option 3: Shadow Mode (Testing)**
```bash
export FEATURE_NAVI_INTELLIGENCE=shadow
# Logs enhanced messages to console without displaying them
```

---

## Feature Flag Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `off` (default) | Static messages only | Production safety - no changes |
| `shadow` | Enhanced logic runs, logs output, shows static | Safe testing - compare outputs |
| `on` | Full MCIP-driven contextual guidance | Active deployment |

---

## What to Test

### 1. Hub Lobby - Flag-Aware Encouragement

**Test Scenario: Falls Risk**
1. Complete GCP with falls risk (answer "multiple falls" in Safety section)
2. Return to hub lobby
3. Expected: Navi encouragement shows 🛡️ with "Given the fall risk, finding the right support level is critical."

**Test Scenario: Memory Support**
1. Complete GCP with memory decline (answer questions showing memory issues)
2. Return to hub lobby
3. Expected: Navi shows 🧠 with "Memory support options will give you peace of mind and safety."

**Test Scenario: Veteran**
1. Complete GCP, select veteran status
2. Return to hub lobby
3. Expected: Navi shows 🎖️ with "As a veteran, you may qualify for Aid & Attendance benefits—up to $2,431/month."

**Test Scenario: High Confidence + Low Risk**
1. Complete GCP fully (90%+ questions) with minimal care needs
2. Return to hub lobby
3. Expected: Navi shows ✅ with "Your plan is crystal clear—let's move forward with confidence."

### 2. Hub Lobby - Dynamic Reason Text

**Test Scenario: After GCP with Memory Care**
1. Complete GCP, get Memory Care recommendation
2. Hub lobby reason text should mention: "Memory Care costs more but provides specialized support."

**Test Scenario: After GCP with Assisted Living + Falls**
1. Complete GCP with falls risk, get Assisted Living
2. Hub lobby reason text should mention: "Now let's see what fall prevention services cost..."

**Test Scenario: After Cost Planner with Funding Gap**
1. Complete Cost Planner with $1,664/month gap
2. Hub lobby reason text should mention: "Your advisor will help you close the $1,664/month gap..."

### 3. Cost Planner - Tier-Specific Intro (Phase 2)

**Note:** `get_cost_planner_intro()` is implemented but not yet wired into Cost Planner UI.

To test the logic:
```python
from core.navi_intelligence import NaviCommunicator
from core.navi import NaviOrchestrator

ctx = NaviOrchestrator.get_context(location="hub")
intro = NaviCommunicator.get_cost_planner_intro(ctx)
print(intro)
```

Expected outputs:
- **Memory Care:** "Memory Care typically costs $6,000-9,000/month"
- **Assisted Living:** "Assisted Living typically costs $4,500-6,500/month"
- **In-Home Care:** "In-Home Care costs vary widely by hours needed"
- **Independent:** "Independent Living typically costs $2,500-4,000/month"

---

## Testing Workflow

### End-to-End Test (Feature On)

```bash
# 1. Enable feature
export FEATURE_NAVI_INTELLIGENCE=on

# 2. Start app
python -m streamlit run app.py

# 3. Create new session (or reset)
# Go to Hub Lobby → "Start Fresh" or clear browser session

# 4. Complete GCP with specific answers
# - Select "multiple falls" in Safety section
# - Select "moderate memory issues" in Cognitive section
# - Select veteran status in Demographics

# 5. Return to Hub Lobby
# Verify Navi panel shows:
# - Icon: 🛡️ (falls risk has priority)
# - Text: "Fall risk plus memory support needs—safety is the priority."
# - Status: urgent (red/orange styling)
# - Reason: "Now let's see what fall prevention services cost and how to fund them."

# 6. Complete Cost Planner
# - Add income sources (simulate $3,000/month)
# - Add assets (simulate $100,000)
# - Get estimate (e.g., $5,200/month → $2,200 gap → 45 month runway)

# 7. Return to Hub Lobby
# Verify Navi panel shows:
# - Reason: "Your advisor will help you close the $2,200/month gap through VA benefits..."
```

### Shadow Mode Test (Compare Outputs)

```bash
# 1. Enable shadow mode
export FEATURE_NAVI_INTELLIGENCE=shadow

# 2. Start app with console visible
python -m streamlit run app.py 2>&1 | tee navi_shadow.log

# 3. Complete GCP with various flags
# Watch console for [NAVI_SHADOW] logs

# 4. Compare static vs enhanced
# Static shows: "You're making great progress!"
# Enhanced logs: "[NAVI_SHADOW] Enhanced: {'icon': '🛡️', 'text': 'Given the fall risk...', 'status': 'urgent'}"

# 5. Review log file
cat navi_shadow.log | grep NAVI_SHADOW
```

### Unit Test Validation

```bash
# Install pytest (if not already)
pip install pytest

# Run Navi Intelligence tests
pytest tests/test_navi_intelligence.py -v

# Expected output:
# test_falls_risk_flag_triggers_urgent PASSED
# test_memory_support_flag_triggers_important PASSED
# test_multiple_urgent_flags PASSED
# test_low_runway_triggers_financial_urgency PASSED
# test_high_confidence_low_risk_positive PASSED
# test_veteran_flag_callout PASSED
# ... 24 tests total
```

---

## Debugging

### Check Feature Flag Value

```python
from core.flags import get_flag_value

# In Streamlit app or Python shell
mode = get_flag_value("FEATURE_NAVI_INTELLIGENCE", "off")
print(f"Navi Intelligence mode: {mode}")
```

### Inspect NaviContext

```python
from core.navi import NaviOrchestrator

ctx = NaviOrchestrator.get_context(location="hub")

print(f"Care Recommendation: {ctx.care_recommendation}")
print(f"Tier: {ctx.care_recommendation.tier if ctx.care_recommendation else None}")
print(f"Flags: {ctx.care_recommendation.flags if ctx.care_recommendation else None}")
print(f"Financial Profile: {ctx.financial_profile}")
print(f"Runway: {ctx.financial_profile.runway_months if ctx.financial_profile else None}")
```

### Test Message Selection Logic

```python
from core.navi_intelligence import NaviCommunicator
from core.navi import NaviOrchestrator

# Get current context
ctx = NaviOrchestrator.get_context(location="hub")

# Test each method independently
encouragement = NaviCommunicator.get_hub_encouragement(ctx)
print(f"Encouragement: {encouragement}")

reason = NaviCommunicator.get_dynamic_reason_text(ctx)
print(f"Reason: {reason}")

intro = NaviCommunicator.get_cost_planner_intro(ctx)
print(f"Cost Intro: {intro}")

strategy = NaviCommunicator.get_financial_strategy_advice(ctx)
print(f"Strategy: {strategy}")
```

---

## Common Issues

### Issue: Enhanced messages not showing

**Symptoms:** Hub lobby shows generic "You're making great progress!" even with feature on

**Possible Causes:**
1. Feature flag not set correctly
2. MCIP data not available (GCP not completed)
3. Flags not active (answers didn't trigger flags)

**Fix:**
```python
# Check flag value
from core.flags import get_flag_value
print(get_flag_value("FEATURE_NAVI_INTELLIGENCE"))  # Should be "on"

# Check MCIP data
from core.mcip import MCIP
care_rec = MCIP.get_care_recommendation()
print(care_rec)  # Should have tier, flags, confidence
```

### Issue: Shadow mode not logging

**Symptoms:** No [NAVI_SHADOW] logs in console

**Possible Causes:**
1. Feature flag set to "off" instead of "shadow"
2. Console output redirected
3. Streamlit buffering console output

**Fix:**
```bash
# Ensure flag is "shadow"
echo $FEATURE_NAVI_INTELLIGENCE  # Should print "shadow"

# Run with console output
python -m streamlit run app.py 2>&1 | grep NAVI_SHADOW
```

### Issue: Tests failing

**Symptoms:** pytest errors or assertion failures

**Possible Causes:**
1. pytest not installed
2. NaviContext dataclass mismatch
3. MCIP contracts changed

**Fix:**
```bash
# Install pytest
pip install pytest

# Run with verbose output
pytest tests/test_navi_intelligence.py -v -s

# Run specific test
pytest tests/test_navi_intelligence.py::TestHubEncouragement::test_falls_risk_flag_triggers_urgent -v
```

---

## Rollback Plan

### Disable Feature Immediately

```bash
# Option 1: Environment variable
export FEATURE_NAVI_INTELLIGENCE=off

# Option 2: In-app
st.session_state["flag_FEATURE_NAVI_INTELLIGENCE"] = "off"

# Option 3: Restart app (flag defaults to "off")
# Just restart Streamlit - no code changes needed
```

### Revert Code Changes

```bash
# If needed to fully revert
git checkout main -- core/navi.py core/flags.py

# Or revert entire feature branch
git checkout main
git branch -D feature/navi-enhancement
```

---

## Performance Notes

### Minimal Overhead

- **NaviCommunicator methods:** ~1-2ms per call (simple dict operations)
- **Feature flag check:** <0.1ms (simple string comparison)
- **Memory impact:** Negligible (no large data structures)

### When Performance Matters

- Hub lobby renders once per navigation (not on every rerun)
- MCIP data already fetched (no additional I/O)
- Message selection is in-memory dictionary lookups

**Recommendation:** No performance concerns for Phase 1. Monitor if Phase 3 adds LLM enhancement.

---

## Phase 2 Preview

**Not Yet Implemented (Coming Next):**
- Context chip badges (confidence, urgency, risk count)
- GCP step-by-step coaching
- Cost Planner intro wiring
- Financial strategy display in Expert Review

**When Ready:**
1. Phase 2 will add UI components (new context chips)
2. Wire `get_cost_planner_intro()` into Cost Planner product
3. Add GCP module guidance with `get_gcp_step_coaching()`
4. Implement financial strategy display in Expert Review page

---

## Contact / Questions

**Feature Owner:** Navi Enhancement Team  
**Branch:** `feature/navi-enhancement`  
**Documentation:** See `NAVI_ENHANCEMENT_PROPOSAL.md` for full strategy  
**Implementation Summary:** See `PHASE_1_SUMMARY.md`

**Questions?**
- Check proposal: Open `NAVI_ENHANCEMENT_PROPOSAL.md`
- Review tests: Open `tests/test_navi_intelligence.py`
- Inspect code: Open `core/navi_intelligence.py`
