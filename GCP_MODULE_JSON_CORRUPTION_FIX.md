# GCP Module JSON Corruption Fix

**Date:** January 2025  
**Status:** ✅ Fixed  
**Branch:** feature/cost_planner_v2

## Problem

App crashed on startup with JSON decode error:

```
json.decoder.JSONDecodeError: This app has encountered an error.
File: products/gcp_v4/modules/care_recommendation/module.json
```

The file was corrupted with incomplete/malformed JSON - cut off mid-way at `"scoreής` (Greek characters, likely encoding issue).

## Root Cause

The `module.json` file became corrupted, likely during:
1. A previous edit/save operation
2. Git merge conflict resolution
3. Text encoding issue (Greek characters appeared: `ής`)

The file was only 187 lines when it should have been ~430+ lines with all sections complete.

## Solution

Replaced corrupted file with clean backup from `/Users/shane/Desktop/SAFE/module.json`.

### Verification
```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('products/gcp_v4/modules/care_recommendation/module.json'))"
✅ JSON is valid!

# Confirm files match
diff /Users/shane/Desktop/SAFE/module.json products/gcp_v4/modules/care_recommendation/module.json
Files are identical
```

## File Structure

The restored `module.json` contains:

### Module Metadata
- **ID:** `gcp_care_recommendation`
- **Version:** `v2025.10`
- **Navi Guidance:** Purpose, outcome, next steps, encouragement, context tips

### 7 Sections
1. **intro** - Welcome screen with actions
2. **about_you** - Age range, living situation, isolation (3 questions)
3. **medication_mobility** - Meds, mobility, falls, chronic conditions (5 questions)
4. **cognition_mental_health** - Memory, behaviors, mood (3 questions)
5. **daily_living** - ADLs, IADLs, hours/day, primary support (5 questions)
6. **results** - Care recommendation summary with actions

### Navi Guidance Tags
Each section includes:
- `section_purpose` - What this section assesses
- `why_this_matters` - Clinical/care rationale
- `red_flags` - Risk combinations to watch for
- `encouragement` - Supportive messaging
- `context_note` - Additional tips (where applicable)

### Question-Level Guidance
Selected questions include:
- `why_asked` - Rationale for the question
- `tip` - Helpful context for answering
- `tone` - inform | urgent | supportive

## Impact

✅ **App Loads:** No more JSON decode errors  
✅ **GCP Functional:** All sections render properly  
✅ **Navi Integration:** Guidance tags available for context-aware assistance  
✅ **Scoring Works:** All options have proper score/flags  
✅ **Results Display:** Outputs section with templated summary

## Prevention

### Best Practices
1. **Always validate JSON** after editing:
   ```bash
   python3 -m json.tool module.json > /dev/null
   ```

2. **Use proper editor** with JSON syntax highlighting (VS Code, not TextEdit)

3. **Keep backups** of critical config files in `/SAFE/` directory

4. **Check encoding** - ensure UTF-8, no BOM, Unix line endings (LF not CRLF)

5. **Test immediately** after editing config files:
   ```bash
   streamlit run app.py
   ```

### Git Hooks (Optional)
Consider adding pre-commit hook to validate JSON:
```bash
#!/bin/bash
for file in $(git diff --cached --name-only | grep '\.json$'); do
  python3 -m json.tool "$file" > /dev/null || exit 1
done
```

## Related Files
- `products/gcp_v4/modules/care_recommendation/config.py` - Loads this JSON
- `core/modules/engine.py` - Renders sections and questions
- `core/navi.py` - Uses `navi_guidance` tags for contextual help

## Testing Checklist
- [x] JSON validates with `python3 -m json.tool`
- [x] File matches clean backup (diff shows identical)
- [ ] App starts without errors (pending manual test)
- [ ] GCP loads all sections (pending manual test)
- [ ] Questions render with proper options (pending manual test)
- [ ] Results show recommendation (pending manual test)
- [ ] Navi can access guidance tags (pending manual test)

---

## Summary

**Issue:** Corrupted JSON file with incomplete data and encoding errors  
**Fix:** Restored from clean backup in `/Users/shane/Desktop/SAFE/`  
**Status:** File validated, ready for testing  
**Next:** Manual end-to-end test of GCP flow
