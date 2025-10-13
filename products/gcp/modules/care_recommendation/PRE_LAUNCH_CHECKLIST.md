# Pre-Launch Verification Checklist

## 🔍 Manual Testing Scenarios

### Scenario 1: Independent Senior (Low Tier)
```
Age: 65-74
Living: With family
Memory: None
Mobility: Independent
Falls: None
Help needed: Independent
Support: Family present

Expected: "Independent / In-Home" tier
Expected Score: < 10
```

### Scenario 2: Moderate Care Needs (Mid Tier)
```
Age: 75-84
Living: Alone
Memory: Occasional forgetfulness
Mobility: Walker
Falls: One fall
Help needed: Some help
ADLs: Bathing
IADLs: Meal prep, housekeeping
Support: Family (limited hours)

Expected: "Assisted Living" tier
Expected Score: 10-20
```

### Scenario 3: Memory Care Needed (High Tier)
```
Age: 85+
Living: Alone
Memory: Moderate to severe
Mobility: Wheelchair
Falls: Multiple
Help needed: Daily assistance
ADLs: Bathing, dressing, eating
Behaviors: Wandering, confusion
Support: None or limited

Expected: "Memory Care" tier
Expected Score: 20-30
```

### Scenario 4: High-Acuity Care (Highest Tier)
```
Age: 85+
Living: Alone
Memory: Severe dementia
Mobility: Bed-bound
Falls: Multiple
Help needed: 24-hour support
ADLs: All 5 (bathing, dressing, eating, toileting, transferring)
Chronic: Multiple conditions
Behaviors: Wandering, aggression
Support: None

Expected: "High-Acuity Memory Care" or "Skilled Nursing"
Expected Score: > 30
```

---

## ✅ Testing Checklist

### Code Quality
- [ ] Run linter: `ruff check products/gcp/modules/care_recommendation/`
- [ ] Check types: `mypy products/gcp/modules/care_recommendation/` (if installed)
- [ ] Review docstrings are complete

### Unit Tests
- [ ] All tests pass: `pytest tests/test_care_recommendation.py -v`
- [ ] Coverage > 90%: `pytest tests/test_care_recommendation.py --cov`
- [ ] No warnings in test output
- [ ] Smoke test passes: `python tests/test_care_recommendation.py`

### Integration Tests
- [ ] Module loads in app without errors
- [ ] Navigate to GCP product: `?page=gcp`
- [ ] Complete full assessment flow
- [ ] Verify all sections render correctly
- [ ] Check progress bar updates
- [ ] Verify session state persists on page refresh

### Conditional Logic
- [ ] "Behaviors" question only shows when memory is moderate/severe
- [ ] Multi-select allows custom entries (chronic conditions, behaviors)
- [ ] Required questions block progression if unanswered
- [ ] Optional questions can be skipped

### Recommendations
- [ ] Independent scenario gives tier 0-1
- [ ] Moderate scenario gives tier 2
- [ ] Memory care scenario gives tier 3
- [ ] High-acuity scenario gives tier 4
- [ ] Summary points are clear and actionable
- [ ] No placeholder text or "n/a" in points

### Confidence Scoring
- [ ] Complete assessment shows 80-100% confidence
- [ ] Partial assessment shows lower confidence
- [ ] Missing critical questions shows warning
- [ ] Confidence label is appropriate

### Flags
- [ ] High-priority flags appear in summary
- [ ] Flag messages are helpful
- [ ] Multiple flags don't overwhelm output

### Error Handling
- [ ] Empty answers return friendly error
- [ ] Missing critical fields show specific message
- [ ] Invalid data doesn't crash module
- [ ] Error messages are user-friendly

### Performance
- [ ] Module loads in < 500ms
- [ ] Scoring completes in < 100ms
- [ ] No console errors
- [ ] No memory leaks (check browser DevTools)

### Accessibility
- [ ] Questions are keyboard-navigable
- [ ] Labels are descriptive
- [ ] Required fields are marked
- [ ] Error messages are clear

### Data Quality
- [ ] Answers persist in session state
- [ ] Outcome is stored correctly
- [ ] Module state updates on each section
- [ ] Progress calculation is accurate

