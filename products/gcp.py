from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List

import streamlit as st

from core.data import load_blurbs, load_schema, load_scoring
from core.events import log_event

SETTINGS_ORDER = [
    "In-Home Care",
    "Assisted Living",
    "Memory Care",
    "Memory Care High Acuity",
]

ELIG_QID = "elig_medicaid"
ACK_KEY = "elig_medicaid_ack"


def _ensure_state():
    st.session_state.setdefault("gcp", {"answers": {}, "scores": {}, "summary": None})
    st.session_state.setdefault("care_profile", {})
    st.session_state.setdefault(ACK_KEY, False)


def _opts(q: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw = q.get("options") or q.get("choices")
    if not raw:
        return []
    normalised: List[Dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            label = item.get("label") or item.get("title") or item.get("value")
            value = item.get("value") or label
        else:
            label = str(item)
            value = label
        normalised.append({"label": str(label), "value": str(value)})
    return normalised


def _render_question(q: Dict[str, Any]):
    qid = q.get("id") or q.get("key")
    if not qid:
        st.warning("Question missing id/key")
        return

    qlabel = q.get("label", qid)
    qhelp = q.get("help")
    qtype = (q.get("type") or q.get("ui") or "single").lower()
    opts = _opts(q)

    st.markdown(f"**{qlabel}**")
    if qhelp:
        st.caption(qhelp)

    key = f"gcp_ans_{qid}"
    answers = st.session_state["gcp"]["answers"]

    if qtype in ("single", "radio"):
        if not opts:
            st.warning(f"Missing options for {qid}")
            return
        labels = [o["label"] for o in opts]
        values = [o["value"] for o in opts]
        idx = 0
        if qid in answers and answers[qid] in values:
            idx = values.index(answers[qid])
        choice = st.radio(" ", labels, index=idx, label_visibility="collapsed", key=key)
        answers[qid] = values[labels.index(choice)]

    elif qtype in ("multi", "checkboxes"):
        if not opts:
            st.warning(f"Missing options for {qid}")
            return
        current = answers.get(qid, {})
        sel = {}
        cols = st.columns(min(3, len(opts)))
        for i, opt in enumerate(opts):
            with cols[i % len(cols)]:
                ck = st.checkbox(opt["label"], value=bool(current.get(opt["value"])), key=f"{key}_{opt['value']}")
                sel[opt["value"]] = ck
        answers[qid] = sel

    elif qtype in ("select", "dropdown"):
        if not opts:
            st.warning(f"Missing options for {qid}")
            return
        labels = [o["label"] for o in opts]
        values = [o["value"] for o in opts]
        idx = 0
        if qid in answers and answers[qid] in values:
            idx = values.index(answers[qid])
        label = st.selectbox(" ", labels, index=idx, label_visibility="collapsed", key=key)
        answers[qid] = values[labels.index(label)]

    elif qtype == "scale":
        minimum = int(q.get("min", 0))
        maximum = int(q.get("max", 10))
        step = int(q.get("step", 1))
        default = int(answers.get(qid, q.get("default", minimum)))
        answers[qid] = st.slider(" ", minimum, maximum, default, step, label_visibility="collapsed", key=key)

    else:
        st.warning(f"Unsupported question type '{qtype}' for {qid}")


def _score(answers: Dict[str, Any]) -> Dict[str, float]:
    df = load_scoring()
    totals = defaultdict(float)
    for _, row in df.iterrows():
        qid = row["question_id"]
        aval = str(row["answer_value"])
        setting = row["setting"]
        pts = float(row["points"])
        if qid not in answers:
            continue
        ans = answers[qid]
        if isinstance(ans, dict):
            if ans.get(aval, False):
                totals[setting] += pts
        else:
            if str(ans) == aval:
                totals[setting] += pts
    return {s: totals.get(s, 0.0) for s in SETTINGS_ORDER}


def _pick_recommendation(scores: Dict[str, float]) -> str:
    return max(scores.items(), key=lambda kv: kv[1])[0] if scores else "In-Home Care"


def _medicaid_gate(answers: Dict[str, Any], blurbs: Dict[str, str]):
    val = str(answers.get(ELIG_QID, "")).lower()
    needs_ack = val in {"yes", "unsure"}
    if not needs_ack:
        st.session_state[ACK_KEY] = True
        return

    st.session_state[ACK_KEY] = False
    st.info(blurbs.get("medicaid_clarify", "Medicaid is different from Medicare. We can work with Medicare."))
    st.markdown(
        f"""
<div class='banner banner--info'>
  {blurbs.get('medicaid_ack', 'Our advisors can’t arrange placement for Medicaid cases, but you can complete the plan and estimator.')}
  <br/>
  <a class='btn btn--secondary' href='https://www.medicaid.gov/' target='_blank' rel='noopener'>Open Medicaid.gov</a>
  <a class='btn btn--ghost' href='https://www.medicaid.gov/medicaid/long-term-services-supports' target='_blank' rel='noopener'>LTSS (Medicaid)</a>
</div>
""",
        unsafe_allow_html=True,
    )
    st.session_state[ACK_KEY] = st.checkbox("I understand", value=st.session_state.get(ACK_KEY, False))


def render():
    _ensure_state()
    st.header("Guided Care Plan")

    schema = load_schema()
    blurbs = load_blurbs()

    if lead := blurbs.get("gcp_intro"):
        st.caption(lead)

    for section in schema.get("sections", []):
        title = section.get("title") or section.get("name") or ""
        if title:
            st.subheader(title)
        for q in section.get("questions", []):
            if not q.get("id") and q.get("key"):
                q["id"] = q["key"]
            _render_question(q)
        st.divider()

    answers = st.session_state["gcp"]["answers"]
    _medicaid_gate(answers, blurbs)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save progress"):
            st.success("Progress saved.")

    with col2:
        disabled = False
        if str(answers.get(ELIG_QID, "")).lower() in {"yes", "unsure"} and not st.session_state[ACK_KEY]:
            disabled = True
        if st.button("Complete", disabled=disabled):
            scores = _score(answers)
            rec = _pick_recommendation(scores)
            st.session_state["gcp"]["scores"] = scores
            st.session_state["gcp_completed"] = True
            st.session_state["gcp_recommendation"] = rec
            st.session_state["care_profile"] = {
                "care_setting": rec,
                "scores": scores,
                "answers": answers,
                "elig_medicaid": answers.get(ELIG_QID),
                "medicaid_acknowledged": st.session_state.get(ACK_KEY, False),
            }
            log_event("gcp.completed", {"recommendation": rec})
            st.success(f"Recommendation: **{rec}**")
            st.markdown(
                """
<div class="kit-row">
  <a class="btn btn--secondary" href="?page=hub_concierge">Back to Hub</a>
  <a class="btn btn--primary" href="?page=cost_planner">Continue to Cost Planner</a>
</div>
""",
                unsafe_allow_html=True,
            )
        if disabled:
            st.caption("Please acknowledge the Medicaid notice to continue.")
