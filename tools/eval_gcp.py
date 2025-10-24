#!/usr/bin/env python3
"""
GCP Disagreement Evaluator

Analyzes disagreement cases and labels to compute:
- Accuracy (deterministic vs gold, LLM vs gold)
- Confusion matrices
- Key slices (e.g., moderate×high without risky behaviors)

Usage:
    python tools/eval_gcp.py
"""

import json
import pathlib

import pandas as pd

CASES = pathlib.Path("data/training/gcp_cases.jsonl")
LABELS = pathlib.Path("data/training/gcp_labels.jsonl")


def load_jsonl(p: pathlib.Path) -> list[dict]:
    """Load JSONL file into list of dicts."""
    if not p.exists():
        return []
    return [json.loads(line) for line in p.open("r", encoding="utf-8") if line.strip()]


def main():
    """Run evaluation on disagreement cases."""

    cases = load_jsonl(CASES)
    labels = {r["id"]: r for r in load_jsonl(LABELS)}

    # Build dataframe
    rows = []
    for c in cases:
        cid = c["id"]
        gold = labels.get(cid, {}).get("gold_tier")
        rows.append({
            "id": cid,
            "det": c["det_tier"],
            "llm": c["llm_tier"],
            "gold": gold,
            "cog": c["bands"]["cog"],
            "sup": c["bands"]["sup"],
            "risky": c.get("has_risky_behaviors", False)
        })

    df = pd.DataFrame(rows)

    print("=" * 70)
    print("GCP DISAGREEMENT EVALUATION")
    print("=" * 70)
    print(f"\nTotal cases: {len(df)}")
    print(f"Labeled:     {df['gold'].notna().sum()}")
    print(f"Unlabeled:   {df['gold'].isna().sum()}")

    if df["gold"].notna().sum() == 0:
        print("\n⚠️  No labels yet. Run the reviewer to tag gold_tier.")
        print("   Command: streamlit run products/admin/disagreements.py")
        return

    # Filter to labeled cases
    lab = df[df["gold"].notna()].copy()

    # Accuracy
    def acc(pred):
        return (lab[pred] == lab["gold"]).mean()

    print("\n" + "=" * 70)
    print("ACCURACY")
    print("=" * 70)
    print(f"Deterministic vs Gold: {acc('det'):.3f}")
    print(f"LLM vs Gold:           {acc('llm'):.3f}")

    # Confusion matrices
    print("\n" + "=" * 70)
    print("CONFUSION MATRIX: Deterministic vs Gold")
    print("=" * 70)
    print("(rows=gold, cols=predicted, values=rate)")
    print(pd.crosstab(lab["gold"], lab["det"], normalize="index").round(2))

    print("\n" + "=" * 70)
    print("CONFUSION MATRIX: LLM vs Gold")
    print("=" * 70)
    print("(rows=gold, cols=predicted, values=rate)")
    print(pd.crosstab(lab["gold"], lab["llm"], normalize="index").round(2))

    # Key slice: moderate × high without risky behaviors
    sl = lab[(lab["cog"] == "moderate") & (lab["sup"] == "high") & (~lab["risky"])]

    if len(sl):
        print("\n" + "=" * 70)
        print(f"KEY SLICE: Moderate×High, No Risky Behaviors (n={len(sl)})")
        print("=" * 70)
        print(f"Deterministic → MC rate: {(sl['det']=='memory_care').mean():.3f}")
        print(f"LLM → MC rate:           {(sl['llm']=='memory_care').mean():.3f}")
        print(f"Gold = AL rate:          {(sl['gold']=='assisted_living').mean():.3f}")
        print(f"Gold = MC rate:          {(sl['gold']=='memory_care').mean():.3f}")

    # Band distribution
    print("\n" + "=" * 70)
    print("BAND DISTRIBUTION (labeled cases)")
    print("=" * 70)
    print("\nCognition:")
    print(lab["cog"].value_counts().sort_index())
    print("\nSupport:")
    print(lab["sup"].value_counts().sort_index())
    print("\nRisky behaviors:")
    print(lab["risky"].value_counts())

    print("\n" + "=" * 70)
    print("✓ Evaluation complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
