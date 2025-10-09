from typing import Optional
import base64, mimetypes, pathlib, sys, functools

import streamlit as st

# Resolve repository root (…/cca_senior_navigator_v3)
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


@functools.lru_cache(maxsize=128)
def img_src(rel_path: str) -> str:
    """
    Return a base64 data URI for an image at repo-relative rel_path.
    Example: img_src("static/images/hero.png")
    """
    safe_rel = rel_path.lstrip("/").replace("\\", "/")
    p = (_REPO_ROOT / safe_rel).resolve()
    if not p.exists():
        print(f"[WARN] Missing static image: {safe_rel} (resolved: {p})", file=sys.stderr)
        return ""
    mime, _ = mimetypes.guess_type(p.name)
    try:
        data = p.read_bytes()
    except Exception as e:
        print(f"[ERROR] Failed to read image {p}: {e}", file=sys.stderr)
        return ""
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime or 'image/png'};base64,{b64}"


def header(app_title: str, current_key: str, pages: dict):
    links = []
    for key, meta in pages.items():
        active = " is-active" if key == current_key else ""
        links.append(f'<a class="nav-link{active}" href="?page={key}">{meta["label"]}</a>')
    html = f"""
    <header class="header">
      <div class="container header__inner">
        <div class="brand">{app_title}</div>
        <nav class="nav cluster">{''.join(links)}</nav>
      </div>
    </header>
    """
    st.markdown(html, unsafe_allow_html=True)


def footer():
    html = """
    <footer class="footer">
      <div class="container footer__inner">
        <div class="muted">© Senior Navigator</div>
        <div class="cluster">
          <a class="nav-link" href="?page=terms">Terms</a>
          <a class="nav-link" href="?page=privacy">Privacy</a>
          <a class="nav-link" href="?page=about">About</a>
        </div>
      </div>
    </footer>
    """
    st.markdown(html, unsafe_allow_html=True)


def page_container_open():
    st.markdown('<main class="container stack">', unsafe_allow_html=True)


def page_container_close():
    st.markdown("</main>", unsafe_allow_html=True)


def hub_section(title: str, right_meta: Optional[str] = None):
    right = f'<div class="tile-meta">{right_meta}</div>' if right_meta else ""
    st.markdown(
        f"""<section class="container section">
<div class="tile-head">
  <h2 class="section-title">{title}</h2>
  {right}
</div>
</section>""",
        unsafe_allow_html=True,
    )


def tiles_open():
    st.markdown('<div class="container"><div class="tiles">', unsafe_allow_html=True)


def tiles_close():
    st.markdown("</div></div>", unsafe_allow_html=True)


def tile_open(size: str = "md"):
    size_class = "tile--md" if size == "md" else "tile--lg"
    st.markdown(f'<article class="tile {size_class}">', unsafe_allow_html=True)


def tile_close():
    st.markdown("</article>", unsafe_allow_html=True)