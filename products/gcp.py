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

PILL_CSS = """
<style>
div[data-testid="stRadio"] label {display:none;}
div[data-testid="stRadio"] div[role="radiogroup"] {
  display:flex;
  gap:var(--space-3);
  flex-wrap:wrap;
}
div[data-testid="stRadio"] div[role="radio"] {
  border:1px solid var(--ink-300);
  border-radius:999px;
  padding:8px 14px;
  background:var(--muted);
  color:var(--ink-600);
  cursor:pointer;
}
div[data-testid="stRadio"] div[role="radio"][aria-checked="true"] {
  background:var(--ink);
  color:#fff;
  border-color:var(--ink);
}
</style>
"""


def _ensure_state() -> None:
    st.session_state.setdefault("gcp", {"answers": {}})
    st.session_state.setdefault("flags", {})
    st.session_state.setdefault("care_profile", {})


def _answers() -> Dict[str, Any]:
    return st.session_state["gcp"]["answers"]


def _normalise_options(options: List[Any]) -> List[Dict[str, str]]:
    normalised: List[Dict[str, str]] = []
    for opt in options:
        if isinstance(opt, dict):
            label = opt.get("label") or opt.get("title") or opt.get("value")
            value = opt.get("value") or label
        else:
            label = str(opt)
            value = label
        normalised.append({"label": str(label), "value": str(value)})
    return normalised


def _eval_condition(rule: Dict[str, Any]) -> bool:
    answers = _answers()
    if not rule:
        return True
    if "eq" in rule:
        key, expected = rule["eq"]
        return answers.get(key) == expected
    if "ne" in rule:
        key, expected = rule["ne"]
        return answers.get(key) != expected
    if "in" in rule:
        key, values = rule["in"]
        ans = answers.get(key)
        if isinstance(ans, list):
            return any(str(a) in [str(v) for v in values] for a in ans)
        return ans in values
    if "count_gte" in rule:
        key, minimum = rule["count_gte"]
        selected = answers.get(key) or []
        if isinstance(selected, list):
            return len(selected) >= minimum
        if isinstance(selected, dict):
            return sum(1 for picked in selected.values() if picked) >= minimum
        return False
    return True


def _depends_on_met(condition: Dict[str, Any]) -> bool:
    if not condition:
        return True
    target = condition.get("id")
    allowed = condition.get("any_of")
    if not target:
        return True
    value = _answers().get(target)
    if allowed is None:
        return value is not None
    if isinstance(value, list):
        return any(v in value for v in allowed)
    return value in allowed


def _should_render(question: Dict[str, Any]) -> bool:
    if not _depends_on_met(question.get("depends_on")):
        _answers().pop(question.get("id") or question.get("key"), None)
        return False
    when = question.get("when")
    if when and not _eval_condition(when):
        _answers().pop(question.get("id") or question.get("key"), None)
        return False
    return True


def _render_single(qid: str, question: Dict[str, Any], options: List[Dict[str, str]]):
    values = [opt["value"] for opt in options]
    labels = [opt["label"] for opt in options]
    current = _answers().get(qid)
    if current not in values:
        current = values[0]
    index = values.index(current)
    style = question.get("style", "pill")
    if style == "pill":
        selected_label = st.radio(
            " ",
            labels,
            index=index,
            horizontal=True,
            key=f"pill_{qid}",
            label_visibility="collapsed",
        )
        value = values[labels.index(selected_label)]
    else:
        selected_label = st.selectbox(
            " ",
            labels,
            index=index,
            key=f"select_{qid}",
            label_visibility="collapsed",
        )
        value = values[labels.index(selected_label)]
    _answers()[qid] = value


def _render_multiselect(qid: str, options: List[Dict[str, str]]):
    labels = [opt["label"] for opt in options]
    label_to_value = {opt["label"]: opt["value"] for opt in options}
    stored = _answers().get(qid, [])
    if isinstance(stored, dict):
        stored = [val for val, picked in stored.items() if picked]
    default_labels = [lbl for lbl, val in label_to_value.items() if val in stored]
    selected_labels = st.multiselect(
        " ",
        labels,
        default=default_labels,
        label_visibility="collapsed",
        key=f"multi_{qid}",
    )
    _answers()[qid] = [label_to_value[lbl] for lbl in selected_labels]


def _render_ack(qid: str, question: Dict[str, Any]):
    depends = question.get("depends_on")
    if not _depends_on_met(depends):
        _answers().pop(qid, None)
        return
    text = question.get("text", "")
    link = question.get("link")
    link_html = (
        f"  <a class='btn btn--secondary' href='{link['href']}' target='_blank'>{link['label']}</a>"
        if link
        else ""
    )
    st.info(f"{text}{'' if not link_html else '<br>' + link_html}")
    checkbox_key = f"ack_{qid}"
    if checkbox_key not in st.session_state:
        st.session_state[checkbox_key] = bool(_answers().get(qid, False))
    checked = st.checkbox("I understand", key=checkbox_key)
    _answers()[qid] = bool(checked)


