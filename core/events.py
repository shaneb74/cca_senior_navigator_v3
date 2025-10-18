import streamlit as st


def log_event(event: str, data: dict | None = None):
    events = st.session_state.get("_events", [])
    events.append({"event": event, "data": data or {}})
    st.session_state["_events"] = events
