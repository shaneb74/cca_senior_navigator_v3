# Repository Cleanup Plan - November 2025

**Branch:** `cleanup/repo-consolidation-2025-11`  
**Date:** November 1, 2025  
**Goal:** Reduce repo size, eliminate confusion, improve maintainability

---

## 📊 Current State Assessment

### Repository Metrics
- **Git size:** 68MB
- **Archive directory:** 336KB (30 files)
- **Pages directory:** 9 Python files
- **CSS files:** 4 files (84KB total)

### Major Issues Identified

#### 1. **Duplicate/Conflicting Page Routing** (HIGH PRIORITY)
**Problem:** Multiple overlapping routes for audience selection:
- `pages/audience.py` ✅ (NEW - working, modern)
- `pages/_stubs.py` contains `render_welcome_contextual()`, `render_for_someone()`, `render_for_me_contextual()` ❌ (OLD - unused)
- `config/nav.json` still routes `welcome_contextual` → `pages._stubs:render_welcome_contextual`

**Impact:**
- Confusing which page is authoritative
- `_stubs.py` has dead code that references non-existent pages (`?page=for_someone`, `?page=for_me_contextual`)
- Maintenance burden - updates must touch multiple files

**Solution:** Delete old contextual welcome functions from `_stubs.py`, remove `welcome_contextual` route

---

#### 2. **Archive Directory Bloat** (MEDIUM PRIORITY)
**Contents:**
- `css_backup_2025-11-01/` - 9 files from 2 weeks ago
- `css_unused_phase2/` - 5 files (products.css, hubs.css, tokens.css)
- `pages_legacy/` - 8 old page implementations
- 17 markdown verification/diagnostic files (PHASE4A, PHASE4B, PYTHON_ENVIRONMENT_FIXED, etc.)
- Demo seed scripts, test files

**Problem:** Archive is meant to be temporary but accumulating indefinitely

**Solution:**
```bash
# Keep only truly useful reference material
# Delete ephemeral diagnostics, backups, and phase verification docs
# Move critical historical context to docs/legacy/ if needed
```

---

#### 3. **Documentation Sprawl** (MEDIUM PRIORITY)
**Current Structure:**
```
docs/
├── phase3a_navi_lobby_integration.md
├── phase3c_finalization.md
├── phase4b_journey_completion.md
├── phase5a_navi_journey_intelligence.md
├── Phase_5G_Journey_Hierarchy.md
├── PHASE5J_GRADIENT_AND_COMPLETED_CARD.md
├── phase5a1_hotfix_navi_and_pills.md
├── patches/
│   ├── CLEANUP_PLAN.md
│   ├── DISCOVERY_JOURNEY_AI_PATCH.md
│   ├── feature_post_css_journey_completion.md
│   ├── fix_welcome_contextual_toggle_and_css.md
│   └── feature_welcome_contextual_redesign.md
├── legacy/
│   ├── ASSESSMENT_TOGGLE_IMPLEMENTATION.md
│   ├── DEMO_PROFILES_UPDATE_COMPLETE.md
│   └── TODO_LINT_TYPE.md
└── cleanup/
    └── CSS_CONSOLIDATION_PHASE_2.md
```

**Problem:**
- Phase docs (3a, 3c, 4b, 5a, 5g, 5j) are historical but scattered
- Patches directory contains both completed work and plans
- No clear indication which docs are current vs historical

**Solution:** Consolidate into:
```
docs/
├── ARCHITECTURE.md (current)
├── CSS_ARCHITECTURE.md (current)
├── TRAINING.md (current)
├── REPO_STRUCTURE.md (current)
├── CLAUDE_5E_GUIDE.md (current)
├── history/
│   ├── phase_history.md (consolidated timeline)
│   └── completed_patches.md (archive of fixes)
└── planning/
    └── (active planning docs only)
```

---

