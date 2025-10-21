# Demo User Fresh Load Feature

**Branch**: `bugfix/session-persistence-refinements`  
**Date**: October 20, 2025

---

## Problem

Demo users now correctly persist session progress (PFMA completion, advisor appointments, etc.) across navigation. However, when demoing the app to stakeholders, you want to show a **clean slate** without manually deleting working copy files.

## Solution

Added a `?fresh=true` query parameter that forces demo users to reload from the clean demo source, overwriting any session progress.

---

## Usage

### Normal Demo User (Persistent Progress)
```
?uid=demo_mary_memory_care
```
- First load: Copies from demo source
- Subsequent loads: Uses working copy (with progress)
- Progress persists across sessions ✅

### Fresh Demo User (Clean Slate)
```
?uid=demo_mary_memory_care&fresh=true
```
- Always copies from demo source
- Overwrites working copy with clean state
- Perfect for demos and presentations ✅

---

## Examples

### Mary - Normal (Persistent)
```
http://localhost:8501/?uid=demo_mary_memory_care
```
- GCP and Cost Planner start complete (as designed)
- Any progress you make persists
- Great for testing session persistence

### Mary - Fresh (Clean Slate)
```
http://localhost:8501/?uid=demo_mary_memory_care&fresh=true
```
- Reloads from demo source
- GCP and Cost Planner complete (as designed)
- PFMA and Advisor Prep reset to incomplete
- Great for stakeholder demos

### John V2 - Normal (Persistent)
```
http://localhost:8501/?uid=demo_user_john_v2
```

### John V2 - Fresh (Clean Slate)
```
http://localhost:8501/?uid=demo_user_john_v2&fresh=true
```

---

## Technical Details

### Implementation
**File**: `core/session_store.py:407-427`

```python
# Check if fresh load is requested via query param
import streamlit as st
force_fresh = st.query_params.get("fresh", "").lower() == "true"

# Copy demo profile if:
# 1. Working copy doesn't exist yet (first load), OR
# 2. Fresh load is explicitly requested (?fresh=true)
should_copy = demo_path.exists() and (not path.exists() or force_fresh)

if should_copy:
    shutil.copy2(demo_path, path)  # Overwrite working copy
```

### File Locations

**Demo Source** (read-only, protected):
- `data/users/demo/demo_mary_memory_care.json`
- `data/users/demo/demo_user_john_v2.json`
- Never modified by the app

**Working Copy** (read-write, session-specific):
- `data/users/demo_mary_memory_care.json`
- `data/users/demo_user_john_v2.json`
- Persists session progress
- Overwritten when `?fresh=true` is used

### Behavior Matrix

| Scenario | Working Copy Exists | Query Param | Action |
|----------|-------------------|-------------|---------|
| First load | ❌ No | None | Copy from demo source |
| First load | ❌ No | `?fresh=true` | Copy from demo source |
| Subsequent load | ✅ Yes | None | Use working copy (with progress) |
| Subsequent load | ✅ Yes | `?fresh=true` | **Overwrite** from demo source |

---

## Use Cases

### 1. Development & Testing
Use **normal mode** (no `?fresh=true`) to test session persistence:
```
?uid=demo_mary_memory_care
```
- Complete PFMA → Navigate → Return → PFMA still complete ✅
- Test that progress persists correctly

### 2. Stakeholder Demos
Use **fresh mode** (`?fresh=true`) to show clean slate:
```
?uid=demo_mary_memory_care&fresh=true
```
- Always starts from known state
- No leftover progress from previous demos
- Consistent experience every time

### 3. QA Testing
Use **fresh mode** for each test run:
```
?uid=demo_user_john_v2&fresh=true
```
- Ensures test starts from baseline
- No contamination from previous test runs
- Reproducible test scenarios

### 4. Production Demos
Bookmark both URLs:
- **Persistent**: For showing progress tracking
- **Fresh**: For showing onboarding flow

---

## Resetting Demo Users

### Option 1: Use `?fresh=true` (Recommended)
Just add `&fresh=true` to the URL - no file manipulation needed.

### Option 2: Delete Working Copy (Manual)
```bash
rm data/users/demo_mary_memory_care.json
```
Next load will copy from demo source.

### Option 3: Restore from Demo Source (Manual)
```bash
cp data/users/demo/demo_mary_memory_care.json data/users/
```

---

## Important Notes

1. **Regular users are NOT affected**
   - Only demo users (UIDs starting with `demo_`) support `?fresh=true`
   - Regular authenticated users always use persistent data

2. **Demo source is always protected**
   - `data/users/demo/*.json` files are never modified
   - Safe to use `?fresh=true` repeatedly

3. **Fresh load overwrites progress**
   - Any in-progress work is lost when using `?fresh=true`
   - Working copy is completely replaced with demo source

4. **Query param is case-insensitive**
   - `?fresh=true` ✅
   - `?fresh=True` ✅
   - `?fresh=TRUE` ✅
   - `?fresh=false` ❌ (ignored, uses normal behavior)

---

## Example Workflow

### Demo Preparation
1. Test the demo flow with persistent mode:
   ```
   ?uid=demo_mary_memory_care
   ```
2. Verify everything works as expected
3. Complete the full flow to ensure no bugs

### During Demo
1. Open fresh mode URL before each demo:
   ```
   ?uid=demo_mary_memory_care&fresh=true
   ```
2. Show stakeholders the clean onboarding experience
3. Walk through the features
4. Complete PFMA to show progress tracking

### After Demo
1. Next demo automatically starts fresh (due to `?fresh=true`)
2. Or remove `&fresh=true` to see persistent progress
3. No manual cleanup needed

---

## Troubleshooting

### Q: Progress isn't persisting
**A**: Remove `&fresh=true` from URL - it overwrites progress on every load.

### Q: Demo user shows old progress
**A**: Add `&fresh=true` to URL to reload from clean demo source.

### Q: Want to manually reset demo user
**A**: Delete working copy: `rm data/users/demo_mary_memory_care.json`

### Q: Demo source file was modified
**A**: Check git status - demo source should never change. If modified, restore from git:
```bash
git checkout data/users/demo/demo_mary_memory_care.json
```

---

## Testing

### Test 1: Fresh Load Works
1. Complete PFMA as Mary (normal mode)
2. Reload with `?fresh=true`
3. **Expected**: PFMA is incomplete (reset to demo state)

### Test 2: Persistent Mode Works
1. Complete PFMA as Mary (normal mode)
2. Navigate to Waiting Room
3. Navigate back to Concierge
4. **Expected**: PFMA still complete (progress persists)

### Test 3: Fresh Doesn't Affect Other Users
1. Complete PFMA as Mary with `?fresh=true`
2. Switch to John: `?uid=demo_user_john_v2`
3. Complete his PFMA
4. Switch back to Mary with `?fresh=true`
5. **Expected**: Mary resets, John's progress unaffected

---

## Future Enhancements

Potential improvements:
1. **Admin UI toggle** for fresh vs persistent mode
2. **Session-specific fresh mode** (browser session only)
3. **Partial reset** (reset specific products only)
4. **Demo mode indicator** in UI showing which mode is active

---

**Status**: ✅ Implemented and ready for testing  
**Branch**: `bugfix/session-persistence-refinements`
