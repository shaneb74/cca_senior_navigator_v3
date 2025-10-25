"""
Disagreement logging for GCP training.

Appends JSONL rows when deterministic and LLM tiers disagree.
No PHI is recorded - only tier recommendations, bands, flags, and context.

Files:
- data/training/gcp_cases.jsonl: disagreement cases
- data/training/gcp_labels.jsonl: gold tier labels from reviewer
"""

import hashlib
import json
import pathlib
import time

OUT = pathlib.Path("data/training/gcp_cases.jsonl")
LBL = pathlib.Path("data/training/gcp_labels.jsonl")


def _mk_id(payload: dict) -> str:
    """Generate stable case ID via hash (no PHI).
    
    Args:
        payload: Case data with det_tier, llm_tier, bands, flags
        
    Returns:
        16-character hex hash
    """
    # Stable id: hash of salient fields (no PHI)
    src = json.dumps({
        "ts": int(time.time()) // 60,  # minute bucket
        "det": payload.get("det_tier"),
        "llm": payload.get("llm_tier"),
        "bands": payload.get("bands"),
        "flags": sorted(payload.get("gcp_context", {}).get("flags", []))
    }, sort_keys=True)
    return hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]


def append_case(row: dict) -> str:
    """Append disagreement case to JSONL file.
    
    Args:
        row: Case data (det_tier, llm_tier, bands, flags, etc.)
        
    Returns:
        Case ID
    """
    OUT.parent.mkdir(parents=True, exist_ok=True)
    row = dict(row)
    row["ts"] = int(time.time())
    row["id"] = _mk_id(row)

    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return row["id"]


def append_label(case_id: str, gold_tier: str, note: str | None = None):
    """Append gold tier label for a case.
    
    Args:
        case_id: Case ID from append_case()
        gold_tier: Human-labeled gold tier
        note: Optional reviewer note
    """
    LBL.parent.mkdir(parents=True, exist_ok=True)

    rec = {
        "id": case_id,
        "gold_tier": gold_tier,
        "ts": int(time.time())
    }
    if note:
        rec["note"] = note

    with LBL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