#### 4. **Stub Functions in _stubs.py** (LOW PRIORITY)
**Current Usage:**
- `render_about()` ✅ Used in nav
- `render_login()` ✅ Used in nav (auth_start alias)
- `render_logout()` ✅ Used in nav
- `render_export_results()` ✅ Used in nav
- `render_welcome_contextual()` ❌ **DELETE - replaced by audience.py**
- `render_for_someone()` ❌ **DELETE - dead code**
- `render_for_me_contextual()` ❌ **DELETE - dead code**
- `render_pro_welcome()` ✅ Keep (professional flow)
- `render_pro_welcome_contextual()` ✅ Keep
- `render_professionals()` ❌ **MOVE to pages/professionals.py**
- `render_waiting_room()` ✅ Keep
- `render_trusted_partners()` ✅ Keep
- `render_my_account()` ✅ Keep
- `render_terms()` ✅ Keep
- `render_privacy()` ✅ Keep
- `render_documents()` ✅ Keep
- `render_exports()` ✅ Keep
- `render_ai_advisor()` ✅ Keep

**Problem:** Mixing dead code with active stubs

**Solution:** Remove dead functions, optionally split _stubs.py into logical groups

---

#### 5. **CSS Backup Files** (LOW PRIORITY)
**Found:**
- `assets/css/overrides.css.backup` (in repo root)
- `archive/css_backup_2025-11-01/` (9 files)

**Problem:** Backup files committed to git (unnecessary - git IS the backup)

**Solution:** Delete all `.backup` files, rely on git history

---

## 🎯 Cleanup Actions (Prioritized)

### Phase 1: Remove Dead Page Routes (IMMEDIATE - SAFE)

**Files to modify:**
1. `pages/_stubs.py` - Delete 3 functions
2. `config/nav.json` - Remove 1 route

**Commands:**
```bash
# This phase removes code that is provably unused
# Backed by: grep search shows only _stubs.py contains these functions
# Risk: ZERO - no active routes point to deleted code
```

**Functions to delete from `pages/_stubs.py`:**
- `render_welcome_contextual()` (lines ~110-170)
- `render_for_someone()` (lines ~173-239)
- `render_for_me_contextual()` (lines ~242-308)

**Route to remove from `config/nav.json`:**
- `welcome_contextual` entry (lines ~23-28)

**Validation:**
```bash
# After changes, verify no broken references:
grep -r "welcome_contextual\|for_someone\|for_me_contextual" --include="*.py" --include="*.json" --exclude-dir=".venv"
# Should return: 0 matches (or only in this cleanup doc)
```

---

### Phase 2: Delete Archive Directory (SAFE - 90% certain)

**Commands:**
```bash
# Move any truly useful reference to docs/legacy/
# Delete everything else
git rm -r archive/css_backup_2025-11-01/
git rm -r archive/css_unused_phase2/
git rm -r archive/pages_legacy/
git rm archive/*.md  # All phase verification docs
git rm archive/*.py  # Test/seed scripts
git rm archive/*.html  # Test HTML files
```

**Keep (if anything):**
- Nothing - git history has everything we need

**Impact:** Reduces repo by ~336KB, removes 30 files

---

### Phase 3: Consolidate Documentation (MEDIUM RISK)

**Actions:**
```bash
# Create consolidated history doc
mkdir -p docs/history/

# Move all phase docs into single timeline
cat docs/phase3*.md docs/phase4*.md docs/phase5*.md > docs/history/phase_history.md

# Delete originals
git rm docs/phase3*.md docs/phase4*.md docs/phase5*.md docs/PHASE*.md

# Move completed patches to history
mv docs/patches/*.md docs/history/completed_patches.md
git rm -r docs/patches/

# Move truly legacy content
mv docs/legacy/*.md docs/history/
```

**Keep in docs/ root:**
- ARCHITECTURE.md
- CSS_ARCHITECTURE.md  
- TRAINING.md
- REPO_STRUCTURE.md
- CLAUDE_5E_GUIDE.md
- OBSOLETE_PNG_ASSETS.md

---

### Phase 4: Split or Clean _stubs.py (LOW RISK)

**Option A: Minimal Clean (RECOMMENDED)**
- Delete dead functions (Phase 1)
- Keep file as-is for active stubs
- Rename to `pages/stubs.py` (no underscore)

**Option B: Split into Logical Groups**
```
pages/
├── stubs_legal.py (terms, privacy, about)
├── stubs_auth.py (login, logout, signup)
├── stubs_pro.py (professional routes)
└── stubs_misc.py (waiting_room, documents, etc)
```

