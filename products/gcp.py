from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List, Optional

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
STEP_KEY = "gcp_section_idx"


def _ensure_state() -> None:
    st.session_state.setdefault("gcp", {"answers": {}, "scores": {}, "summary": None})
    st.session_state.setdefault("care_profile", {})
    st.session_state.setdefault(ACK_KEY, False)
    st.session_state.setdefault(STEP_KEY, 0)


def _options(q: Dict[str, Any]) -> List[Dict[str, Any]]:
    return q.get("options") or q.get("choices") or []


def _radio(qid: str, labels: List[str], values: List[str], current: Optional[str]) -> str:
    index = values.index(current) if (current in values) else 0
    chosen = st.radio(
        " ",
        labels,
        index=index,
        label_visibility="collapsed",
        key=f"gcp_ans_{qid}",
    )
    return values[labels.index(chosen)]


def _select(
    qid: str,
    labels: List[str],
    values: List[str],
    current: Optional[str],
    placeholder: str = "Choose an option",
) -> Optional[str]:
    index = values.index(current) if (current in values) else None
    chosen = st.selectbox(
        " ",
        labels,
        index=index,
        placeholder=placeholder,
        label_visibility="collapsed",
        key=f"gcp_ans_{qid}",
    )
    if chosen is None:
        return None
    return values[labels.index(chosen)]


def _multiselect(qid: str, labels: List[str], values: List[str], current: List[str]) -> List[str]:
    default_labels = [labels[values.index(v)] for v in current if v in values]
    chosen_labels = st.multiselect(
        " ",
        labels,
        default=default_labels,
        label_visibility="collapsed",
        key=f"gcp_ans_{qid}",
    )
    return [values[labels.index(lbl)] for lbl in chosen_labels]


def _render_question(q: Dict[str, Any]) -> None:
    qid = q.get("id") or q.get("key")
    if not qid:
        st.warning("Question missing id/key")
        return

    qlabel = q.get("label", qid)
    qhelp = q.get("help")
    qtype = (q.get("type") or q.get("ui") or "single").lower()
    opts = _options(q)

    st.markdown(f"**{qlabel}**")
    if qhelp:
        st.caption(qhelp)

    answers = st.session_state["gcp"]["answers"]
    current = answers.get(qid)

    if qtype in ("single", "radio"):
        if not opts:
            st.warning(f"Missing options for {qid}")
            return
        labels = [o["label"] for o in opts]
        values = [o["value"] for o in opts]
        if qid == ELIG_QID:
            selected = _select(qid, labels, values, current if isinstance(current, str) else None)
            if selected is not None:
                answers[qid] = selected
        else:
            answers[qid] = _radio(qid, labels, values, current if isinstance(current, str) else None)

    elif qtype in ("multi", "checkboxes"):
        if not opts:
            st.warning(f"Missing options for {qid}")
            return
        current_dict = current if isinstance(current, dict) else {}
        selected: Dict[str, bool] = {}
        cols = st.columns(min(3, len(opts)))
        for i, o in enumerate(opts):
            ck_key = f"g_{qid}_{o['value']}"
            with cols[i % len(cols)]:
                ck = st.checkbox(o["label"], value=bool(current_dict.get(o["value"])), key=ck_key)
            selected[o["value"]] = ck
        answers[qid] = selected

    elif qtype in ("multiselect",):
        if not opts:
            st.warning(f"Missing options for {qid}")
            return
        labels = [o["label"] for o in opts]
        values = [o["value"] for o in opts]
        current_list = current if isinstance(current, list) else []
        answers[qid] = _multiselect(qid, labels, values, current_list)

    elif qtype in ("select", "dropdown"):
        if not opts:
            st.warning(f"Missing options for {qid}")
            return
        labels = [o["label"] for o in opts]
        values = [o["value"] for o in opts]
        selected = _select(qid, labels, values, current if isinstance(current, str) else None)
        if selected is not None:
            answers[qid] = selected

    elif qtype == "scale":
        min_v = int(q.get("min", 0))
        max_v = int(q.get("max", 10))
        step = int(q.get("step", 1))
        default = int(current if isinstance(current, int) else q.get("default", min_v))
        answers[qid] = st.slider(
            " ",
            min_v,
            max_v,
            default,
            step,
            label_visibility="collapsed",
            key=f"gcp_ans_{qid}",
        )

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
        elif isinstance(ans, list):
            if aval in [str(v) for v in ans]:
                totals[setting] += pts
        else:
            if str(ans) == aval:
                totals[setting] += pts
    return {s: totals.get(s, 0.0) for s in SETTINGS_ORDER}


