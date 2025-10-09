import streamlit as st


def _ensure_container(label: str):
    if label:
        st.markdown(f"<p><strong>{label}</strong></p>", unsafe_allow_html=True)


def pill_row(key: str, options: list[str], value: str | None = None):
    st.markdown('<div class="choice-pills">', unsafe_allow_html=True)
    current = st.session_state.get(key, value or "")
    for opt in options:
        selected = " is-selected" if current == opt else ""
        if st.button(opt, key=f"{key}::{opt}"):
            st.session_state[key] = opt
            current = opt
    st.markdown("</div>", unsafe_allow_html=True)
    return st.session_state.get(key, value or "")


def pills(key: str, options: list[str]):
    return pill_row(key, options)


def text(key: str, placeholder: str = ""):
    return st.text_input("", placeholder=placeholder, key=key)


def multiselect(key: str, options: list[str]):
    return st.multiselect("", options, default=st.session_state.get(key, []), key=key)


def render_question(q: dict):
    q_type = q["type"]
    label = q.get("label", "")
    _ensure_container(label)
    if q_type == "pills":
        return pills(q["key"], q["options"])
    if q_type == "text":
        return text(q["key"], q.get("placeholder", ""))
    if q_type == "multiselect":
        return multiselect(q["key"], q["options"])
    if q_type == "slider":
        return st.slider(
            label,
            q["min"],
            q["max"],
            q.get("default", q["min"]),
            key=q["key"],
        )
    st.write(f"Unsupported question type: {q_type}")
    return None


def render_form(schema: list[dict]):
    answers = {}
    for q in schema:
        val = render_question(q)
        answers[q["key"]] = val
        st.markdown('<div class="helper"></div>', unsafe_allow_html=True)
    return answers
