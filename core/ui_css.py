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
  display:flex;
  flex-wrap:wrap;
  gap:10px;
}

[data-testid="stRadio"] div[role="radio"]{
  border:1px solid var(--pill-border) !important;
  background:var(--pill-bg) !important;
  color:var(--pill-fg) !important;
  padding:8px 14px;
  border-radius:10px;
  box-shadow:var(--pill-shadow);
  cursor:pointer;
  user-select:none;
  transition:background .12s ease, color .12s ease, border-color .12s ease, transform .04s ease;
}

[data-testid="stRadio"] div[role="radio"]:hover{
  border-color:#d1d5db !important;
}

[data-testid="stRadio"] div[role="radio"][aria-checked="true"]{
  background:var(--pill-bg-active) !important;
  color:var(--pill-fg-active) !important;
  border-color:var(--pill-bg-active) !important;
}

[data-testid="stRadio"] div[role="radio"]:focus{
  outline:2px solid #11182733;
  outline-offset:2px;
  border-color:#111827 !important;
}
"""

def inject_pill_css():
    """
    Ensures the pill CSS always remains the last style in <head>,
    surviving Streamlit/Emotion re-injections after widget interactions.
    
    This works by:
    1. Injecting a <style> tag with a unique ID
    2. Using MutationObserver to watch for <head> changes
    3. Re-appending our style to the end whenever Emotion injects new styles
    
    Call this once at the top of each page render that uses radio pills.
    It's idempotent and lightweight.
    """
    html(
        f"""
        <script>
        (function() {{
          const STYLE_ID = "cca-pill-css";
          const CSS_TEXT = `{PILL_CSS}`;
          function ensureLast() {{
            let el = document.getElementById(STYLE_ID);
            if (!el) {{
              el = document.createElement("style");
              el.id = STYLE_ID;
              el.appendChild(document.createTextNode(CSS_TEXT));
              document.head.appendChild(el);
              return;
            }}
            // If our style isn't the last one, move it to the end
            if (el.parentNode !== document.head || document.head.lastChild !== el) {{
              el.remove();
              document.head.appendChild(el);
            }}
          }}
          // Ensure now…
          ensureLast();
          // …and keep ensuring any time Streamlit/Emotion mutates <head>
          const mo = new MutationObserver(ensureLast);
          mo.observe(document.head, {{ childList: true }});
        }})();
        </script>
        """,
        height=0,
    )
