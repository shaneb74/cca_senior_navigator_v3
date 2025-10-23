# LLM Tier Replacement Policy Implementation

## Summary
Implemented a guarded "LLM as recommender" policy that allows the LLM to override the deterministic tier recommendation when safe and confident.

## Files Modified

### 1. `products/gcp_v4/modules/care_recommendation/logic.py`
**Added:**
- `get_llm_tier_mode()` - Feature flag resolver (FEATURE_GCP_LLM_TIER: off|shadow|replace)
- `_choose_final_tier()` - Policy function implementing guarded replacement rules

**Modified:**
- `ensure_summary_ready()` - Wired in tier decision policy after LLM advice generation

### 2. `products/gcp_v4/product.py`
**Modified:**
- Outcome building section to read `gcp.final_tier` from session state and override deterministic tier

### 3. `tools/test_tier_policy.py` (NEW)
Unit tests for tier replacement policy logic

## Policy Rules (mode="replace")

### 1. Basic Guards
- LLM tier MUST be in `allowed_tiers` (respects cognitive/behavioral gates)
- LLM confidence MUST be ≥ 0.80 for general acceptance
- No downgrades when risky behaviors require MC/MC-HA

### 2. Special De-overscore Rule
**When:**
- Deterministic says: memory_care or memory_care_high_acuity
- LLM says: assisted_living (with conf ≥ 0.80)
- Bands: moderate cognition × high support
- Gates removed MC/MC-HA (no risky behaviors)

**Then:** Accept LLM recommendation (AL)

**Rationale:** Moderate×high without risky behaviors often overshoots to MC; LLM can recognize when AL is more appropriate.

### 3. Risky Behavior Protection
**When:**
- Risky cognitive behaviors present
- Deterministic tier: MC or MC-HA
- LLM suggests downgrade (e.g., AL)

**Then:** Keep deterministic tier

**Rationale:** Risky behaviors (wandering, aggressive, etc.) require MC-level care regardless of other factors.

## Modes

### `FEATURE_GCP_LLM_TIER="off"`
- No LLM tier consideration
- Always use deterministic tier
- No logging

### `FEATURE_GCP_LLM_TIER="shadow"` (default)
- Compute LLM tier
- Always use deterministic tier
- Log decision with: `[GCP_TIER_DECISION] mode=shadow det=X llm=Y conf=Z -> final=X`

### `FEATURE_GCP_LLM_TIER="replace"`
- Compute LLM tier
- Apply policy rules to choose final tier
- Update `st.session_state["gcp.final_tier"]` with final decision
- Update `_summary_advice` tier for UI consistency
- Log decision with: `[GCP_TIER_DECISION] mode=replace det=X llm=Y conf=Z -> final=W reason=R`
- Append training case to `data/training/gcp_cases.jsonl`

## Session State Keys

### Input
- `_summary_advice` - LLM summary with tier/confidence (from `ensure_summary_ready`)
- Standard GCP answers/flags for gate computation

### Output
- `gcp.final_tier` - Final tier after policy application (read by product.py)
- `_summary_advice["tier"]` - Updated to match final tier (for UI consistency)

## Logging Examples

### Shadow Mode
```
[GCP_TIER_DECISION] mode=shadow det=memory_care llm=assisted_living conf=0.87 -> final=memory_care
```

### Replace Mode - LLM Accepted
```
[GCP_TIER_DECISION] mode=replace det=memory_care llm=assisted_living conf=0.87 -> final=assisted_living reason=de_overscore_accept_al
```

### Replace Mode - Deterministic Kept
```
[GCP_TIER_DECISION] mode=replace det=memory_care llm=assisted_living conf=0.87 -> final=memory_care reason=risky_behaviors_keep_det
```

## Training Data Capture

Each decision (in replace mode) appends a row to `data/training/gcp_cases.jsonl`:
```json
{
  "det_tier": "memory_care",
  "llm_tier": "assisted_living",
  "llm_conf": 0.87,
  "final_tier": "assisted_living",
  "allowed_tiers": ["assisted_living", "in_home"],
  "bands": {"cog": "moderate", "sup": "high"},
  "risky": false,
  "reason": "de_overscore_accept_al",
  "answers": {...},
  "flags": [...]
}
```

## Testing

### Unit Tests
```bash
python tools/test_tier_policy.py
```

**Scenarios Covered:**
1. ✓ LLM tier not in allowed set → keep deterministic
2. ✓ Risky behaviors → keep MC
3. ✓ De-overscore (moderate×high, no risky) → accept AL
4. ✓ Confident LLM → accept
5. ✓ Low confidence → keep deterministic

### Manual Testing (Streamlit)
1. Set `FEATURE_GCP_LLM_TIER="shadow"` in secrets
2. Complete GCP with moderate×high profile
3. Check console: `[GCP_TIER_DECISION] mode=shadow ...`
4. Change to `FEATURE_GCP_LLM_TIER="replace"`
5. Rerun same profile
6. Check console: `[GCP_TIER_DECISION] mode=replace ... -> final=...`
7. Verify final tier used in Cost Planner handoff

## Acceptance Criteria

✅ **With mode="shadow":**
- Deterministic tier always used
- Console logs show det vs llm comparison
- No functional changes to user experience

✅ **With mode="replace":**
- Final tier switches to LLM when policy allows
- Allowed tiers enforced (cognitive/behavioral gates)
- Risky behavior protection active
- De-overscore rule correctly identifies moderate×high cases
- Console logs show decision chain with reason
- Training cases captured to JSONL

✅ **UI Consistency:**
- Summary headline reflects final tier
- Cost Planner receives final tier
- Move Preferences conditional rendering uses final tier

## Rollout Plan

1. **Phase 1: Shadow (Current Default)**
   - Collect baseline comparison data
   - Validate LLM tier accuracy
   - Review disagreement patterns

2. **Phase 2: Targeted Replace**
   - Enable "replace" for specific cohorts
   - Monitor decision reasons distribution
   - Track user satisfaction metrics

3. **Phase 3: General Replace**
   - Roll out to all users
   - Continue monitoring training data
   - Iterate on policy rules based on outcomes

## Notes
- No UI changes (per requirements)
- All changes surgical and local
- Not pushed (per requirements)
- Ready for testing on dev branch