def _handle_medicaid_ack(blurbs: Dict[str, str]) -> None:
    answers = _answers()
    current = answers.get("medicaid_status")
    if current not in {"yes", "unsure"}:
        st.session_state.pop("medicaid_acknowledged", None)
        return

    title = blurbs.get("gcp_medicaid_title", "We may not be able to assist with Medicaid")
    body = blurbs.get(
        "gcp_medicaid_body",
        "If the person is currently on Medicaid or you’re not sure, our Care Advisors aren’t able to provide services under that program. "
        "Medicaid is a government benefit that offers its own care options for long-term services and supports. You can still complete the Guided Care Plan and use the Cost Planner to learn more about what care might look like and how much it may cost.",
    )
    cta = blurbs.get(
        "gcp_medicaid_cta",
        "Visit Medicaid.gov to learn more about Long-Term Services & Supports",
    )

    st.warning(f"**{title}**  \n{body}")
    st.markdown(
        "<a class='btn btn--secondary' href='https://www.medicaid.gov/medicaid/long-term-services-supports' target='_blank'>"
        f"{cta}</a>",
        unsafe_allow_html=True,
    )

    acknowledged = st.checkbox(
        "I understand and wish to continue", key="medicaid_acknowledged"
    )
    if not acknowledged:
        st.stop()

def _render_question(question: Dict[str, Any], blurbs: Dict[str, str]):
    qid = question.get("id") or question.get("key")
    if not qid:
        raise KeyError("Question missing 'id' or 'key'")
    if not _should_render(question):
        return

    qlabel = question.get("label", str(qid))
    qhelp = question.get("help")
    qtype = question.get("type", "single").lower()
    options = _normalise_options(question.get("options", []))

    st.markdown(f"**{qlabel}**")
    if qhelp:
        st.caption(qhelp)

    if qtype in {"single", "pill", "pills"}:
        _render_single(qid, question, options)
    elif qtype in {"multiselect", "multi"}:
        _render_multiselect(qid, options)
    elif qtype == "ack":
        _render_ack(qid, question)
    else:
        default = _answers().get(qid, "")
        value = st.text_input("Answer", value=str(default), key=f"text_{qid}")
        _answers()[qid] = value

    if qid == "medicaid_status":
        _handle_medicaid_ack(blurbs)


def _score(answers: Dict[str, Any]) -> Dict[str, float]:
    df = load_scoring()
    totals = defaultdict(float)
    for _, row in df.iterrows():
        qid = row["question_id"]
        aval = str(row["answer_value"])
        setting = row["setting"]
        pts = float(row["points"])
        ans = answers.get(qid)
        if isinstance(ans, list):
            if aval in [str(v) for v in ans]:
                totals[setting] += pts
        elif isinstance(ans, dict):
            if ans.get(aval, False):
                totals[setting] += pts
        else:
            if str(ans) == aval:
                totals[setting] += pts
    return {setting: totals.get(setting, 0.0) for setting in SETTINGS_ORDER}


def _pick_recommendation(scores: Dict[str, float]) -> str:
    return max(scores.items(), key=lambda kv: kv[1])[0] if scores else SETTINGS_ORDER[0]


def render():
    _ensure_state()
    st.markdown(PILL_CSS, unsafe_allow_html=True)

    st.header("Guided Care Plan")

    schema = load_schema()
    blurbs = load_blurbs()

    intro = blurbs.get("gcp_intro")
    if intro:
        st.markdown(f'<div class="banner banner--info">{intro}</div>', unsafe_allow_html=True)

    for section in schema.get("sections", []):
        st.subheader(section.get("title", ""))
        for question in section.get("questions", []):
            _render_question(question, blurbs)
        st.divider()

    answers = _answers()
    medicaid_val = answers.get("medicaid_status")
    ack_ok = bool(st.session_state.get("medicaid_acknowledged"))
    medicaid_flag = medicaid_val in ("yes", "unsure")
    st.session_state["flags"]["medicaid"] = medicaid_flag

    if medicaid_flag:
        st.markdown(
            """<div class=\"banner banner--warning\">
            We can’t schedule advisor appointments for Medicaid cases. You can still finish your plan and estimate costs.
            </div>""",
            unsafe_allow_html=True,
        )

    disabled_complete = medicaid_flag and not ack_ok

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save progress"):
            st.success("Progress saved.")

    with col2:
        if st.button("Complete", disabled=disabled_complete):
            scores = _score(answers)
            recommendation = _pick_recommendation(scores)
            st.session_state.update(
                {
                    "gcp_completed": True,
                    "gcp_recommendation": recommendation,
                    "care_profile": {
                        "care_setting": recommendation,
                        "scores": scores,
                        "answers": answers.copy(),
                    },
                }
            )
            log_event("gcp.completed", {"recommendation": recommendation})
            st.success(f"Recommendation: **{recommendation}**")
            if answers.get("medicaid_status") in ("yes", "unsure"):
                st.info(
                    "Because Medicaid provides its own long-term care programs, our Care Advisors can’t schedule services directly. "
                    "You can still explore care options and costs below. "
                    "[Learn more about Medicaid Long-Term Services & Supports →](https://www.medicaid.gov/medicaid/long-term-services-supports)"
                )
            st.markdown(
                """
                <div class="card-actions">
                  <a class="btn btn--secondary" href="?page=hub_concierge">Back to Hub</a>
                  <a class="btn btn--primary" href="?page=cost_planner">Continue to Cost Planner</a>
                </div>
                """,
                unsafe_allow_html=True,
            )