---

## 🐛 Known Issues to Watch For

### Issue: Chip selection requires double-click
**Symptom**: First click highlights, second click selects  
**Workaround**: This is Streamlit button behavior - expected  
**Fix**: Not needed; users adapt quickly

### Issue: Multi-select doesn't show selected count
**Symptom**: No visual indicator of how many items selected  
**Workaround**: Use Streamlit's native multiselect widget  
**Fix**: Already implemented in `core/modules/inputs.py`

### Issue: Progress jumps when navigating back
**Symptom**: Progress bar updates unexpectedly  
**Workaround**: Track section completion separately  
**Fix**: Implemented in `BaseProduct._update_progress()`

---

## 📊 Metrics to Verify

### Scoring Distribution
Run this to check score distribution:
```python
from products.gcp.modules.care_recommendation.logic import derive
from core.modules.base import load_module_manifest

manifest = load_module_manifest("gcp", "care_recommendation")

# Test various scenarios
scenarios = [
    ("Independent", {...}),  # Should be 0-10
    ("Moderate", {...}),     # Should be 10-20
    ("High need", {...}),    # Should be 20-30
]

for name, answers in scenarios:
    result = derive(manifest, answers, {})
    print(f"{name}: {result['score']} -> {result['tier']}")
```

Expected distribution:
- Tier 0-1: score 0-10
- Tier 2: score 10-20
- Tier 3: score 20-30
- Tier 4: score 30+

### Confidence Distribution
- Complete assessment: 85-100%
- Partial assessment: 60-84%
- Minimal assessment: < 60%

---

## 🚀 Pre-Deployment Steps

### 1. Code Review
- [ ] Review all changes in `logic.py`
- [ ] Verify manifest (`module.json`) is valid JSON
- [ ] Check test coverage report
- [ ] Review documentation for accuracy

### 2. Stakeholder Review
- [ ] Demo all 4 test scenarios
- [ ] Show summary point examples
- [ ] Explain confidence scoring
- [ ] Discuss edge cases

### 3. Final Validation
- [ ] Run full test suite one more time
- [ ] Test in production-like environment
- [ ] Verify analytics tracking (if applicable)
- [ ] Check error logging works

### 4. Documentation
- [ ] README is up to date
- [ ] Quick Start guide is accurate
- [ ] Changelog is updated
- [ ] Support contacts are correct

---

## 🎯 Launch Criteria

### Must Have (Blocking)
- [ ] All unit tests pass
- [ ] No console errors
- [ ] Recommendations make sense for test scenarios
- [ ] Module loads without crashes

### Should Have (Non-blocking but important)
- [ ] Coverage > 90%
- [ ] All 4 test scenarios validated manually
- [ ] Documentation complete
- [ ] Debug mode tested

### Nice to Have (Post-launch)
- [ ] Performance profiling
- [ ] User acceptance testing
- [ ] A/B testing setup
- [ ] Analytics dashboard

---

## 📝 Post-Launch Monitoring

### Week 1
- [ ] Monitor error rates
- [ ] Check recommendation distribution
- [ ] Gather user feedback
- [ ] Review completion rates

### Week 2-4
- [ ] Analyze score patterns
- [ ] Identify edge cases
- [ ] Refine summary points based on feedback
- [ ] Adjust scoring weights if needed

---

## 🆘 Emergency Rollback Plan

If critical issues are found:

1. **Disable module temporarily**:
   ```python
   # In config/nav.json, add:
   {"key": "gcp", "hidden": true}
   ```

2. **Revert to previous version**:
   ```bash
   git revert <commit-hash>
   git push origin dev
   ```

3. **Show maintenance message**:
   ```python
   st.warning("⚠️ The Guided Care Plan is temporarily unavailable. Please check back soon.")
   ```

---

## ✅ Sign-Off

**Developer**: _________________________  Date: ___________

**Reviewer**: _________________________  Date: ___________

**Product Owner**: ____________________  Date: ___________

---

**Notes**:
- Keep this checklist with your sprint documentation
- Update as you discover new edge cases
- Share findings with the team
- Celebrate when complete! 🎉
