# Diagnostic Plan for $4,698 Bug

## If Clear Session Doesn't Fix It

Run through Quick Estimate → Financial Review and copy the console output here:

### Expected Logs (what we SHOULD see):
```
[QE_WARMED] active=al result={'total': 7875.0, 'segments': {...}}
[CP_PERSIST] sel=al care=5175.0 carry=2700.0 comb=7875.0
[CP_PERSIST_FA] cost_v2_quick_estimate.monthly_adjusted=5175.0
[FIN_PICK] persisted_selection=al current_tab=al
[FIN_BASE] sel=al care=5175.0 carry=2700.0 combined=7875.0
```

### If ANY of these show wrong values, paste actual logs here:
```
[PASTE CONSOLE OUTPUT]
```

### Then run this search:
```bash
cd /Users/shane/Desktop/cca_senior_navigator_v3
rg -n --pretty "4698|monthly_adjusted.*=.*segment" products/concierge_hub/cost_planner_v2
```

This will find any remaining code that might be setting monthly_adjusted to a segment value.

## Quick Theory Test

$4,698 might be from:
1. Old cache (99% likely - **CLEAR SESSION FIRST**)
2. A different code path setting cost_v2_quick_estimate before our CTA handler runs
3. expert_review.py calculating its own estimate instead of reading persisted value
4. Regional adjustment being applied incorrectly (4500 * 1.044 = 4698)

If it's #4 (regional adjustment), we need to check if something is multiplying the Room segment by regional factor AFTER we persist.
