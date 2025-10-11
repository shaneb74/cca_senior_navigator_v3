#!/usr/bin/env python3
"""
One-time migration helper to convert the legacy GCP CSV exports into JSON.

The upstream CSVs were authored without quoting, so fields that contain commas
end up shifting subsequent columns. This script rehydrates those rows using a
set of heuristics that match the known column layout.

Usage:
    python scripts/migrate_gcp_csv_to_json.py \
        config/gcp_v3_scoring.csv \
        config/gcp_v3_conversational_blurbs.csv
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "config" / "gcp"
OUT_SCORING = OUT_DIR / "scoring.json"
OUT_BLURBS = OUT_DIR / "blurbs.json"

VALID_DOMAINS = {
    "Funding",
    "ADL/IADL Burden",
    "Support Network",
    "Cognitive Function",
    "Medication Complexity",
    "Mobility & Falls",
    "Health & Chronic Conditions",
    "Geographic Isolation",
    "Emotional Health",
}


def _read_lines(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8") as handle:
        lines = handle.readlines()
    # Drop header
    return [line.rstrip("\n") for line in lines[1:] if line.strip()]


def _parse_scoring_line(line: str) -> Dict[str, str]:
    parts = line.split(",")
    if len(parts) < 10:
        parts += [""] * (10 - len(parts))

    question_id = parts[0].strip()
    section = parts[1].strip()
    remainder = parts[2:]

    domain_idx = None
    for idx, token in enumerate(remainder):
        if token.strip() in VALID_DOMAINS:
            domain_idx = idx
            break
    if domain_idx is None:
        raise ValueError(f"Could not find Domain column in line:\n{line}")

    question = ",".join(remainder[:domain_idx]).strip()
    domain = remainder[domain_idx].strip()
    tail = remainder[domain_idx + 1 :]

    def _maybe_number(value: str) -> float | None:
        if not value:
            return None
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return None

    pos = 0
    answer_tokens: List[str] = []
    while pos < len(tail):
        candidate = tail[pos].strip()
        if _maybe_number(candidate) is not None:
            break
        answer_tokens.append(candidate)
        pos += 1

    answer_option = ", ".join(token.strip() for token in answer_tokens if token is not None).strip(
        ", "
    )

    score_value = None
    if pos < len(tail):
        score_value = _maybe_number(tail[pos].strip())
        pos += 1

    domain_weight = None
    if pos < len(tail):
        domain_weight = _maybe_number(tail[pos].strip())
        pos += 1

    flags_emitted = ""
    if pos < len(tail):
        flags_emitted = tail[pos].strip()
        pos += 1

    remaining = tail[pos:]
    if not remaining:
        gating_logic = ""
        notes = ""
    elif len(remaining) == 1:
        gating_logic = remaining[0].strip()
        notes = ""
    else:
        gating_tokens = remaining[:-1]
        notes_tokens = remaining[-1:]
        gating_logic = ",".join(gating_tokens).strip()
        notes = ",".join(notes_tokens).strip()

    if answer_option == "" and answer_tokens:
        answer_option = ",".join(answer_tokens).strip()

    def _maybe_number(value: str) -> float | None:
        if not value:
            return None
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return None

    return {
        "QuestionID": question_id,
        "Section": section,
        "Question": question,
        "Domain": domain,
        "AnswerOption": answer_option,
        "ScoreValue": score_value,
        "DomainWeight": domain_weight,
        "FlagsEmitted": flags_emitted,
        "GatingLogic": gating_logic,
        "Notes": notes,
    }


def migrate_scoring(csv_path: Path) -> Dict[str, List[Dict[str, str]]]:
    rows: List[Dict[str, str]] = []
    for line in _read_lines(csv_path):
        if line.startswith("RULE,"):
            continue
        rows.append(_parse_scoring_line(line))
    return {"scoring": rows}


def _parse_blurbs_line(line: str) -> Dict[str, object]:
    parts = line.split(",")
    if len(parts) < 6:
        parts += [""] * (6 - len(parts))

    question_id = parts[0].strip()
    remainder = parts[1:]

    # We need to recover the question text until the remaining tokens equal 4
    # (answer option + three variants).
    idx = 0
    while len(remainder) - idx > 4:
        idx += 1
    question = ",".join(remainder[:idx]).strip()
    tail = remainder[idx:]

    if len(tail) < 4:
        tail += [""] * (4 - len(tail))

    answer_option = tail[0].strip()
    variants = [v.strip() for v in tail[1:] if v.strip()]

    return {
        "QuestionID": question_id,
        "Question": question,
        "AnswerOption": answer_option,
        "text": variants,
    }


def migrate_blurbs(csv_path: Path) -> Dict[str, object]:
    rows = [_parse_blurbs_line(line) for line in _read_lines(csv_path)]
    return {"byAnswer": rows}


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(
            "Usage: python scripts/migrate_gcp_csv_to_json.py "
            "<legacy_scoring.csv> <legacy_blurbs.csv>"
        )
        return 1

    scoring_csv = Path(argv[1])
    blurbs_csv = Path(argv[2])
    if not scoring_csv.is_file():
        print(f"[error] cannot find scoring CSV: {scoring_csv}")
        return 1
    if not blurbs_csv.is_file():
        print(f"[error] cannot find blurbs CSV: {blurbs_csv}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    scoring_payload = migrate_scoring(scoring_csv)
    blurbs_payload = migrate_blurbs(blurbs_csv)

    with OUT_SCORING.open("w", encoding="utf-8") as handle:
        json.dump(scoring_payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with OUT_BLURBS.open("w", encoding="utf-8") as handle:
        json.dump(blurbs_payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"[ok] wrote {OUT_SCORING}")
    print(f"[ok] wrote {OUT_BLURBS}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
