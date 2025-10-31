"""CSS injection helpers that survive Streamlit's Emotion re-injection.

This module provides deterministic CSS injection that ensures our styles
always remain last in the cascade, even after Streamlit's Emotion engine
re-injects styles on widget interactions.
"""

from streamlit.components.v1 import html

PILL_CSS = r"""
:root{
  --pill-bg:#f3f4f6;
  --pill-fg:#111827;
  --pill-bg-active:#111827;
  --pill-fg-active:#ffffff;
  --pill-border:#e5e7eb;
  --pill-shadow:0 1px 2px rgba(0,0,0,.04);
}

[data-testid="stRadio"] > div[role="radiogroup"]{
  display:flex !important;
  flex-wrap:wrap !important;
  gap:10px !important;
}

[data-testid="stRadio"] > div[role="radiogroup"] > div{
  border:1px solid var(--pill-border) !important;
  background:var(--pill-bg) !important;
  color:var(--pill-fg) !important;
  padding:8px 14px !important;
  border-radius:10px !important;
  box-shadow:var(--pill-shadow) !important;
  cursor:pointer !important;
  user-select:none !important;
  transition:background .12s ease, color .12s ease, border-color .12s ease !important;
}

[data-testid="stRadio"] > div[role="radiogroup"] > div:hover{
  border-color:#d1d5db !important;
}

[data-testid="stRadio"] > div[role="radiogroup"] > div:has(input:checked){
  background:var(--pill-bg-active) !important;
  color:var(--pill-fg-active) !important;
  border-color:var(--pill-bg-active) !important;
}

[data-testid="stRadio"] input[type="radio"]{
  display:none !important;
}

[data-testid="stRadio"] label > div:first-child{
  display:none !important;
}
"""

def inject_pill_css():
    """
    Ensures pill CSS always re-applies *after* Streamlit Emotion reinjects its styles.
    Uses a targeted observer that tracks Emotion's mount events specifically.
    
    This works by:
    1. Watching for Emotion's style[data-emotion] tag in <head>
    2. Re-appending our style after any Emotion mutation
    3. Running a heartbeat check every 1s to ensure recovery from full teardowns
    
    Call this once at the top of each page render that uses radio pills.
    It's idempotent and lightweight.
    """
    html(f"""
    <script>
    (function() {{
        const STYLE_ID = "cca-pill-css";
        const CSS_TEXT = `{PILL_CSS}`;
        let emotionObserver = null;

        function applyStyles() {{
            let el = document.getElementById(STYLE_ID);
            if (!el) {{
                el = document.createElement("style");
                el.id = STYLE_ID;
                el.textContent = CSS_TEXT;
                document.head.appendChild(el);
            }} else {{
                // re-append so it always stays last
                el.remove();
                document.head.appendChild(el);
            }}
        }}

        function watchEmotion() {{
            // watch for Emotion cache re-injection
            const emotionHead = document.querySelector('style[data-emotion]');
            if (!emotionHead) return;
            if (emotionObserver) emotionObserver.disconnect();

            emotionObserver = new MutationObserver(() => {{
                applyStyles();
            }});
            emotionObserver.observe(document.head, {{ childList: true }});
        }}

        // run now and reapply every second in case of delayed emotion injection
        applyStyles();
        watchEmotion();
        setInterval(() => {{
            if (!document.getElementById(STYLE_ID)) applyStyles();
        }}, 1000);
    }})();
    </script>
    """, height=0)

