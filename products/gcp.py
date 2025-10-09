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
ACK_KEY = "gcp_medicaid_ack"


def _ensure_state() -> None:
    st.session_state.setdefault("gcp", {"answers": {}})
    st.session_state.setdefault("care_profile", {})
    st.session_state.setdefault(STEP_KEY, 0)
    st.session_state.setdefault(ACK_KEY, False)


def _answers() -> Dict[str, Any]:
    return st.session_state["gcp"]["answers"]


def _opt_pair(opt: Any) -> Tuple[str, str]:
    if isinstance(opt, dict):
        label = opt.get("label") or opt.get("title") or opt.get("value", "")
        value = opt.get("value") or label
        return str(label), str(value)
    if isinstance(opt, (list, tuple)) and opt:
        label = opt[0]
        value = opt[1] if len(opt) > 1 else opt[0]
        return str(label), str(value)
    s = str(opt)
    return s, s


def _render_question(q: Dict[str, Any]) -> None:
    qid = q.get("id") or q.get("key")
    if not qid:
        st.warning("Question missing id/key")
        return

    qtype = (q.get("type") or q.get("ui") or "single").lower()
    label = q.get("label", qid).replace("{{name}}", subject_name())
    help_text = q.get("help")

    st.markdown(f"### {label}")
    if help_text:
        st.caption(help_text)

    answers = _answers()
    current = answers.get(qid)
    opts = [_opt_pair(o) for o in (q.get("options") or q.get("choices") or [])]

    if qtype in {"single", "select", "radio"}:
        if not opts:
            st.warning(f"Missing options for {qid}")
            return

        if qid == ELIG_QID:
            order = {"no": 0, "yes": 1, "unsure": 2}
            opts.sort(key=lambda item: order.get(item[1].lower(), 99))

        labels = [opt[0].replace("{{name}}", subject_name()) for opt in opts]
        values = [opt[1] for opt in opts]

        if current in values:
            idx = values.index(current)
        elif qid == ELIG_QID and "no" in values:
            idx = values.index("no")
            current = "no"
            answers[qid] = current
        else:
            idx = 0
            current = values[idx]
            answers[qid] = current

        chosen_label = st.radio(
            " ",
            labels,
            index=idx,
            label_visibility="collapsed",
            key=f"gcp_radio_{qid}",
        )
        answers[qid] = values[labels.index(chosen_label)]

        if qid == ELIG_QID:
            _medicaid_acknowledgement(answers[qid])

    elif qtype in {"multiselect", "multi", "checkboxes"}:
        if not opts:
            st.warning(f"Missing options for {qid}")
            return
        labels = [opt[0].replace("{{name}}", subject_name()) for opt in opts]
        values = [opt[1] for opt in opts]
        saved = answers.get(qid)
        if isinstance(saved, dict):
            default_vals = [val for val, on in saved.items() if on]
        elif isinstance(saved, list):
            default_vals = [str(v) for v in saved]
        else:
            default_vals = []

        chosen_labels = st.multiselect(
            " ",
            labels,
            default=[labels[values.index(v)] for v in default_vals if v in values],
            label_visibility="collapsed",
            key=f"gcp_multi_{qid}",
        )
        selected = {val: (labels[values.index(val)] in chosen_labels if val in values else False) for val in values}
        answers[qid] = selected

    elif qtype == "integer":
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
            label_visibility="collapsed",
            key=f"gcp_int_{qid}",
        )

    else:
        st.warning(f"Unsupported question type '{qtype}' for {qid}")


def _medicaid_acknowledgement(value: Optional[str]) -> None:
    if value in {"yes", "unsure"}:
        st.markdown(
            """
<div class="banner banner--info">
  Concierge Care Advisors can’t arrange care services for people on Medicaid because those programs are provided directly through state and federal agencies. You can still complete the Guided Care Plan and use the Cost Planner. For program details and support, visit <a class='btn btn--secondary' href='https://www.medicaid.gov/' target='_blank'>Medicaid.gov</a> or learn about long-term services and supports at <a class='btn btn--secondary' href='https://www.medicaid.gov/medicaid/long-term-services-supports' target='_blank'>LTSS</a>.
</div>
""",
            unsafe_allow_html=True,
        )
        col_ack, col_links = st.columns([1, 2])
        with col_ack:
            st.session_state[ACK_KEY] = st.checkbox(
                "I understand",
                value=st.session_state.get(ACK_KEY, False),
                key=ACK_KEY,
            )
        with col_links:
            st.markdown(
                "<div class='kit-row'>"
                "<a class='btn btn--secondary' target='_blank' href='https://www.medicaid.gov/'>Open Medicaid.gov</a>"
                "<a class='btn btn--ghost' target='_blank' href='https://www.medicaid.gov/medicaid/long-term-services-supports'>What is LTSS?</a>"
                "</div>",
                unsafe_allow_html=True,
            )
    else:
        st.session_state[ACK_KEY] = True if value else False


def _section_requires_ack(section: Dict[str, Any]) -> bool:
    val = _answers().get(ELIG_QID)
    if val in {"yes", "unsure"} and not st.session_state.get(ACK_KEY, False):
        return any((q.get("id") or q.get("key")) == ELIG_QID for q in section.get("questions", []))
    if val is None:
        return True
    return False


def _section_required_missing(section: Dict[str, Any]) -> bool:
    answers = _answers()
    for q in section.get("questions", []):
        qid = q.get("id") or q.get("key")
        if not qid:
            continue
        required = bool(q.get("required")) or (qid == ELIG_QID)
        if not required:
            continue
        val = answers.get(qid)
        qtype = (q.get("type") or q.get("ui") or "single").lower()
        if qtype in {"single", "select", "radio"} and not val:
            return True
        if qtype in {"multiselect", "multi", "checkboxes"}:
            if isinstance(val, dict) and not any(val.values()):
                return True
            if isinstance(val, list) and not val:
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
        resp = answers[qid]
        if isinstance(resp, dict):
            for ans, on in resp.items():
                if on:
                    for setting, pts in mapping.get(str(ans), {}).items():
                        totals[setting] += float(pts)
        elif isinstance(resp, list):
            for ans in resp:
                for setting, pts in mapping.get(str(ans), {}).items():
                    totals[setting] += float(pts)
        else:
            for setting, pts in mapping.get(str(resp), {}).items():
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
    sections = schema.get("sections", [])

    step = st.session_state.get(STEP_KEY, 0)
    step = max(0, min(step, max(len(sections) - 1, 0)))
    st.session_state[STEP_KEY] = step

    st.markdown('<h1 class="h1">Guided Care Plan</h1>', unsafe_allow_html=True)

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

    prev_btn, next_btn, complete_btn, _ = st.columns([1, 1, 1, 6])

    with prev_btn:
        if st.button("Back", disabled=step == 0):
            st.session_state[STEP_KEY] = max(0, step - 1)
            st.rerun()

    with next_btn:
        if step < len(sections) - 1:
            disable_next = _section_required_missing(current_section) or _section_requires_ack(current_section)
            if st.button("Next", disabled=disable_next):
                st.session_state[STEP_KEY] = min(len(sections) - 1, step + 1)
                st.rerun()

    with complete_btn:
        if step == len(sections) - 1:
            disable_complete = _section_required_missing(current_section) or _section_requires_ack(current_section)
            if st.button("Complete", disabled=disable_complete):
                _finish()
                st.rerun()
