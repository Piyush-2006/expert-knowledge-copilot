from __future__ import annotations

import streamlit as st

from frontend.components.api_client import APIClient, APIError


def _render_backend_status(api: APIClient) -> None:
    try:
        health = api.health()
        status_class = "status-online"
        status_text = f"Online · {health.get('environment', 'unknown')}"
    except APIError:
        status_class = "status-offline"
        status_text = "Offline"

    st.markdown(
        f'<span class="status-pill {status_class}">● {status_text}</span>',
        unsafe_allow_html=True,
    )


def refresh_documents(api: APIClient) -> None:
    try:
        payload = api.list_documents()
        st.session_state.documents = payload.get("documents", [])
    except APIError as exc:
        st.session_state.documents = []
        st.sidebar.error(str(exc))


def render_sidebar(api: APIClient) -> None:
    with st.sidebar:
        st.markdown("### Knowledge Base")
        _render_backend_status(api)

        st.markdown("#### Upload PDF")
        uploaded_file = st.file_uploader(
            "Add industrial document",
            type=["pdf"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            if st.button("Ingest document", type="primary", use_container_width=True):
                with st.spinner(f"Ingesting {uploaded_file.name}..."):
                    try:
                        result = api.upload_pdf(uploaded_file.name, uploaded_file.getvalue())
                        st.success(
                            f"Ingested {result['filename']} "
                            f"({result['chunk_count']} chunks, {result['page_count']} pages)"
                        )
                        refresh_documents(api)
                    except APIError as exc:
                        st.error(str(exc))

        st.markdown("#### Retrieval settings")
        st.caption("Queries retrieve the top 4 most relevant chunks.")

        if st.button("Refresh documents", use_container_width=True):
            refresh_documents(api)

        st.markdown("#### Uploaded documents")
        documents = st.session_state.documents

        if not documents:
            st.caption("No documents indexed yet.")
        else:
            for document in documents:
                doc_id = document.get("id", document.get("filename", "unknown"))
                filename = document.get("filename", doc_id)
                chunk_count = document.get("chunk_count", 0)
                pages = document.get("page_numbers", [])

                st.markdown(
                    f"""
                    <div class="document-card">
                        <div class="document-name">{filename}</div>
                        <div class="document-meta">{chunk_count} chunks · pages {", ".join(map(str, pages)) or "-"}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(f"Delete {filename}", key=f"delete-{doc_id}", use_container_width=True):
                    try:
                        deleted = api.delete_document(doc_id)
                        st.success(f"Deleted {deleted['deleted_chunks']} chunks.")
                        refresh_documents(api)
                        st.rerun()
                    except APIError as exc:
                        st.error(str(exc))

        st.markdown("---")
        if st.button("Clear chat history", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        st.caption("Backend: " + st.session_state.api_base_url)
