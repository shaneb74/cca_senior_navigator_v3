import streamlit as st


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
