import csv
import json
import pathlib

root = pathlib.Path(__file__).resolve().parents[1]
cfg = root / "config"

scoring_csv = cfg / "gcp_v3_scoring.csv"
blurbs_csv = cfg / "gcp_v3_conversational_blurbs.csv"

scoring_json = cfg / "gcp_scoring.json"
blurbs_json = cfg / "gcp_blurbs.json"

# --- Scoring: rows -> objects ---
# Expected CSV headers: question_id,answer_value,setting,points
if scoring_csv.exists():
    with scoring_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            if not r.get("question_id"):
                continue
            rows.append(
                {
                    "question_id": r["question_id"].strip(),
                    "answer_value": r["answer_value"].strip(),
                    "setting": r["setting"].strip(),
                    "points": float(r["points"]),
                }
            )
    scoring_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {scoring_json} ({len(rows)} rows).")
else:
    print(f"[WARN] Missing {scoring_csv} — skipping scoring conversion.")

# --- Blurbs: key,text -> {key: text} (first comma splits) ---
if blurbs_csv.exists():
    out = {}
    with blurbs_csv.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    start = 1 if lines and lines[0].lower().startswith("key,") else 0

    for raw in lines[start:]:
        line = raw.rstrip("\r\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "," not in line:
            continue
        key, text = line.split(",", 1)
        out[key.strip()] = text.strip().strip('"')

    blurbs_json.write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[OK] Wrote {blurbs_json} ({len(out)} keys).")
else:
    print(f"[WARN] Missing {blurbs_csv} — skipping blurbs conversion.")
