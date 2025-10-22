#!/usr/bin/env bash
# Pre-Commit Hook Template
# Copy this to .git/hooks/pre-commit and chmod +x it
# Usage: cp docs/PRE_COMMIT_HOOK_TEMPLATE.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

echo "[pre-commit] Running repository guards..."

# Guard 1: Block backup files from being committed
blocked=$(git diff --cached --name-only | grep -E '\.bak([0-9]+)?$|\.bak_|_bak[0-9]+|_backup[0-9]+' || true)
if [ -n "$blocked" ]; then
  echo "❌ Backup files detected in commit. Remove or unstage these:"
  echo "$blocked" | sed 's/^/   - /'
  exit 1
fi

# Guard 2: Ensure only one module.json under products/
module_json_count=$(git diff --cached --name-only | grep -E '^products/.*module\.json$' | wc -l | tr -d ' ')
if [ "$module_json_count" -gt 0 ]; then
  total_count=$(find products -type f -name module.json 2>/dev/null | wc -l | tr -d ' ')
  if [ "$total_count" -gt 1 ]; then
    echo "❌ Multiple module.json files detected under products/:"
    find products -type f -name module.json | sed 's/^/   - /'
    echo ""
    echo "Only ONE module.json allowed (canonical: products/gcp_v4/modules/care_recommendation/module.json)"
    exit 1
  fi
fi

# Guard 3: Block legacy GCP imports (gcp_v1/v2/v3)
staged_py_files=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.py$' || true)
if [ -n "$staged_py_files" ]; then
  legacy_imports=$(echo "$staged_py_files" | xargs grep -l 'products\.gcp_v[123]\b' 2>/dev/null || true)
  if [ -n "$legacy_imports" ]; then
    echo "❌ Legacy GCP imports detected (gcp_v1/v2/v3):"
    echo "$legacy_imports" | sed 's/^/   - /'
    echo ""
    echo "Use products.gcp_v4 instead."
    exit 1
  fi
fi

echo "[pre-commit] ✓ All guards passed"
exit 0
