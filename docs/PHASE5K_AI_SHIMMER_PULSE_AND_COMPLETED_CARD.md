Excellent question — those two markdowns are sequential phases of the *same feature evolution*, not conflicting instructions.

Here’s how to think of them:

| Phase  | Feature                             | Status             | Notes                                                                  |
| ------ | ----------------------------------- | ------------------ | ---------------------------------------------------------------------- |
| **5J** | Gradient + Animated Gradient Border | ✅ Baseline version | Adds the static + gradient border animation and completed-card styling |
| **5K** | Shimmer Pulse Extension             | 🔄 Enhancement     | Builds directly on 5J, adding the subtle shimmer-pulse overlay         |

So the second one **replaces and extends** the first.
To avoid confusion, here’s the **merged single markdown** you can give Claude, containing everything from both 5J and 5K in one authoritative spec.

---

## 📘 `PHASE5K_AI_SHIMMER_PULSE_AND_COMPLETED_CARD.md`

### 🎯 Objectives

1. Apply a **purple→pink gradient** border to AI-related tiles (e.g. NAVI).
2. Add a **soft shimmer-pulse effect** for subtle movement and “intelligence.”
3. Maintain and polish the **Completed Journey Card** style.
4. Keep all motion smooth, lightweight, and compliant with `prefers-reduced-motion`.

---

### 🎨 CSS Additions (`assets/css/overrides.css`)

```css
/* ==========================================
   PHASE 5K — AI SHIMMER PULSE + COMPLETED CARD
   ========================================== */

/* --- AI / NAVI Card Base --- */
.ai-card, .navi-card {
    border-left: 5px solid transparent;
    border-image: linear-gradient(180deg, #9b5de5, #f15bb5);
    border-image-slice: 1;
    border-radius: 10px;
    background: #fff;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.3s ease;
}

/* --- Animated Gradient Flow --- */
.ai-card.animate-border, .navi-card.animate-border {
    border-image: linear-gradient(180deg, #9b5de5, #f15bb5, #9b5de5);
    animation: borderGradient 8s ease-in-out infinite;
    border-image-slice: 1;
}
@keyframes borderGradient {
    0%   { border-image-source: linear-gradient(180deg, #9b5de5, #f15bb5); }
    50%  { border-image-source: linear-gradient(180deg, #f15bb5, #9b5de5); }
    100% { border-image-source: linear-gradient(180deg, #9b5de5, #f15bb5); }
}

/* --- Shimmer Pulse Overlay --- */
.ai-card::before, .navi-card::before {
    content: "";
    position: absolute;
    top: 0; left: -150%;
    width: 250%;
    height: 100%;
    background: linear-gradient(
        120deg,
        rgba(155,93,229,0) 30%,
        rgba(241,91,181,0.15) 50%,
        rgba(155,93,229,0) 70%
    );
    animation: shimmerPulse 6s infinite ease-in-out;
    pointer-events: none;
}
@keyframes shimmerPulse {
    0%   { transform: translateX(0); opacity: 0.3; }
    50%  { transform: translateX(30%); opacity: 0.5; }
    100% { transform: translateX(0); opacity: 0.3; }
}

/* --- Hover Depth + Optional Glow --- */
.ai-card:hover, .navi-card:hover {
    box-shadow: 0 4px 14px rgba(241,91,181,0.18);
    transform: translateY(-1px);
    transition: all 0.25s ease-in-out;
}

/* --- Motion Accessibility --- */
@media (prefers-reduced-motion: reduce) {
    .ai-card.animate-border,
    .navi-card.animate-border,
    .ai-card::before,
    .navi-card::before {
        animation: none !important;
    }
}

/* --- Completed Journey Card --- */
.completed-card {
    background: linear-gradient(180deg, #f8faff 0%, #ffffff 100%);
    border-left: 5px solid #2ecc71;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    padding: 1.25rem 1.5rem;
    position: relative;
    transition: 0.2s ease-in-out;
}
.completed-card:hover {
    background: linear-gradient(180deg, #f2fcf7 0%, #ffffff 100%);
    border-left: 5px solid #27ae60;
    transform: translateY(-1px);
}
.completed-card::after {
    content: "✓";
    font-weight: bold;
    font-size: 1.2rem;
    color: #27ae60;
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: #e8f9f0;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
}
```

---

### 🧩 Example Usage in Streamlit

```python
# NAVI / AI card
st.markdown("""
<div class="navi-card ai-card animate-border">
    <h4>✨ NAVI</h4>
    <p>Answer these questions to match the right level of support.</p>
</div>
""", unsafe_allow_html=True)

# Completed Journey card
st.markdown("""
<div class="completed-card">
    <h4>Guided Care Plan</h4>
    <p>Your personalized care plan recommendation.</p>
</div>
""", unsafe_allow_html=True)
```

---

### 🧭 Claude Task Directive

> **Claude**, on branch `feature/phase5k_ai_shimmer_pulse`:
>
> * Append the above CSS to `assets/css/overrides.css`.
> * Apply `.animate-border` to all AI-driven or NAVI cards.
> * Keep the shimmer pulse and hover glow subtle.
> * Retain completed card styling from previous phase.
> * Verify animation fluidity and accessibility (`prefers-reduced-motion`).

---

