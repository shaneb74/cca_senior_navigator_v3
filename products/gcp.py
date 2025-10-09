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


def _ensure_state():
    st.session_state.setdefault("gcp", {"answers": {}, "scores": {}, "summary": None})
    st.session_state.setdefault("care_profile", {})


def _render_question(q: Dict[str, Any]):
    qid = q["id"]
    qlabel = q.get("label", qid)
    qhelp = q.get("help")
    qtype = q.get("type", "single")
    opts: List[Dict[str, Any]] = q.get("options", [])

    st.markdown(f"### {qlabel}")
    if qhelp:
        st.caption(qhelp)

    key = f"gcp_ans_{qid}"
    ans_store = st.session_state["gcp"]["answers"]

    if qtype == "single":
        labels = [o["label"] for o in opts]
        values = [o["value"] for o in opts]
        default_idx = 0
        if qid in ans_store and ans_store[qid] in values:
            default_idx = values.index(ans_store[qid])
        choice_label = st.radio(
            " ",
            labels,
            index=default_idx,
            label_visibility="collapsed",
            key=key,
        )
        ans_store[qid] = values[labels.index(choice_label)]
    elif qtype == "multi":
        current = ans_store.get(qid, {})
        picks = {}
        for option in opts:
            opt_val = option["value"]
            opt_key = f"{key}_{opt_val}"
            picks[opt_val] = st.checkbox(
                option["label"],
                key=opt_key,
                value=current.get(opt_val, False),
            )
        ans_store[qid] = picks
    else:
        text_val = st.text_input("Answer", value=ans_store.get(qid, ""), key=key)
        ans_store[qid] = text_val


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

        answer_val = answers[qid]
        if isinstance(answer_val, dict):
            if answer_val.get(aval, False):
                totals[setting] += pts
        else:
            if str(answer_val) == aval:
                totals[setting] += pts

    return {setting: totals.get(setting, 0.0) for setting in SETTINGS_ORDER}


def _pick_recommendation(scores: Dict[str, float]) -> str:
    return max(scores.items(), key=lambda kv: kv[1])[0] if scores else "In-Home Care"


def render():
    _ensure_state()
    if st.query_params.get("reset") == "1":
        st.session_state.pop("gcp", None)
        st.session_state.pop("gcp_completed", None)
        st.session_state.pop("gcp_recommendation", None)
        st.session_state.pop("care_profile", None)
        _ensure_state()
    st.header("Guided Care Plan")

    schema = load_schema()
    blurbs = load_blurbs()

    intro = blurbs.get("gcp_intro")
    if intro:
        st.info(intro)

    for section in schema.get("sections", []):
        if section.get("title"):
            st.subheader(section["title"])
        for question in section.get("questions", []):
            _render_question(question)
        st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save progress"):
            st.success("Progress saved.")

    with col2:
        if st.button("Complete"):
            answers = st.session_state["gcp"]["answers"]
            scores = _score(answers)
            rec = _pick_recommendation(scores)

            st.session_state["gcp"]["scores"] = scores
            st.session_state["gcp_completed"] = True
            st.session_state["gcp_recommendation"] = rec
            st.session_state["care_profile"] = {
                "care_setting": rec,
                "scores": scores,
                "answers": answers,
            }

            log_event("gcp.completed", {"recommendation": rec})
            st.success(f"Recommendation: **{rec}**")
            st.markdown(
                '<div class="kit-row">'
                '<a class="btn btn--secondary" href="?page=hub_concierge">Back to Hub</a>'
                '<a class="btn btn--primary" href="?page=cost_planner">Continue to Cost Planner</a>'
                '</div>',
                unsafe_allow_html=True,
            )
