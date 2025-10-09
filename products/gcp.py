import json
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from core.forms import render_question
from core.state import set_module_status

_SCHEMA_PATH = Path("config/gcp_schema.json")


def _load_schema() -> Dict[str, Any]:
    with _SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _get(key: str):
    return st.session_state.get(key)


def _eval_when(rule: Dict[str, Any]) -> bool:
    if not rule:
        return True
    if "eq" in rule:
        k, v = rule["eq"]
        return _get(k) == v
    if "ne" in rule:
        k, v = rule["ne"]
        return _get(k) != v
    if "in" in rule:
        k, arr = rule["in"]
        val = _get(k)
        return val in arr
    if "count_gte" in rule:
        k, n = rule["count_gte"]
        val = _get(k) or []
        return isinstance(val, list) and len(val) >= n
    return False


def _handle_effect(effect: Dict[str, Any]):
    if not _eval_when(effect.get("when", {})):
        return
    action = effect.get("action")
    if action == "exit":
        st.warning(effect.get("message", ""))
        st.markdown('<a class="btn btn--primary" href="?page=hub_concierge">Return to Care Hub</a>', unsafe_allow_html=True)
        st.stop()
    if action == "flag":
        flags = st.session_state.setdefault("_gcp_flags", set())
        flag = effect.get("flag")
        if flag:
            flags.add(flag)
        if effect.get("message"):
            st.info(effect["message"])


def render():
    if "current_section" not in st.session_state:
        st.session_state.current_section = 0
    schema = _load_schema()
    intro = schema.get("intro", {})
    st.header(intro.get("title", "Guided Care Plan"))
    if intro.get("body"):
        st.write(intro["body"])
    if intro.get("cta"):
        st.markdown('<div class="card-actions"><a class="btn btn--primary" href="#gcp-form">{}</a></div>'.format(intro["cta"]), unsafe_allow_html=True)

    st.markdown('<div id="gcp-form"></div>', unsafe_allow_html=True)

    sections = schema.get("sections", [])
    total_sections = len(sections)
    current_section = st.session_state.get("current_section", 0)

    # Progress indicator
    progress = (current_section + 1) / total_sections
    st.progress(progress)
    st.write(f"Section {current_section + 1} of {total_sections}")

    section = sections[current_section]
    title = section.get("title")
    if title:
        st.subheader(title)
    if "summary" in section:
        summary = section["summary"]
        for bullet in summary.get("bullets", []):
            st.write(f"- {bullet}")
        for cta in summary.get("ctas", []):
            st.markdown(f'<a class="btn btn--primary" href="?page=hub_concierge">{cta}</a>', unsafe_allow_html=True)
        return

    for q in section.get("questions", []):
        if "showIf" in q and not _eval_when(q["showIf"]):
            continue
        render_question(q)
        qid = q["key"]
        answer = st.session_state.get(qid)
        if qid == "Q1" and answer in ["Yes", "Unsure"]:
            st.info("We are unable to help with Medicaid-only situations. If you have additional private pay or long-term care insurance, please contact us directly.")
            st.markdown('<p><strong>Medicaid Acknowledgment</strong></p><p>By checking this box, I acknowledge that I understand Concierge Care Advisors cannot assist with Medicaid-only care planning.</p>', unsafe_allow_html=True)
            st.checkbox("I understand and want to continue the assessment.", key="medicaid_ack")
            # if not st.session_state.get("medicaid_ack", False):
            #     st.stop()
        for eff in q.get("effects", []):
            _handle_effect(eff)
        st.markdown('<div class="helper"></div>', unsafe_allow_html=True)    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if current_section > 0 and st.button("Back"):
            st.session_state["current_section"] = current_section - 1
            st.rerun()
    with col2:
        if current_section < total_sections - 1:
            if st.button("Next"):
                st.session_state["current_section"] = current_section + 1
                st.rerun()
        else:
            if st.button("Complete"):
                set_module_status("gcp", "done")
                st.success("Guided Care Plan responses saved.")
                st.rerun()

