from __future__ import annotations

import os

import streamlit as st

from frontend.components.api_client import APIClient
from frontend.components.chat import handle_user_query, render_chat_history
from frontend.components.sidebar import refresh_documents, render_sidebar
from frontend.components.styles import inject_theme


def init_session_state() -> None:
    defaults = {
        "api_base_url": os.getenv("API_BASE_URL", "http://127.0.0.1:8000"),
        "chat_history": [],
        "documents": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <p class="hero-title">Expert Knowledge Copilot</p>
            <p class="hero-subtitle">
                Industrial document intelligence with grounded answers, source citations, and confidence scoring.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Expert Knowledge Copilot",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_theme()
    init_session_state()

    api = APIClient(base_url=st.session_state.api_base_url)

    if not st.session_state.get("documents_loaded"):
        refresh_documents(api)
        st.session_state.documents_loaded = True

    render_sidebar(api)
    render_header()

    if not st.session_state.chat_history:
        st.info("Upload PDFs in the sidebar, then ask questions about your industrial knowledge base.")

    render_chat_history()
    handle_user_query(api)


if __name__ == "__main__":
    main()
