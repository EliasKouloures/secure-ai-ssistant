from __future__ import annotations

import base64
from pathlib import Path


def load_styles() -> str:
    font_face = ""
    font_path = Path("app/assets/fonts/IBMPlexSans-Regular.ttf")
    if font_path.exists():
        encoded = base64.b64encode(font_path.read_bytes()).decode("ascii")
        font_face = f"""
        @font-face {{
            font-family: 'IBM Plex Sans';
            src: url('data:font/ttf;base64,{encoded}') format('truetype');
            font-weight: 400;
            font-style: normal;
        }}
        """
    return (
        """
    <style>
    """
        + font_face
        + """
    :root {
        --sc-navy: #0A192F;
        --sc-slate: #708090;
        --sc-surface: #F4F4F9;
        --sc-accent: #2E8B57;
        --sc-border: rgba(10, 25, 47, 0.16);
        --sc-soft: rgba(244, 244, 249, 0.82);
        --sc-body: 16px;
        --sc-headline: 42px;
    }

    .stApp {
        background:
            linear-gradient(180deg, rgba(10, 25, 47, 0.04), rgba(10, 25, 47, 0.01)),
            linear-gradient(90deg, rgba(112, 128, 144, 0.08) 1px, transparent 1px),
            linear-gradient(rgba(112, 128, 144, 0.08) 1px, transparent 1px),
            var(--sc-surface);
        background-size: auto, 24px 24px, 24px 24px, auto;
        color: var(--sc-navy);
        font-family: "IBM Plex Sans", "Aptos", "Segoe UI", sans-serif;
        font-size: var(--sc-body);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }

    h1, h2, h3, p, label, span, div {
        font-size: var(--sc-body);
        line-height: 1.5;
    }

    .sc-hero {
        border: 1px solid var(--sc-border);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.64));
        backdrop-filter: blur(16px);
        border-radius: 24px;
        padding: 24px;
    }

    .sc-headline {
        font-size: var(--sc-headline);
        line-height: 1.05;
        font-weight: 600;
        letter-spacing: -0.04em;
        color: var(--sc-navy);
        margin: 0 0 8px 0;
    }

    .sc-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 999px;
        border: 1px solid rgba(46, 139, 87, 0.3);
        background: rgba(46, 139, 87, 0.12);
        color: var(--sc-accent);
        font-weight: 600;
    }

    .sc-kpi {
        border: 1px solid var(--sc-border);
        background: rgba(255, 255, 255, 0.7);
        border-radius: 20px;
        padding: 20px;
        text-align: right;
    }

    .sc-kpi-value {
        font-size: var(--sc-headline);
        line-height: 1;
        font-weight: 600;
        color: var(--sc-navy);
    }

    .sc-panel {
        border: 1px solid var(--sc-border);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(255, 255, 255, 0.65));
        border-radius: 24px;
        padding: 24px;
        min-height: 100%;
    }

    .sc-panel-title {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--sc-slate);
        font-weight: 700;
        margin-bottom: 12px;
    }

    .sc-warning {
        border-left: 4px solid #D4AF37;
        background: rgba(212, 175, 55, 0.12);
        padding: 12px 14px;
        margin: 8px 0;
    }

    .sc-error {
        border-left: 4px solid #B22222;
        background: rgba(178, 34, 34, 0.1);
        padding: 12px 14px;
        margin: 8px 0;
    }

    .sc-muted {
        color: var(--sc-slate);
    }

    .stButton > button {
        border-radius: 999px;
        border: 1px solid var(--sc-border);
        padding: 0.7rem 1.2rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.8);
        color: var(--sc-navy);
        box-shadow: none;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #0A192F, #003399);
        color: white;
        border: none;
    }

    .stDownloadButton > button {
        border-radius: 20px;
        border: 1px solid var(--sc-border);
        padding: 0.85rem 1.2rem;
        font-weight: 600;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(244, 244, 249, 0.9));
        color: var(--sc-navy);
        box-shadow: none;
    }

    .stDownloadButton > button:hover {
        border-color: rgba(46, 139, 87, 0.45);
        color: var(--sc-navy);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 244, 249, 0.96));
    }

    .stDownloadButton > button:focus,
    .stDownloadButton > button:focus-visible {
        outline: 2px solid rgba(46, 139, 87, 0.25);
        box-shadow: none;
        color: var(--sc-navy);
    }

    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 16px !important;
    }
    </style>
    """
    )
