#!/usr/bin/env bash
set -euo pipefail

# Controls
: "${APPLY_FIX:=0}"          # set to 1 to apply fixes

say()  { printf "\n\033[1m%s\033[0m\n" "$*"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$*"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$*"; }
err()  { printf "  \033[31m✗\033[0m %s\n" "$*"; }

repo_check() {
  if [[ ! -f core/base_hub.py ]]; then
    err "Run this from the repo root (core/base_hub.py not found)."
    exit 1
  fi
}

env_info() {
  say "== Python/Streamlit =="
  python -V || true
  python - <<'PY' || true
import streamlit
print("streamlit", streamlit.__version__)
PY
}

presence_checks() {
  say "== Presence check =="
  if [[ -f ui/dashboard.py ]]; then
    err "ui/dashboard.py STILL EXISTS (should be deleted)"
  else
    ok "ui/dashboard.py missing (good)"
  fi
  for f in core/base_hub.py pages/_stubs.py core/nav.py; do
    if [[ -f "$f" ]]; then ok "$f"; else err "$f missing"; fi
  done

  say "== CSS inventory =="
  for f in assets/css/theme.css assets/css/hub_grid.css assets/css/dashboard.css; do
    if [[ -f "$f" ]]; then
      sz=$(wc -c < "$f" 2>/dev/null || echo 0)
      ok "$f ($sz bytes)"
    else warn "$f [MISSING]"; fi
  done
}

base_hub_probe() {
  say "== base_hub injector mentions (theme|hub_grid|dashboard) =="
  python - <<'PY' || true
from pathlib import Path
p = Path("core/base_hub.py")
s = p.read_text(encoding="utf-8") if p.is_file() else ""
print("core/base_hub.py present:", bool(s))
print("injector exists:", "_inject_hub_css_once" in s)
print("mentions theme.css:", "theme.css" in s)
print("mentions hub_grid.css:", "hub_grid.css" in s)
print("mentions dashboard.css:", "dashboard.css" in s)
print("emits sn-hub wrapper:", '<div class="sn-hub' in s)
print("uses sorted_cards loop:", "for _, __, card in sorted_cards" in s)
PY
}

