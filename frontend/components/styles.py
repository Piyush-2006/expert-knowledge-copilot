from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
  st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

      :root {
        --bg-primary: #0b0f14;
        --bg-secondary: #121821;
        --bg-elevated: #1a2230;
        --accent: #f59e0b;
        --accent-soft: rgba(245, 158, 11, 0.15);
        --text-primary: #e8edf5;
        --text-muted: #9aa7b8;
        --border: #2a3444;
        --success: #22c55e;
        --danger: #ef4444;
      }

      .stApp {
        background:
          radial-gradient(circle at top right, rgba(245, 158, 11, 0.08), transparent 30%),
          linear-gradient(180deg, var(--bg-primary) 0%, #070a0f 100%);
        color: var(--text-primary);
        font-family: "IBM Plex Sans", sans-serif;
      }

      [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f141c 0%, #0a0e14 100%);
        border-right: 1px solid var(--border);
      }

      [data-testid="stSidebar"] * {
        color: var(--text-primary);
      }

      .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1100px;
      }

      .hero-card, .metric-card, .citation-card, .document-card {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
      }

      .hero-card {
        margin-bottom: 1rem;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(26, 34, 48, 0.95));
      }

      .hero-title {
        font-size: 1.55rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.02em;
      }

      .hero-subtitle {
        color: var(--text-muted);
        margin-top: 0.35rem;
        font-size: 0.95rem;
      }

      .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid var(--border);
        background: rgba(255, 255, 255, 0.03);
      }

      .status-online { color: var(--success); border-color: rgba(34, 197, 94, 0.35); }
      .status-offline { color: var(--danger); border-color: rgba(239, 68, 68, 0.35); }

      .confidence-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(245, 158, 11, 0.35);
      }

      .citation-card {
        margin-top: 0.55rem;
      }

      .citation-meta {
        color: var(--accent);
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
      }

      .citation-excerpt {
        color: var(--text-muted);
        font-size: 0.88rem;
        line-height: 1.45;
      }

      .document-card {
        margin-bottom: 0.65rem;
      }

      .document-name {
        font-weight: 600;
        font-size: 0.92rem;
      }

      .document-meta {
        color: var(--text-muted);
        font-size: 0.78rem;
        margin-top: 0.2rem;
      }

      div[data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.4rem 0.2rem;
      }

      .stChatInput textarea {
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
      }

      .stButton > button {
        border-radius: 10px;
        border: 1px solid var(--border);
        background: var(--bg-elevated);
        color: var(--text-primary);
      }

      .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #111827;
        border: none;
        font-weight: 600;
      }

      @media (max-width: 768px) {
        .block-container {
          padding-left: 0.8rem;
          padding-right: 0.8rem;
        }

        .hero-title {
          font-size: 1.25rem;
        }

        .hero-card, .metric-card, .citation-card, .document-card {
          padding: 0.85rem;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
  )
