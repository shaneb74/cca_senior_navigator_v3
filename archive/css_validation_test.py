import streamlit as st

st.set_page_config(page_title="CSS Validation Test", layout="wide")

# Load global CSS
st.markdown('<link rel="stylesheet" href="assets/css/overrides.css">', unsafe_allow_html=True)

st.title("🧪 CSS Validation Test Suite")

st.subheader("AI / NAVI Card")
st.markdown("""
<div class="navi-card ai-card animate-border">
  <h4>✨ NAVI</h4>
  <p>Guided AI assistance for Discovery.</p>
  <div class="progress-wrapper">
      <div class="progress-label">Discovery Progress: 45% Complete</div>
      <div class="progress-bar">
          <div class="progress-bar-fill shimmer" style="width:45%;"></div>
      </div>
  </div>
  <div class="cta-row">
      <button class="cta-primary">Continue</button>
      <button class="cta-secondary">Ask NAVI</button>
  </div>
</div>
""", unsafe_allow_html=True)

st.subheader("Completed Journey Card")
st.markdown("""
<div class="completed-card">
  <h4>Guided Care Plan</h4>
  <p>Your personalized recommendation is ready.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Module Pills")
st.markdown("""
<div>
  <span class="pill-dark">Memory Care</span>
  <span class="pill-gray">Assisted Living</span>
  <span class="pill-dark">Independent</span>
</div>
""", unsafe_allow_html=True)

st.subheader("Dashboard Tile Example")
st.markdown("""
<div class="ai-card animate-border" style="max-width:300px;">
  <h4>Dashboard Metric</h4>
  <p>Move-ins this month: <strong>27</strong></p>
</div>
""", unsafe_allow_html=True)

st.caption("Confirm gradient shimmer, layout consistency, and lack of CSS regressions.")
