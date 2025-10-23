# Merge Checklist: feature/llm-shadow-navi → dev → main

## Pre-Merge Status
✅ All changes committed on feature/llm-shadow-navi
- Commit: 87f0285 "feat(llm-shadow): complete LLM-assisted GCP summary with diagnostics"

## Step-by-Step Merge Process

### 1. Switch to dev and update
```bash
git checkout dev
git pull origin dev
```

### 2. Merge feature branch
```bash
git merge --no-ff feature/llm-shadow-navi -m "merge(feature/llm-shadow-navi): LLM-assisted GCP summary + diagnostics

Features:
- LLM summary generation on GCP RESULTS (assist mode)
- Spinner during LLM work (assist mode only)
- Hours Accept button recomputes summary
- Concise LLM-vs-det logs + disagreement capture
- Gated event/watcher logging (quiet by default)
- Smoke test for LLM validation

Flags:
- FEATURE_LLM_GCP=assist (LLM summary on RESULTS)
- FEATURE_GCP_HOURS=assist (hours suggestions)
- DEBUG_LLM=off (quiet by default)
- DEBUG_EVENTS=off (no event spam)
- FEATURE_TRAIN_LOG_ALL=off (only log disagreements)"
```

### 3. Local Verification (CRITICAL - Do Not Skip)
```bash
./run_app.sh
```

**Test Checklist:**
- [ ] Navigate to GCP → complete assessment → reach RESULTS
- [ ] ✅ Spinner appears: "Summarizing your recommendation…"
- [ ] ✅ Navi header shows LLM headline (one sentence)
- [ ] ✅ Body shows "What this means for you" paragraph
- [ ] ✅ No debug captions in top-left corner
- [ ] ✅ Terminal shows: `[GCP_LLM_SUMMARY] det=... llm=... aligned=... conf=...`
- [ ] ✅ Hours nudge appears if user under-selected
- [ ] ✅ Click "Accept 4–8h" → spinner reappears → summary updates
- [ ] ✅ Navigate to Cost Planner → no regressions
- [ ] ✅ No console spam (no [EVENT], no watcher logs)

### 4. Commit merge (if tests pass)
```bash
git commit --allow-empty -m "merge(feature/llm-shadow-navi): verified spinner + LLM summary + hours accept fix

Verified:
✅ LLM summary renders with headline + paragraph
✅ Spinner appears during LLM calls (assist mode)
✅ Hours Accept button recomputes summary correctly
✅ No UI regressions (GCP layout, Cost Planner intact)
✅ Console quiet by default (no event/watcher spam)
✅ Concise LLM logs: [GCP_LLM_SUMMARY] det=... llm=... aligned=..."
```

### 5. Push to main
```bash
git checkout main
git pull origin main
git merge --no-ff dev -m "release: LLM-assisted GCP summary (v4.1.0)

Features:
- LLM-generated summary on GCP RESULTS page
- Smart hours suggestions with nudge/accept flow
- Concise LLM-vs-deterministic logging
- Gated debug flags for clean console

Breaking changes: None
Backward compatible: Yes"

git push origin main
```

### 6. Post-Push Verification

**A) Verify Streamlit Cloud Build**
- Check: https://share.streamlit.io/[your-app]/deployments
- Ensure build succeeds (green check)
- Test RESULTS page in production

**B) Verify Production Secrets (Streamlit Cloud)**
```toml
# .streamlit/secrets.toml (Streamlit Cloud dashboard)
FEATURE_LLM_GCP = "assist"           # Enable LLM summary
FEATURE_GCP_HOURS = "assist"          # Enable hours suggestions
FEATURE_GCP_MC_BEHAVIOR_GATE = "on"   # Enable MC behavior gate
DEBUG_LLM = "off"                     # Quiet by default
DEBUG_NAVI = "off"                    # Quiet by default
DEBUG_EVENTS = "off"                  # No event spam
OPENAI_API_KEY = "sk-..."            # Your production key
OPENAI_MODEL = "gpt-4o-mini"          # Cost-effective model
```

**C) Production Smoke Test**
- Navigate to GCP RESULTS in production
- Verify spinner + summary appear
- Check browser console for errors
- Verify no console spam

## Rollback Plan (if needed)
```bash
# If production issues arise
git checkout main
git revert HEAD~1  # Revert the merge
git push origin main
```

## Success Criteria
✅ All local tests pass
✅ Streamlit Cloud build succeeds
✅ Production RESULTS page shows LLM summary
✅ No console errors or spam
✅ Cost Planner still works
✅ Feature flags correctly configured

## Notes
- Smoke test available: `python3 tools/smoke_llm_summary.py`
- Training logs: `data/training/gcp_cases.jsonl` (disagreements only)
- Hours logs: `data/training/hours_cases.jsonl` (all cases)
