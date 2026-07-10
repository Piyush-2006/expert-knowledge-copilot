from __future__ import annotations

from typing import Any
import streamlit as st

from frontend.components.api_client import (
    APIClient,
    APIError,
)


##########################################################
# Sources
##########################################################

def render_citations(
    citations: list[dict[str, Any]],
    chunks: list[dict[str, Any]] | None = None,
):

    if not citations:
        st.caption(
            "No source citations available."
        )
        return

    chunk_lookup = {
        (
            chunk.get("document_name"),
            chunk.get("page_number"),
        ): chunk
        for chunk in (chunks or [])
    }

    st.markdown("### 📚 Sources")

    for i, citation in enumerate(
        citations,
        start=1,
    ):

        document_name = citation.get(
            "document_name",
            "Unknown",
        )

        page_number = citation.get(
            "page_number",
            "?",
        )

        chunk = chunk_lookup.get(
            (
                document_name,
                page_number,
            )
        )

        excerpt = (
            (chunk or {})
            .get("content", "")
            .strip()
        )

        with st.expander(
            f"[{i}] {document_name} - Page {page_number}"
        ):

            st.write(
                excerpt[:1000]
            )


##########################################################
# Chat History
##########################################################

def render_chat_history():

    for message in (
        st.session_state.chat_history
    ):

        role = message["role"]

        with st.chat_message(role):

            st.markdown(
                message["content"]
            )

            ##################################################
            # Assistant Details
            ##################################################

            if role == "assistant":

                confidence = message.get(
                    "confidence_score"
                )

                confidence_level = message.get(
                    "confidence_level"
                )

                processing_time = message.get(
                    "processing_time"
                )

                cols = st.columns(3)

                cols[0].metric(
                    "Confidence",
                    f"{confidence:.1f}%"
                    if confidence
                    else "0%",
                )

                cols[1].metric(
                    "Level",
                    confidence_level
                    or "Low",
                )

                cols[2].metric(
                    "Response Time",
                    f"{processing_time}s"
                    if processing_time
                    else "-",
                )

                render_citations(
                    message.get(
                        "citations",
                        [],
                    ),
                    message.get(
                        "chunks",
                        [],
                    ),
                )

                ##################################################
                # Download
                ##################################################

                st.download_button(
                    "⬇ Download Answer",
                    data=message["content"],
                    file_name="answer.md",
                    mime="text/markdown",
                )


##########################################################
# Query
##########################################################

def handle_user_query(
    api: APIClient,
):

    prompt = st.chat_input(
        "Ask about procedures, equipment, incidents, SOPs..."
    )

    if not prompt:
        return

    ######################################################
    # User
    ######################################################

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message(
        "user"
    ):
        st.markdown(prompt)

    ######################################################
    # Assistant
    ######################################################

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Searching knowledge base..."
        ):

            try:

                result = api.query(
                    prompt
                )

            except APIError as exc:

                st.error(
                    str(exc)
                )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content":
                        f"Error: {exc}",
                        "citations": [],
                        "chunks": [],
                        "confidence_score": 0.0,
                        "confidence_level": "Low",
                        "processing_time": 0.0,
                    }
                )

                return

        ##################################################
        # Result
        ##################################################

        answer = result.get(
            "answer",
            "Information not found in provided documents.",
        )

        citations = result.get(
            "citations",
            [],
        )

        chunks = result.get(
            "chunks",
            [],
        )

        confidence_score = float(
            result.get(
                "confidence_score",
                0.0,
            )
        )

        confidence_level = result.get(
            "confidence_level",
            "Low",
        )

        processing_time = result.get(
            "processing_time",
            0.0,
        )

        ##################################################
        # UI
        ##################################################

        st.markdown(
            answer
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Confidence",
            f"{confidence_score:.1f}%"
        )

        c2.metric(
            "Level",
            confidence_level
        )

        c3.metric(
            "Time",
            f"{processing_time}s"
        )

        render_citations(
            citations,
            chunks,
        )

        st.download_button(
            "⬇ Download Answer",
            data=answer,
            file_name="answer.md",
            mime="text/markdown",
        )

        ##################################################
        # Save Chat
        ##################################################

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
                "citations": citations,
                "chunks": chunks,
                "confidence_score":
                confidence_score,
                "confidence_level":
                confidence_level,
                "processing_time":
                processing_time,
            }
        )