**Recommendation:** Option A - splitting is low value, high risk

---

### Phase 5: Remove CSS Backups (TRIVIAL)

**Commands:**
```bash
git rm assets/css/overrides.css.backup
# Archive CSS backups already handled in Phase 2
```

---

## 📏 Expected Impact

### File Reduction
- **Before:** ~30 archive files + 3 dead functions + backups
- **After:** Clean repo, ~35+ fewer files
- **Lines of code removed:** ~500+ (dead code)

### Clarity Improvements
- ✅ Single audience page (`pages/audience.py` only)
- ✅ No routing ambiguity (welcome_contextual gone)
- ✅ Clean docs structure (history vs current)
- ✅ No backup files in git

### Maintenance Burden
- **Before:** Update audience flow = touch 3 files
- **After:** Update audience flow = touch 1 file

---

## ⚠️ Risks & Mitigations

### Risk 1: Breaking Hidden Routes
**Mitigation:** Full grep search before deletion + manual testing of:
- Welcome page → Audience selection
- Audience → Hub Lobby flow
- All _stubs.py functions (except deleted 3)

### Risk 2: Losing Important Context
**Mitigation:** 
- All changes in git history forever
- Branch persists after merge
- This document serves as audit trail

### Risk 3: Merge Conflicts
**Mitigation:**
- Work in dedicated branch
- Merge only when dev is stable
- Can cherry-pick safe changes if needed

---

## 🚀 Execution Plan

### Step 1: Create Branch ✅ DONE
```bash
git checkout -b cleanup/repo-consolidation-2025-11
```

### Step 2: Phase 1 - Dead Code (15 min)
1. Delete 3 functions from `_stubs.py`
2. Remove `welcome_contextual` from `nav.json`
3. Test: Visit `?page=welcome` → click "Start Now" → should go to `?page=audience`
4. Commit: `git commit -m "cleanup: remove dead contextual welcome functions"`

### Step 3: Phase 2 - Archive (5 min)
1. Delete entire archive directory
2. Commit: `git commit -m "cleanup: delete archive directory (use git history instead)"`

### Step 4: Phase 3 - Docs (20 min)
1. Consolidate phase docs
2. Restructure docs/
3. Commit: `git commit -m "cleanup: consolidate documentation structure"`

### Step 5: Phase 4 - Stubs (10 min)
1. Rename `_stubs.py` → `stubs.py`
2. Update nav.json references
3. Commit: `git commit -m "cleanup: rename _stubs.py to stubs.py (no leading underscore)"`

### Step 6: Phase 5 - CSS Backups (2 min)
1. Delete backup files
2. Commit: `git commit -m "cleanup: remove CSS backup files (redundant with git)"`

### Step 7: Testing (30 min)
- Full manual test of all routes in nav.json
- Verify no 404s or missing modules
- Check hub → product flows

### Step 8: Merge (when ready)
```bash
git checkout dev
git merge cleanup/repo-consolidation-2025-11
git push origin dev
```

---

## 📝 Acceptance Criteria

- [ ] All dead code removed
- [ ] Archive directory empty or deleted
- [ ] Documentation consolidated and organized
- [ ] No `.backup` files in repo
- [ ] All existing routes still work
- [ ] No references to deleted functions
- [ ] Clean git history (1 commit per phase)
- [ ] This cleanup plan committed for audit trail

---

## 🔄 Rollback Plan

```bash
# If anything breaks:
git checkout dev  # Abandon cleanup branch
git branch -D cleanup/repo-consolidation-2025-11

# If already merged:
git revert <merge-commit-sha>
```

---

## 💡 Future Cleanup Opportunities (Post-Merge)

1. **Training data:** Consider moving `data/training/*.jsonl` to external storage (2MB+)
2. **Git history:** If repo grows >100MB, consider `git filter-branch` to purge large blobs
3. **Asset optimization:** Compress images in `assets/images/` (potential 20-30% size reduction)
4. **Dependency audit:** Review `requirements.txt` for unused packages
5. **Module splitting:** Consider splitting large modules like `core/mcip.py` (1000+ lines)

---

**Ready to execute? Start with Phase 1 (safest, highest value).**
