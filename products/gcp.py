from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List, Optional

import streamlit as st

from core.data import load_blurbs, load_schema, load_scoring
from core.events import log_event
from core.forms import choice_pills, section_header, subject_name

SETTINGS_ORDER = [
    "In-Home Care",
    "Assisted Living",
    "Memory Care",
    "Memory Care High Acuity",
]

ELIG_QID = "elig_medicaid"
STEP_KEY = "gcp_step"
ACK_KEY = "gcp_ack_ok"


def _ensure_state() -> None:
    st.session_state.setdefault("gcp", {"answers": {}})
    st.session_state.setdefault("care_profile", {})
    st.session_state.setdefault(STEP_KEY, 0)
    st.session_state.setdefault(ACK_KEY, False)


def _answers() -> Dict[str, Any]:
    return st.session_state["gcp"]["answers"]


def _render_question(q: Dict[str, Any]) -> None:
    qid = q.get("id") or q.get("key")
    if not qid:
        st.warning("Question missing id/key")
        return

    q_type = (q.get("type") or q.get("ui") or "single").lower()
    label = q.get("label", qid).replace("{{name}}", subject_name())
    help_text = q.get("help")

    st.markdown(f"<div class='h3'>{label}</div>", unsafe_allow_html=True)
    if help_text:
        st.caption(help_text)

    answers = _answers()
    current = answers.get(qid)
    options = q.get("options") or q.get("choices") or []

    if q_type in {"single", "select"}:
        opts = [(opt["label"].replace("{{name}}", subject_name()), str(opt["value"])) for opt in options]
        allow_none = (qid == ELIG_QID) or not bool(q.get("required"))
        val = choice_pills(f"gcp_{qid}", opts, value=current, allow_none=allow_none)
        answers[qid] = val

    elif q_type in {"multiselect"}:
        opts = [(opt["label"].replace("{{name}}", subject_name()), str(opt["value"])) for opt in options]
        current_vals = current if isinstance(current, list) else []
        labels = [lbl for lbl, _ in opts]
        values = [val for _, val in opts]
        defaults = [labels[values.index(v)] for v in current_vals if v in values]
        chosen = st.multiselect(
            " ",
            labels,
            default=defaults,
            label_visibility="collapsed",
            key=f"gcp_{qid}__multiselect",
        )
        answers[qid] = [values[labels.index(lbl)] for lbl in chosen]

    elif q_type in {"multi", "checkboxes"}:
        current_map = current if isinstance(current, dict) else {}
        out: Dict[str, bool] = {}
        for opt in options:
            opt_label = opt["label"].replace("{{name}}", subject_name())
            opt_value = str(opt["value"])
            out[opt_value] = st.checkbox(
                opt_label,
                value=bool(current_map.get(opt_value)),
                key=f"gcp_{qid}__{opt_value}",
            )
        answers[qid] = out

    elif q_type == "integer":
        min_v = int(q.get("min", 0))
        max_v = int(q.get("max", 100))
        step = int(q.get("step", 1))
        default = int(current if isinstance(current, int) else q.get("default", min_v))
        answers[qid] = st.number_input(
            " ",
            min_value=min_v,
            max_value=max_v,
            value=default,
            step=step,
            key=f"gcp_{qid}__int",
            label_visibility="collapsed",
        )

    else:
        st.warning(f"Unsupported question type '{q_type}' for {qid}")
        return

    if qid == ELIG_QID:
        _medicaid_acknowledgement()


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
            if val in {"yes", "unsure"} and not st.session_state.get(ACK_KEY, False):
                return True
    return False


def _section_required_missing(section: Dict[str, Any]) -> bool:
    answers = _answers()
    for q in section.get("questions", []):
        qid = q.get("id") or q.get("key")
        required = bool(q.get("required"))
        if not qid or not required:
            continue
        val = answers.get(qid)
        qtype = (q.get("type") or q.get("ui") or "single").lower()
        if qtype in {"single", "select"} and not val:
            return True
        if qtype in {"multiselect"} and isinstance(val, list) and not val:
            return True
        if qtype in {"multi", "checkboxes"} and isinstance(val, dict) and not any(val.values()):
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

    st.divider()

    cols = st.columns([1, 1, 1, 6])
    with cols[0]:
        if st.button("Back", disabled=step == 0):
            st.session_state[STEP_KEY] = max(0, step - 1)
            st.experimental_rerun()

    with cols[1]:
        disable_next = _section_required_missing(current_section) or _section_requires_ack(current_section)
        show_next = step < len(sections) - 1
        if show_next and st.button("Next", disabled=disable_next):
            st.session_state[STEP_KEY] = min(len(sections) - 1, step + 1)
            st.experimental_rerun()

    with cols[2]:
        if step == len(sections) - 1:
            disable_complete = _section_required_missing(current_section) or _section_requires_ack(current_section)
            if st.button("Complete", disabled=disable_complete):
                _finish()
*** End Patch
