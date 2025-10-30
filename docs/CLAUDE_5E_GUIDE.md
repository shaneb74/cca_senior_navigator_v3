Perfect — I’ve gone through the **apzumi branch** (including all updated docs, app logic, and layout files).
Here’s your full **Phase 5E kickoff pack**, including the glitch patch plan and a new internal guide for Claude.

---

## 🧭 Phase 5E — Dynamic Personalization (Kickoff)

### 🎯 Goal

Personalize the Senior Navigator experience dynamically for each user based on their **profile, care tier, cognition/support bands, and journey phase**, while cleaning up visual and navigation inconsistencies left from 5D.

---

### ✅ Pre-Phase Fixes (from 5D)

| Item                                             | Status | Action                                                                                                 |
| ------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------ |
| Remove PNG product tiles                         | ⏳      | Replace static PNG with CSS-based or SVG icons in `layout.py` & `core/ui.py`.                          |
| Rename “Back to Hub” → “Back to Lobby”           | ⏳      | Update all product modules (GCP, Cost Planner, PFMA) buttons and calls to `route_to("hub_concierge")`. |
| Confirm Lobby routing returns to `hub_concierge` | ⏳      | QA after rename.                                                                                       |
| Journey state restoration                        | ✅      | Complete in `app.py`.                                                                                  |
| Compact NAVI progress tracker                    | ✅      | Injected globally in `layout.py`.                                                                      |

---

### ⚙️ Glitch Patch Plan

Create a patch branch `feature/5e-prepatch-cleanup` with these commits:

1. **`fix: replace PNG product tiles with CSS/SVG`**

   * Remove `static/images/*.png` tile assets.
   * Update `layout.py` product tile definitions to use `.product-tile-icon` CSS class.
   * Add fallback emoji icons (`🧭`, `💰`, `🧑‍⚕️`) to `modules.css`.

2. **`fix: rename Back to Hub → Back to Lobby`**

   * In each product module:

     ```python
     st.button("Back to Lobby", on_click=lambda: route_to("hub_concierge"))
     ```

3. **`fix: unify hub routing`**

   * Verify and patch any residual `route_to("welcome")` calls.

4. **`qa: journey coherence and nav consistency`**

   * Smoke test return paths for all modules.
   * Confirm `uid` persistence across navigations.

---

### 🚀 Phase 5E Deliverables

| Component                                  | Purpose                                                                               | Owner   |
| ------------------------------------------ | ------------------------------------------------------------------------------------- | ------- |
| `config/personalization_schema.json`       | Schema defining adjustable journey parameters (per user tier, band, phase).           | Backend |
| `core/personalizer.py`                     | Applies schema to current `ctx` and modifies navigation visibility / recommendations. | Core    |
| `data/personalization_cases.jsonl`         | Captured real user journey data for testing dynamic adjustments.                      | AI/QA   |
| `docs/Phase_5E_Dynamic_Personalization.md` | Living spec for Claude and Apzumi tracking.                                           | Claude  |

---

### 🧩 Personalization Logic (Outline)

1. **Context Inputs**

   * `ctx.tier` (`independent`, `assisted`, `memory_care`)
   * `ctx.bands` (cognition + support)
   * `ctx.phase` (`intake`, `plan`, `advisor`, `placement`)
   * User flags (`is_repeat_user`, `has_referral`, etc.)

2. **Dynamic Adjustments**

   * Show/hide hubs and modules based on tier.
   * Change copy tone (“exploratory” vs “directive”).
   * Reorder navigation options per journey stage.
   * Trigger AI recommendations via `FEATURE_LLM_NAVI = assist|adjust`.

3. **Persistence / Recovery**

   * User snapshot stored in `session_store` and synced to `load_user(uid)`.
   * Allow re-entry to correct journey phase upon return.

---

### 📋 Claude Phase 5E Implementation Guide (`docs/CLAUDE_5E_GUIDE.md`)

```markdown
# CLAUDE 5E Guide — Dynamic Personalization

## Purpose
Keep the Senior Navigator app aligned with Phase 5E goals.

## Responsibilities
1. Implement the personalization schema (`config/personalization_schema.json`).
2. Extend `core/personalizer.py` with dynamic journey logic.
3. Maintain navigation coherence — all “Back to Lobby” buttons must point to `hub_concierge`.
4. Eliminate static PNG tiles in favor of CSS/SVG icons.
5. Verify state persistence (`uid`, `session_id`) and recovery across modules.

## Key Routes
- `welcome` → Awareness
- `gcp` → Guided Care Plan
- `cost_v2` → Cost Planner v2
- `pfma_v2` → Plan with My Advisor
- `hub_concierge` → Central Lobby (return target)

## Success Criteria
- Seamless, personalized navigation based on user profile.
- No hard-coded PNG assets.
- All “Back to Lobby” routes work correctly.
- Personalization snapshot persists between sessions.
```

---

Would you like me to go ahead and draft the actual contents of
**`docs/Phase_5E_Dynamic_Personalization.md`** and **`docs/CLAUDE_5E_GUIDE.md`** so you can commit them in one go?
