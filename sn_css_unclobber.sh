#!/usr/bin/env bash
set -euo pipefail

: "${APPLY_FIX:=0}"

say() { printf "\n\033[1m%s\033[0m\n" "$*"; }
ok()  { printf "  \033[32m✓\033[0m %s\n" "$*"; }
warn(){ printf "  \033[33m!\033[0m %s\n" "$*"; }
err() { printf "  \033[31m✗\033[0m %s\n" "$*"; }

repo_check() {
  if [[ ! -f assets/css/theme.css ]]; then
    err "Run this from the repo root. assets/css/theme.css not found."
    exit 1
  fi
}

inventory() {
  say "== CSS inventory =="
  for f in assets/css/theme.css assets/css/hub_grid.css assets/css/dashboard.css; do
    if [[ -f "$f" ]]; then
      sz=$(wc -c < "$f" 2>/dev/null || echo 0)
      ok "$f ($sz bytes)"
    else
      warn "$f [MISSING]"
    fi
  done
}

report_before() {
  say "== BEFORE: theme.css lines mentioning .dashboard-cta and !important =="
  grep -nE '\.dashboard-cta' assets/css/theme.css || true
  echo ""
  grep -n '!important' assets/css/theme.css || true
}

apply_patch() {
  say "=== APPLY FIX: remove !important for .dashboard-cta* in theme.css (backup first) ==="
  cp -f assets/css/theme.css assets/css/theme.css.bak

  # Use Python so this works the same on macOS and Linux
  python - <<'PY'
from pathlib import Path
import re

p = Path("assets/css/theme.css")
s = p.read_text(encoding="utf-8")

# We only want to remove !important inside rules that target .dashboard-cta*
# Strategy:
#  1) Split into blocks by '}' (very simple CSS block parsing).
#  2) For blocks with a selector containing ".dashboard-cta", strip "!important" tokens in declarations.
#  3) Reassemble.
blocks = []
for chunk in s.split('}'):
    if not chunk.strip():
        continue
    part = chunk + '}'  # add back the brace we split on
    # selector is up to the first '{'
    try:
        selector, body = part.split('{', 1)
    except ValueError:
        blocks.append(part)
        continue
    if ".dashboard-cta" in selector:
        # remove !important inside this block only
        body = re.sub(r'\s*!important\s*', ' ', body)
        part = selector + '{' + body
    blocks.append(part)

new = "".join(blocks)
if new != s:
    Path("assets/css/theme.css").write_text(new, encoding="utf-8")
    print("Patched: removed !important in .dashboard-cta* rules.")
else:
    print("No changes made (no .dashboard-cta* !important found).")
PY

  ok "Backup at assets/css/theme.css.bak"
}

report_after() {
  say "== AFTER: theme.css lines mentioning .dashboard-cta and any remaining !important =="
  grep -nE '\.dashboard-cta' assets/css/theme.css || true
  echo ""
  grep -n '!important' assets/css/theme.css || echo "  (no !important tokens remain)"
}

reminders() {
  say "Next steps"
  echo "  1) Restart Streamlit (stop/start) to clear session styles."
  echo "  2) Safari: Develop → Empty Caches (or hard reload)."
  echo "  3) Verify hub buttons: they should now pick up styles from assets/css/dashboard.css (the .sn-hub layer)."
}

# --- main ---
repo_check
inventory
report_before

if [[ "${APPLY_FIX}" == "1" ]]; then
  apply_patch
  report_after
  reminders
else
  say "Diagnostics only. To apply the fix:"
  echo "  APPLY_FIX=1 bash ./sn_css_unclobber.sh"
fi

