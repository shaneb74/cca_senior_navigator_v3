#!/usr/bin/env python3
"""Validate that recommended FAQ chips have valid, non-empty answers."""

import json
import sys
from pathlib import Path

# Get paths relative to repo root
repo_root = Path(__file__).parent.parent
faq_path = repo_root / "config" / "faq.json"
recs_path = repo_root / "config" / "faq_recommended.json"

# Load data
faq = {x["id"]: x for x in json.load(open(faq_path))}
recs = json.load(open(recs_path))["items"]

# Validate
missing = []
for r in recs:
    item = faq.get(r["id"])
    if not item:
        missing.append(("missing", r["id"]))
    elif not item.get("answer") or len(item["answer"].strip()) < 20:
        missing.append(("empty_answer", r["id"]))

if missing:
    print("❌ FAQ recs validation failed:")
    for issue_type, faq_id in missing:
        if issue_type == "missing":
            print(f"  - FAQ ID '{faq_id}' not found in faq.json")
        else:
            print(f"  - FAQ ID '{faq_id}' has empty or too-short answer")
    sys.exit(1)

print("✅ FAQ recs OK - all recommended questions have valid answers")
