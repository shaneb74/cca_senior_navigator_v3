Goal: tighten the repo without changing the current visual output or the CSS cascade.
Non-goals: no merging CSS, no token moves, no edits to global.css or modules.css.

✅ Current Known-Good State (do not change)

Loaded CSS: assets/css/global.css, assets/css/modules.css

Pill source of truth: core/ui_css.py → inject_pill_css() (adds <style id="cca-pill-css"> and re-appends after Emotion updates)

Not loaded: assets/css/products.css, assets/css/hubs.css, assets/css/tokens.css

Removed already: assets/css/z_overrides.css

🧪 Preflight (run before doing anything)
# 1) Snapshot working tree
git status
git diff --stat

# 2) Confirm active CSS loaders (do NOT change them)
grep -R "global.css" -n
grep -R "modules.css" -n

# 3) Confirm non-loaded files are still non-loaded
grep -R "products.css" -n || true
grep -R "hubs.css" -n || true
grep -R "tokens.css" -n || true

# 4) Ensure pill injector exists and ID is stable
grep -R "inject_pill_css" core/ui_css.py
grep -R "cca-pill-css" core/ui_css.py


Expectations:

Only global.css and modules.css are referenced by app code.

inject_pill_css() exists and uses STYLE_ID = "cca-pill-css".

🧱 Actions (zero visual risk)
1) Archive unused CSS (do not delete)
mkdir -p archive/css_unused_phase2
git mv assets/css/products.css archive/css_unused_phase2/products.css || true
git mv assets/css/hubs.css archive/css_unused_phase2/hubs.css || true
git mv assets/css/tokens.css archive/css_unused_phase2/tokens.css || true


Rationale: These weren’t loaded in Phase 1; parking them removes confusion without touching runtime.

2) Add guardrails to prevent future regressions
2a) Lint: forbid radio/pill CSS outside ui_css.py

Create .githooks/pre-commit (if not already present) and append:

#!/usr/bin/env bash
set -e

# Block any new radio/pill rules from entering CSS files
if git diff --cached --name-only | grep -E '\.css$' >/dev/null; then
  if git diff --cached | grep -E '(data-testid="stRadio"|role="radiogroup"|input\[type="radio"\])' >/dev/null; then
    echo
    echo "❌ Blocked: radio/pill styles belong ONLY in core/ui_css.py (inject_pill_css)."
    echo "   Please move any stRadio/radiogroup/radio selectors into ui_css.py."
    echo
    exit 1
  fi
fi


Then enable hooks:

chmod +x .githooks/pre-commit
git config core.hooksPath .githooks

2b) Unit test: ensure pill style tag exists after render

Create tests/test_pills_style_tag.py:

import re
from core.ui_css import inject_pill_css

def test_pill_style_id_is_constant():
    # Ensure the style tag ID never changes (cascade anchor)
    from core.ui_css import PILL_CSS
    assert isinstance(PILL_CSS, str)
    # If we ever rename the style ID in JS, this test should fail.
    STYLE_ID = "cca-pill-css"
    assert STYLE_ID in open("core/ui_css.py", "r", encoding="utf-8").read()


(We’re not spinning Streamlit here; this is a “canary” that fails if someone renames the ID or moves the injector.)

2c) Canary test: forbid duplicate radio/pill styles in CSS

Create tests/test_no_radio_css_in_assets.py:

import pathlib, re

def test_no_radio_css_in_assets():
    css_dir = pathlib.Path("assets/css")
    offenders = []
    patterns = [
        r'data-testid="stRadio"',
        r'role="radiogroup"',
        r'input\[type="radio"\]',
        r'\[aria-checked',
    ]
    for p in css_dir.rglob("*.css"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if any(re.search(ptn, text) for ptn in patterns):
            offenders.append(str(p))
    assert not offenders, f"Radio/pill styles must live in core/ui_css.py, found in: {offenders}"

3) Optional: call inject_pill_css() globally (safe redundancy)

If not already done, you may call it once in your top-level page render (e.g., app.py or your base layout) in addition to module pages. It’s idempotent and safe:

from core.ui_css import inject_pill_css
inject_pill_css()  # harmless if no radios on the current page


This does not replace per-module calls; it’s only a belt-and-suspenders reinforcement.

🔍 Validation

Hard refresh (Cmd+Shift+R), then click around:

Pills render in black/gray and stay pills after any interaction.

Lobby/hubs/product tiles/Navi look exactly the same.

Dashboards unaffected.

Run tests:

pytest -q

📝 Commit
git add archive/css_unused_phase2 .githooks tests
git commit -m "chore(css): Phase 2 SAFE — archive unused CSS and add guardrails/tests without changing cascade"
git push

♻️ Rollback
git restore --staged -S .
git checkout -- assets/css
rm -rf archive/css_unused_phase2
git checkout .

Why this won’t break pills (or anything else)

We don’t edit global.css or modules.css.

We don’t change :root or tokens.

We don’t touch the cascade order.

We archive only files proven to be non-loaded.

We add tests to prevent anyone from reintroducing pill styles into static CSS.

If you want, I can also produce a tiny CI step snippet (GitHub Actions) that runs those tests on PRs so nothing slips back in.