def _pick_recommendation(scores: Dict[str, float]) -> str:
    return max(scores.items(), key=lambda kv: kv[1])[0] if scores else "In-Home Care"


def _medicaid_gate(answers: Dict[str, Any], blurbs: Dict[str, str]) -> None:
    val = str(answers.get(ELIG_QID, "")).lower()
    needs_ack = val in ("yes", "unsure")
    if not needs_ack:
        st.session_state[ACK_KEY] = True
        return

    st.session_state[ACK_KEY] = False
    if tip := blurbs.get("medicaid_clarify"):
        st.info(tip)

    st.markdown(
        f"""
<div class=\"banner banner--info\">
  {blurbs.get('medicaid_ack', 'You can still complete the plan and estimator, but placement services are limited for Medicaid.')}
  <br/>
  <a class=\"btn btn--secondary\" href=\"https://www.medicaid.gov/\" target=\"_blank\" rel=\"noopener\">Open Medicaid.gov</a>
  <a class=\"btn btn--ghost\" href=\"https://www.medicaid.gov/medicaid/long-term-services-supports\" target=\"_blank\" rel=\"noopener\">LTSS (Medicaid)</a>
</div>
""",
        unsafe_allow_html=True,
    )
    st.session_state[ACK_KEY] = st.checkbox(
        "I understand", value=st.session_state.get(ACK_KEY, False), key=ACK_KEY
    )


def render() -> None:
    _ensure_state()
    schema = load_schema()
    blurbs = load_blurbs()

    st.header("Guided Care Plan")
    if lead := blurbs.get("gcp_intro"):
        st.caption(lead)

    sections = schema.get("sections", [])
    step = max(0, min(st.session_state[STEP_KEY], max(len(sections) - 1, 0)))
    st.session_state[STEP_KEY] = step

    if sections:
        st.caption(f"Section {step + 1} of {len(sections)}")

    if sections:
        section = sections[step]
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

    prev_col, next_col, complete_col = st.columns([1, 1, 1])
    with prev_col:
        if st.button("◀︎ Previous", disabled=(step == 0)):
            st.session_state[STEP_KEY] = max(step - 1, 0)
            st.rerun()
    with next_col:
        if step < len(sections) - 1:
            if st.button("Next ▶︎"):
                st.session_state[STEP_KEY] = min(step + 1, len(sections) - 1)
                st.rerun()
    with complete_col:
        disabled = (
            str(answers.get(ELIG_QID, "")).lower() in ("yes", "unsure")
            and not st.session_state.get(ACK_KEY, False)
        )
        if st.button("Complete", disabled=disabled):
            scores = _score(answers)
            recommendation = _pick_recommendation(scores)
            st.session_state["gcp"]["scores"] = scores
            st.session_state["gcp_completed"] = True
            st.session_state["gcp_recommendation"] = recommendation
            st.session_state["care_profile"] = {
                "care_setting": recommendation,
                "scores": scores,
                "answers": answers,
                "elig_medicaid": answers.get(ELIG_QID),
                "medicaid_acknowledged": st.session_state.get(ACK_KEY, False),
            }
            log_event("gcp.completed", {"recommendation": recommendation})
            st.success(f"Recommendation: **{recommendation}**")
            st.markdown(
                """
<div class=\"kit-row\">
  <a class=\"btn btn--secondary\" href=\"?page=hub_concierge\">Back to Hub</a>
  <a class=\"btn btn--primary\" href=\"?page=cost_planner\">Continue to Cost Planner</a>
</div>
""",
                unsafe_allow_html=True,
            )
        if disabled:
            st.caption("Please acknowledge the Medicaid notice to continue.")
