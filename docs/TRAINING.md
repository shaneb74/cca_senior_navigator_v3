# GCP Disagreement Logging & Training

## Overview

When the deterministic GCP engine and LLM recommendations disagree, cases are automatically logged to `data/training/gcp_cases.jsonl` for review and evaluation.

**No PHI is recorded** - only tier recommendations, cognition/support bands, flags, and context needed for analysis.

## Files

- **`data/training/gcp_cases.jsonl`** - Logged disagreement cases
- **`data/training/gcp_labels.jsonl`** - Human-labeled gold tiers
- **`tools/log_disagreement.py`** - JSONL append helpers
- **`tools/eval_gcp.py`** - Evaluation script (accuracy, confusion matrix)
- **`products/admin/disagreements.py`** - Streamlit reviewer UI

## Workflow

### 1. Cases are logged automatically

When `FEATURE_LLM_GCP` is set to `shadow` or `assist` and tiers disagree:

```python
[GCP_LLM_NOTE] mismatch: llm=memory_care vs det=assisted_living; detWins=True (conf=0.85)
[GCP_LOG] disagreement captured id=a1b2c3d4e5f6g7h8
```

Each case includes:
- Deterministic tier (`det_tier`)
- LLM tier (`llm_tier`)  
- LLM confidence (`llm_conf`)
- Cognition band (`cog: none|mild|moderate|high`)
- Support band (`sup: low|moderate|high|24h`)
- Risky behaviors flag (`has_risky_behaviors`)
- LLM reasons (first 6)
- Allowed tiers (from cognitive gate)
- Timestamp

### 2. Review cases and tag gold tiers

Run the reviewer UI:

```bash
streamlit run products/admin/disagreements.py
```

**Features:**
- Filter by cognition/support bands
- View case details (det tier, LLM tier, confidence, reasons, context)
- Tag gold tier (correct answer)
- Add optional notes
- Save labels to `gcp_labels.jsonl`

### 3. Evaluate accuracy and patterns

Run the evaluator:

```bash
python tools/eval_gcp.py
```

**Output:**
- Total cases (labeled vs unlabeled)
- Accuracy: deterministic vs gold, LLM vs gold
- Confusion matrices (both engines)
- Key slice analysis: moderate×high without risky behaviors
- Band distributions

## Example Output

```
======================================================================
GCP DISAGREEMENT EVALUATION
======================================================================

Total cases: 127
Labeled:     45
Unlabeled:   82

======================================================================
ACCURACY
======================================================================
Deterministic vs Gold: 0.756
LLM vs Gold:           0.822

======================================================================
CONFUSION MATRIX: Deterministic vs Gold
======================================================================
(rows=gold, cols=predicted, values=rate)
                        assisted_living  memory_care
assisted_living                    0.85         0.15
memory_care                        0.32         0.68

======================================================================
KEY SLICE: Moderate×High, No Risky Behaviors (n=18)
======================================================================
Deterministic → MC rate: 0.778
LLM → MC rate:           0.389
Gold = AL rate:          0.611
Gold = MC rate:          0.389
```

## Use Cases

### Training

Labeled cases can be used to:
- Fine-tune LLM prompts
- Adjust deterministic scoring weights
- Identify edge cases for rule improvements

### Calibration

Analyze slices to understand:
- When cognition band alone drives MC (vs behaviors)
- Moderate×high patterns (ADLs vs memory)
- Confidence calibration (LLM vs actual accuracy)

### Validation

Compare engines:
- Which performs better overall?
- Which performs better on specific slices?
- Where do they systematically disagree?

## Privacy

**No PHI is logged:**
- ✅ Tier recommendations (canonical values only)
- ✅ Bands (cognition, support - categorical)
- ✅ Flags (boolean indicators)
- ✅ Counts (BADL count, IADL count)
- ❌ Names, DOB, addresses, medical details
- ❌ Free-text responses
- ❌ Identifiers

All cases are stored locally in `data/training/` and never transmitted.
