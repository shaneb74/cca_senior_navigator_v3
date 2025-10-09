from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from core.data import load_blurbs, load_schema, load_scoring
from core.events import log_event
from core.forms import section_header, subject_name

SETTINGS_ORDER = [
    "In-Home Care",
    "Assisted Living",
    "Memory Care",
    "Memory Care High Acuity",
]

ELIG_QID = "elig_medicaid"
STEP_KEY = "gcp_step"
ACK_KEY = "gcp_ack_ok"


def _opt_pair(opt: Any) -> Tuple[str, str]:
    """Normalize option definitions to (label, value)."""
    if isinstance(opt, dict):
        label = opt.get("label") or opt.get("title") or opt.get("value")
        value = opt.get("value") or label
        return str(label), str(value)
    if isinstance(opt, (list, tuple)) and opt:
        label = opt[0]
        value = opt[1] if len(opt) > 1 else opt[0]
        return str(label), str(value)
    s = str(opt)
    return s, s


def _ensure_state() -> None:
    st.session_state.setdefault("gcp", {"answers": {}})
    st.session_state.setdefault("care_profile", {})
    st.session_state.setdefault(STEP_KEY, 0)
    st.session_state.setdefault(ACK_KEY, False)


def _answers() -> Dict[str, Any]:
    return st.session_state["gcp"]["answers"]


def _render_question(q: Dict[str, Any]) -> None:
    qid = q["id"]
    qlabel = q.get("label", qid)
    qhelp = q.get("help")
    qtype = (q.get("type") or "single").lower()
    options_raw: List[Any] = q.get("options", [])
    opts: List[Tuple[str, str]] = [_opt_pair(o) for o in options_raw]

    st.markdown(f"### {qlabel}")
    if qhelp:
        st.caption(qhelp)

    key = f"gcp_ans_{qid}"
    answers = st.session_state["gcp"]["answers"]

    if qtype in ("single", "radio"):
        labels = [o[0] for o in opts]
        values = [o[1] for o in opts]

        if not labels:
            st.warning(f"Missing options for {qid}")
            return

        if answers.get(qid) in values:
            idx_default = values.index(answers[qid])
        elif qid == ELIG_QID and "no" in values:
            idx_default = values.index("no")
        else:
            idx_default = 0

        chosen_label = st.radio(" ", labels, index=idx_default, label_visibility="collapsed", key=key)
        answers[qid] = values[labels.index(chosen_label)]

    elif qtype in ("multi", "multiselect"):
        labels = [o[0] for o in opts]
        values = [o[1] for o in opts]

        if not labels:
            st.warning(f"Missing options for {qid}")
            return

        saved = answers.get(qid)
        if isinstance(saved, dict):
            default_vals = [v for v, on in saved.items() if on]
        elif isinstance(saved, list):
            default_vals = [str(v) for v in saved]
        else:
            default_vals = []

        chosen_labels = st.multiselect(
            qlabel,
            labels,
            default=[labels[values.index(v)] for v in default_vals if v in values]
        )
        selected_values = [values[labels.index(lbl)] for lbl in chosen_labels]
        answers[qid] = {v: (v in selected_values) for v in values}

    else:
        st.text_input("Answer", key=key)
        answers[qid] = st.session_state[key]



def _medicaid_acknowledgement() -> None:
    blurbs = load_blurbs()
    val = str(_answers().get(ELIG_QID) or "").lower()
    if val in {"yes", "unsure"}:
        if banner := blurbs.get("medicaid_banner"):
            st.info(banner)
        if body := blurbs.get("medicaid_ack"):
            st.markdown(f"<div class='banner banner--info'>{body}</div>", unsafe_allow_html=True)
        st.session_state[ACK_KEY] = st.checkbox(
            "I understand",
            value=st.session_state.get(ACK_KEY, False),
            key=ACK_KEY,
        )
    else:
        st.session_state[ACK_KEY] = True if val else False