css_probe() {
  say "== css: .sn-hub selectors =="
  if compgen -G "assets/css/*.css" > /dev/null; then
    grep -Hn "sn-hub" assets/css/*.css || true
  else
    warn "No CSS files in assets/css"
  fi
}

welcome_bleed_probe() {
  say "== render_signup calls (should not be called outside route) =="
  # Use -E and single quotes so parentheses don't explode
  grep -RInE 'render_signup\s*\(' . || ok "No direct calls found."

  say "== TOP-LEVEL Streamlit calls in pages/_stubs.py (should be none) =="
  python - <<'PY' || true
import ast, pathlib
p = pathlib.Path("pages/_stubs.py")
if not p.exists():
    print("pages/_stubs.py missing")
    raise SystemExit(0)
t = ast.parse(p.read_text(encoding="utf-8"))
top=[]
for node in t.body:
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        v=node.value
        # st.foo(...) or bare render_xxx(...) at top-level
        if (hasattr(v.func, "value") and getattr(v.func.value, "id", "")=="st") or (hasattr(v.func, "id") and str(v.func.id).startswith("render_")):
            top.append(node.lineno)
print("no top-level calls detected" if not top else f"WARNING: top-level calls at lines {top}")
PY
}

zombie_dashboard_probe() {
  say "== Zombie 'dashboard' references (code & CSS) =="
  grep -RIn --include="*.py" --include="*.css" '\bdashboard[-_]' . | sed -E 's#^\./##' | head -n 100 || ok "No obvious zombie refs"
}

apply_fixes() {
  say "=== APPLYING FIXES ==="

  # 1) Patch core/base_hub.py injector to load theme.css, hub_grid.css, dashboard.css (in that order)
  python - <<'PY' || true
from pathlib import Path, re
bp = Path("core/base_hub.py")
if not bp.exists():
    raise SystemExit(0)
s = bp.read_text(encoding="utf-8")
if "_inject_hub_css_once" not in s:
    print("No injector found in core/base_hub.py; skipping.")
else:
    # normalize candidates block
    import textwrap
    new_block = textwrap.dedent('''
        here = Path(__file__).resolve().parent
        candidates = [
            Path("assets/css/theme.css"),
            Path("assets/css/hub_grid.css"),
            Path("assets/css/dashboard.css"),
            # fallback relative paths if someone runs from a weird CWD
            here.parents[1] / "assets" / "css" / "theme.css",
            here.parents[1] / "assets" / "css" / "hub_grid.css",
            here.parents[1] / "assets" / "css" / "dashboard.css",
        ]
    ''').strip()
    s = re.sub(r"here\s*=\s*Path\([^\n]+?\)\s*\.parent\s*\ncandidates\s*=\s*\[[\s\S]*?\]\s*", new_block + "\n", s, count=1)
    # Ensure we actually iterate candidates and inject
    if "for css_path in candidates" not in s:
        s = s.replace(
            "css_path = next((c for c in candidates if c.is_file()), None)\n    if not css_path:\n        # last-ditch: don’t crash, just bail\n        return\n\n    try:\n        css = css_path.read_text(encoding=\"utf-8\")\n        st.markdown(f\"<style>{css}</style>\", unsafe_allow_html=True)\n        st.session_state[key] = True\n    except Exception:\n        pass\n",
            "any_loaded = False\n    for css_path in candidates:\n        try:\n            if css_path.is_file():\n                css = css_path.read_text(encoding='utf-8')\n                if '</style>' in css.lower():\n                    continue\n                st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)\n                any_loaded = True\n        except Exception:\n            continue\n    if any_loaded:\n        st.session_state[key] = True\n"
        )
    bp.write_text(s, encoding="utf-8")
    print("Patched core/base_hub.py injector.")
PY

  # 2) Ensure hubs import and call _inject_hub_css_once() once
  for hub in hubs/concierge.py hubs/waiting_room.py; do
    if [[ -f "$hub" ]]; then
      if ! grep -q "_inject_hub_css_once" "$hub"; then
        sed -i '' -e 's#from core/base_hub import render_dashboard#from core.base_hub import render_dashboard, _inject_hub_css_once#' "$hub" 2>/dev/null || true
        # If the import line format differs, fall back to python edit
        python - <<PY || true
from pathlib import Path
p = Path("$hub")
s = p.read_text(encoding="utf-8")
if "from core.base_hub import render_dashboard" in s and "_inject_hub_css_once" not in s:
    s = s.replace("from core.base_hub import render_dashboard", "from core.base_hub import render_dashboard, _inject_hub_css_once")
if "_inject_hub_css_once()" not in s:
    s = s.replace("__all__ = [\"render\"]", "__all__ = [\"render\"]\n\n_inject_hub_css_once()")
p.write_text(s, encoding="utf-8")
print("Patched $hub to import/call _inject_hub_css_once()")
PY
      else
        ok "$hub already imports/calls _inject_hub_css_once"
      fi
    fi
  done

  # 3) Guard render_signup so it never renders unless explicitly routed
  if [[ -f pages/_stubs.py ]]; then
    python - <<'PY' || true
from pathlib import Path, re
p = Path("pages/_stubs.py")
s = p.read_text(encoding="utf-8")
m = re.search(r'^\s*def\s+render_signup\s*\([^)]*\)\s*:\s*$', s, flags=re.M)
if m:
    start = m.end()
    guard = ("\n"
             "    # hard guard: only render when explicitly routed\n"
             "    if st.query_params.get('page') not in ('signup','login'):\n"
             "        return\n")
    # insert guard if not present in first ~12 lines after def
    tail = s[start:start+600]
    if "hard guard: only render" not in tail:
        s = s[:start] + guard + s[start:]
        p.write_text(s, encoding="utf-8")
        print("Guarded pages/_stubs.py: render_signup() early-return unless routed.")
    else:
        print("pages/_stubs.py render_signup already guarded.")
else:
    print("render_signup() not found in pages/_stubs.py")
PY
  fi

  # 4) Ensure hub grid fallback exists
  if [[ -f assets/css/hub_grid.css ]]; then
    if ! grep -q "sn-hub .dashboard-grid" assets/css/hub_grid.css; then
      cat >> assets/css/hub_grid.css <<'CSS'

/* --- Hub fallback rules (safe for marketing pages) --- */
.sn-hub .dashboard-grid{display:grid;grid-template-columns:repeat(12,1fr);gap:var(--space-6)}
.sn-hub .dashboard-grid > [data-testid="stMarkdownContainer"],
.sn-hub .dashboard-grid > [data-testid="stMarkdown"],
.sn-hub .dashboard-grid > div[data-testid="stMarkdown"]{grid-column:span 6 !important}
@media (max-width:900px){
  .sn-hub .dashboard-grid > [data-testid="stMarkdownContainer"],
  .sn-hub .dashboard-grid > [data-testid="stMarkdown"],
  .sn-hub .dashboard-grid > div[data-testid="stMarkdown"]{grid-column:span 12 !important}
}
.sn-hub .dashboard-grid .ptile{grid-column:span 6}
.sn-hub .dashboard-grid .mtile{grid-column:span 12}
@media (max-width:900px){
  .sn-hub .dashboard-grid .ptile,.sn-hub .dashboard-grid .mtile{grid-column:span 12}
}
.sn-hub .dashboard-head:empty{padding:0;margin:0;height:auto}
.sn-hub .dashboard-additional:empty{display:none}
CSS
      ok "Appended hub grid fallback to assets/css/hub_grid.css"
    else
      ok "Hub grid fallback present"
    fi
  else
    warn "assets/css/hub_grid.css missing (not fatal)"
  fi

  say "Fixes applied. Restart Streamlit and hard-refresh (Safari: Develop → Empty Caches)."
}

repo_check
env_info
presence_checks
base_hub_probe
css_probe
welcome_bleed_probe
zombie_dashboard_probe

if [[ "${APPLY_FIX}" == "1" ]]; then
  apply_fixes
else
  say "Diagnostics only. To apply safe fixes: APPLY_FIX=1 bash ./sn_doctor.sh"
fi
