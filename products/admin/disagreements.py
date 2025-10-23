"""
GCP Disagreement Reviewer

Streamlit UI for reviewing disagreement cases and tagging gold tiers.

Usage:
    streamlit run products/admin/disagreements.py
"""

import json
import pathlib
import streamlit as st

CASES = pathlib.Path("data/training/gcp_cases.jsonl")
LABELS = pathlib.Path("data/training/gcp_labels.jsonl")
ALLOWED = ["none", "in_home", "assisted_living", "memory_care", "memory_care_high_acuity"]

st.set_page_config(page_title="GCP Disagreement Reviewer", layout="wide")
st.title("🔍 GCP Disagreement Reviewer")
st.caption("Review cases where deterministic and LLM tiers disagree, tag gold tier")


def load_jsonl(p: pathlib.Path) -> list[dict]:
    """Load JSONL file into list of dicts."""
    if not p.exists():
        return []
    return [json.loads(line) for line in p.open("r", encoding="utf-8") if line.strip()]


# Load data
cases = load_jsonl(CASES)
labels = {r["id"]: r for r in load_jsonl(LABELS)}

st.markdown(f"**{len(cases)}** cases • **{len(labels)}** labeled • **{len(cases) - len(labels)}** unlabeled")
st.markdown("---")

# Filters
st.markdown("### Filters")
col1, col2, col3 = st.columns(3)

with col1:
    sel_cog = st.multiselect(
        "Cognition band",
        ["none", "mild", "moderate", "high"],
        default=["moderate", "high"]
    )

with col2:
    sel_sup = st.multiselect(
        "Support band",
        ["low", "moderate", "high", "24h"],
        default=["high", "24h"]
    )

with col3:
    show_labeled = st.checkbox("Show labeled only", value=False)

# Filter cases
todo = []
for c in cases:
    # Band filter
    if c["bands"]["cog"] not in sel_cog:
        continue
    if c["bands"]["sup"] not in sel_sup:
        continue
    
    # Labeled filter
    if show_labeled and c["id"] not in labels:
        continue
    
    todo.append(c)

st.markdown(f"**{len(todo)}** cases match filters (showing first 50)")
st.markdown("---")

# Display cases
for idx, c in enumerate(todo[:50]):
    cid = c["id"]
    current_label = labels.get(cid, {})
    
    st.markdown(f"### Case {idx + 1}: `{cid}`")
    
    # Summary row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Deterministic", c["det_tier"])
    with col2:
        st.metric("LLM", c["llm_tier"])
    with col3:
        st.metric("LLM Confidence", f"{c.get('llm_conf', 0):.2f}")
    with col4:
        if current_label.get("gold_tier"):
            st.metric("Gold (saved)", current_label["gold_tier"])
    
    # Bands and flags
    st.text(f"Bands: cognition={c['bands']['cog']} × support={c['bands']['sup']}")
    st.text(f"Risky behaviors: {c['has_risky_behaviors']}")
    st.text(f"Allowed tiers: {', '.join(c.get('allowed_tiers', []))}")
    
    # LLM reasons
    with st.expander("💬 LLM Reasons", expanded=False):
        reasons = c.get("reasons", [])
        if reasons:
            for r in reasons[:6]:
                st.markdown(f"- {r}")
        else:
            st.caption("No reasons provided")
    
    # GCP context
    with st.expander("📋 GCP Context (flags, scores)", expanded=False):
        st.json(c["gcp_context"])
    
    # Gold tier selection
    col_gold, col_note = st.columns([1, 2])
    
    with col_gold:
        current_gold = current_label.get("gold_tier")
        gold_index = ALLOWED.index(current_gold) if current_gold in ALLOWED else 2  # Default to AL
        
        gold = st.selectbox(
            "Gold tier",
            ALLOWED,
            index=gold_index,
            key=f"gold_{cid}"
        )
    
    with col_note:
        note = st.text_input(
            "Note (optional)",
            value=current_label.get("note", ""),
            key=f"note_{cid}"
        )
    
    # Save button
    if st.button(f"💾 Save Gold Tier", key=f"save_{cid}"):
        from tools.log_disagreement import append_label
        append_label(cid, gold, note if note else None)
        st.success(f"✓ Saved: {cid} → {gold}")
        st.rerun()
    
    st.markdown("---")

# Footer
if len(todo) == 0:
    st.info("No cases match current filters. Adjust filters above.")
elif len(todo) > 50:
    st.warning(f"Showing first 50 of {len(todo)} cases. Use filters to narrow down.")