def _section_requires_ack(section: Dict[str, Any]) -> bool:
    for q in section.get("questions", []):
        if (q.get("id") or q.get("key")) == ELIG_QID:
            val = _answers().get(ELIG_QID)
            if not val:
                return True
            if val in {"yes", "unsure"} and not st.session_state.get(ACK_KEY, False):
                return True
    return False


def _section_required_missing(section: Dict[str, Any]) -> bool:
    answers = _answers()
    for q in section.get("questions", []):
        qid = q.get("id") or q.get("key")
        if not qid:
            continue
        qtype = (q.get("type") or q.get("ui") or "single").lower()
        required = bool(q.get("required")) or (qid == ELIG_QID)
        if not required:
            continue
        val = answers.get(qid)
        if qtype in {"single", "select"} and not val:
            return True
        if qtype in {"multiselect"} and isinstance(val, dict) and not any(val.values()):
            return True
        if qtype in {"multi", "checkboxes"} and isinstance(val, dict) and not any(val.values()):
            return True
        if qtype == "integer" and val is None:
            return True
    return False


def _score(answers: Dict[str, Any]) -> Dict[str, float]:
    scoring = load_scoring()
    totals = defaultdict(float)
    for qid, mapping in scoring.items():
        if qid not in answers:
            continue
        response = answers[qid]
        if isinstance(response, dict):
            for ans, is_on in response.items():
                if is_on:
                    for setting, pts in mapping.get(str(ans), {}).items():
                        totals[setting] += float(pts)
        elif isinstance(response, list):
            for ans in response:
                for setting, pts in mapping.get(str(ans), {}).items():
                    totals[setting] += float(pts)
        else:
            for setting, pts in mapping.get(str(response), {}).items():
                totals[setting] += float(pts)
    return {setting: float(totals.get(setting, 0.0)) for setting in SETTINGS_ORDER}


def _pick(scores: Dict[str, float]) -> str:
    return max(scores, key=scores.get) if scores else SETTINGS_ORDER[0]


def _finish() -> None:
    answers = _answers()
    scores = _score(answers)
    recommendation = _pick(scores)
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
    <div class="cluster mt-space-4">
      <a class="btn btn--secondary" href="?page=hub_concierge">Back to Hub</a>
      <a class="btn btn--primary" href="?page=cost_planner">Continue to Cost Planner</a>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render() -> None:
    _ensure_state()
    schema = load_schema()
    blurbs = load_blurbs()
    sections = schema.get("sections", [])

    step = st.session_state.get(STEP_KEY, 0)
    step = max(0, min(step, max(len(sections) - 1, 0)))
    st.session_state[STEP_KEY] = step

    st.markdown('<h1 class="h1">Guided Care Plan</h1>', unsafe_allow_html=True)
    if intro := blurbs.get("gcp_intro"):
        st.caption(intro)

    if not sections:
        st.info("No sections configured.")
        return

    current_section = sections[step]
    title = current_section.get("title", "")
    blurb = (current_section.get("blurb") or "").replace("{{name}}", subject_name())
    section_header(title, blurb)

    for q in current_section.get("questions", []):
        _render_question(q)
        if (q.get("id") or q.get("key")) == ELIG_QID:
            _medicaid_acknowledgement()

    st.divider()

    cols = st.columns([1, 1, 1, 6])
    with cols[0]:
        if st.button("Back", disabled=step == 0):
            st.session_state[STEP_KEY] = max(0, step - 1)
            st.rerun()

    with cols[1]:
        disable_next = _section_required_missing(current_section) or _section_requires_ack(current_section)
        show_next = step < len(sections) - 1
        if show_next and st.button("Next", disabled=disable_next):
            st.session_state[STEP_KEY] = min(len(sections) - 1, step + 1)
            st.rerun()

    with cols[2]:
        if step == len(sections) - 1:
            disable_complete = _section_required_missing(current_section) or _section_requires_ack(current_section)
            if st.button("Complete", disabled=disable_complete):
                _finish()
