"""FAQ Metrics Admin View (Stage 4)

Displays analytics for LLM-powered FAQ interactions:
- Total events, helpful rate
- Top queries
- Gaps (no sources) for content expansion

Uses data/events.log populated by core/events.log_event()
"""

import json
import os
from collections import Counter

import streamlit as st

LOG_PATH = os.getenv("APP_EVENT_LOG", "data/events.log")


def render():
    """Main metrics view."""
    st.title("FAQ Metrics")
    st.caption("Analytics for LLM-powered FAQ interactions")

    if not os.path.exists(LOG_PATH):
        st.info(f"No events yet. Log path: `{LOG_PATH}`")
        st.caption("Start using the FAQ search to populate this view.")
        return

    # Load events
    rows = []
    with open(LOG_PATH) as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

    if not rows:
        st.info("No events found in log file.")
        return

    # Filters
    st.markdown("### Filters")
    kind = st.selectbox("Event kind", options=["faq_llm", "all"], index=0)
    q = st.text_input("Filter by substring in query", placeholder="e.g., assisted living")

    def match(rec):
        if kind != "all" and rec.get("event") != kind:
            return False
        if q and q.lower() not in (rec.get("data", {}).get("query", "").lower()):
            return False
        return True

    filtered = [r for r in rows if match(r)]

    # Metrics
    st.markdown("### Overview")
    col1, col2, col3 = st.columns(3)

    total_faq = len([r for r in rows if r.get("event") == "faq_llm"])
    col1.metric("Total FAQ events", total_faq)

    with_feedback = sum(
        r.get("data", {}).get("feedback") is not None
        for r in filtered
    )
    col2.metric("With feedback", with_feedback)

    if with_feedback > 0:
        helpful_count = sum(
            bool(r.get("data", {}).get("feedback"))
            for r in filtered
        )
        helpful_rate = (helpful_count / with_feedback) * 100
        col3.metric("Helpful rate", f"{helpful_rate:.0f}%")
    else:
        col3.metric("Helpful rate", "N/A")

    # Top queries
    st.markdown("### Top Queries")
    queries = [
        r.get("data", {}).get("query", "").strip()
        for r in filtered
        if r.get("data", {}).get("query")
    ]
    top_q = Counter(queries).most_common(10)

    if top_q:
        for qtext, cnt in top_q:
            st.write(f"- **{qtext}**  —  {cnt} time{'s' if cnt > 1 else ''}")
    else:
        st.caption("No queries yet.")

    # Gaps (no sources)
    st.markdown("### Gaps (No Sources)")
    st.caption("Queries that returned no relevant FAQs — candidates for new content.")

    no_src = [
        r
        for r in filtered
        if not r.get("data", {}).get("used_sources")
    ]

    if no_src:
        for r in no_src[:20]:
            query = r.get("data", {}).get("query", "")
            st.write(f"- {query}")
    else:
        st.success("✅ All queries had at least one source match!")

    # Raw data (collapsible)
    with st.expander("🔍 Raw Event Data", expanded=False):
        st.json(filtered[-50:])  # Last 50 events


if __name__ == "__main__":
    render()
