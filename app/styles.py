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
        --ssa-blue: #003399;
        --ssa-navy: #0A192F;
        --ssa-slate: #708090;
        --ssa-white: #F4F4F9;
        --ssa-green: #2E8B57;
        --ssa-gold: #D4AF37;
        --ssa-border: rgba(10, 25, 47, 0.82);
        --ssa-soft-border: rgba(10, 25, 47, 0.18);
        --ssa-paper: rgba(255, 255, 255, 0.92);
        --ssa-frost: rgba(244, 244, 249, 0.74);
        --ssa-grid: rgba(112, 128, 144, 0.08);
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stHeader"],
    #MainMenu,
    footer {
        display: none !important;
    }

    .stAppHeader {
        display: none !important;
    }

    .stApp {
        background:
            linear-gradient(180deg, rgba(0, 51, 153, 0.035), rgba(10, 25, 47, 0.01)),
            linear-gradient(90deg, var(--ssa-grid) 1px, transparent 1px),
            linear-gradient(var(--ssa-grid) 1px, transparent 1px),
            linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 244, 249, 0.96));
        background-size: auto, 18px 18px, 18px 18px, auto;
        color: var(--ssa-navy);
        font-family: "IBM Plex Sans", "Aptos", "Segoe UI", sans-serif;
    }

    .block-container {
        max-width: 1760px;
        padding-top: 0.35rem;
        padding-bottom: 1.4rem;
    }

    h1, h2, h3, p, label, span, div {
        color: var(--ssa-navy);
        line-height: 1.35;
    }

    .ssa-topbar {
        border: 2px solid var(--ssa-border);
        border-radius: 28px;
        padding: 20px 34px;
        margin-top: 0;
        margin-bottom: 16px;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(244, 244, 249, 0.82)),
            linear-gradient(90deg, rgba(112, 128, 144, 0.08) 1px, transparent 1px),
            linear-gradient(rgba(112, 128, 144, 0.08) 1px, transparent 1px);
        background-size: auto, 26px 26px, 26px 26px;
    }

    .ssa-brand-line {
        display: flex;
        align-items: baseline;
        justify-content: center;
        gap: 14px;
        flex-wrap: wrap;
    }

    .ssa-brand {
        font-size: 44px;
        font-weight: 700;
        letter-spacing: -0.04em;
    }

    .ssa-claim {
        font-size: 28px;
        font-weight: 400;
        letter-spacing: -0.03em;
    }

    .ssa-section-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.03em;
        margin: 0 0 10px 0;
    }

    .ssa-section-title-output {
        margin-top: 14px;
    }

    .ssa-muted {
        color: var(--ssa-slate);
        font-size: 16px;
        margin: 0;
    }

    .ssa-message,
    .ssa-error {
        border-radius: 16px;
        padding: 12px 14px;
        margin: 10px 0 8px;
        border: 1px solid var(--ssa-soft-border);
        font-size: 16px;
    }

    .ssa-message {
        background: rgba(46, 139, 87, 0.12);
        border-color: rgba(46, 139, 87, 0.28);
    }

    .ssa-error {
        background: rgba(212, 175, 55, 0.14);
        border-color: rgba(212, 175, 55, 0.45);
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--ssa-navy) !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 24px !important;
        border: 2px solid rgba(10, 25, 47, 0.82) !important;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(244, 244, 249, 0.82)),
            radial-gradient(circle at top right, rgba(212, 175, 55, 0.04), transparent 32%) !important;
        box-shadow: none !important;
        padding: 12px !important;
    }

    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input {
        border-radius: 22px !important;
        border: 2px solid rgba(10, 25, 47, 0.78) !important;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 244, 249, 0.94)) !important;
        color: var(--ssa-navy) !important;
        box-shadow: none !important;
        font-size: 17px !important;
    }

    .stTextArea textarea {
        padding: 14px 16px !important;
        line-height: 1.45 !important;
    }

    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: rgba(112, 128, 144, 0.92) !important;
    }

    .stButton > button {
        min-height: 60px;
        border-radius: 22px;
        border: 2px solid var(--ssa-border) !important;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(244, 244, 249, 0.92)) !important;
        color: var(--ssa-navy) !important;
        box-shadow: none !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        padding: 0 18px !important;
        font-family: "Aptos", "Segoe UI", sans-serif !important;
    }

    .stButton > button:hover,
    .stButton > button:focus,
    .stButton > button:active {
        border-color: var(--ssa-blue) !important;
        color: var(--ssa-blue) !important;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(244, 244, 249, 0.92)) !important;
        box-shadow: none !important;
    }

    .stButton > button p {
        font-size: 20px !important;
        font-weight: 700 !important;
        line-height: 1.1 !important;
        color: var(--ssa-navy) !important;
        font-family: "Aptos", "Segoe UI", sans-serif !important;
    }

    .stButton > button[kind="primary"],
    .stButton > button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:focus,
    .stButton > button[kind="primary"]:active {
        background: linear-gradient(180deg, rgba(0, 51, 153, 0.98), rgba(10, 25, 47, 0.98));
        color: white !important;
        border-color: rgba(0, 51, 153, 0.98);
    }

    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"]:hover p {
        color: rgba(244, 244, 249, 0.98) !important;
    }

    .st-key-run_prompt_shell .stButton > button,
    .st-key-run_prompt_shell .stButton > button:hover,
    .st-key-run_prompt_shell .stButton > button:focus,
    .st-key-run_prompt_shell .stButton > button:active {
        min-height: 60px !important;
        border-radius: 22px !important;
        border: 2px solid rgba(0, 51, 153, 0.98) !important;
        background: linear-gradient(180deg, rgba(0, 51, 153, 0.98), rgba(10, 25, 47, 0.98)) !important;
        color: rgba(244, 244, 249, 0.98) !important;
        box-shadow: none !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        padding: 0 18px !important;
        font-family: "Aptos", "Segoe UI", sans-serif !important;
    }

    .st-key-run_prompt_shell .stButton > button p,
    .st-key-run_prompt_shell .stButton > button:hover p,
    .st-key-run_prompt_shell .stButton > button:focus p,
    .st-key-run_prompt_shell .stButton > button:active p {
        color: rgba(244, 244, 249, 0.98) !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        line-height: 1.1 !important;
        font-family: "Aptos", "Segoe UI", sans-serif !important;
    }

    .st-key-history_cards .stButton > button,
    .st-key-history_cards button[kind="secondary"],
    .st-key-history_cards button[kind="secondary"]:hover,
    .st-key-history_cards button[kind="secondary"]:focus,
    .st-key-history_cards button[kind="secondary"]:active {
        min-height: 84px !important;
        height: auto !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        justify-content: flex-start;
        align-items: flex-start;
        padding: 12px 14px !important;
        margin-bottom: 10px;
        border-radius: 20px !important;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(244, 244, 249, 0.92)) !important;
        color: var(--ssa-navy) !important;
        border: 2px solid var(--ssa-border) !important;
        box-shadow: none !important;
    }

    .st-key-history_cards .stButton > button p,
    .st-key-history_cards button[kind="secondary"] p {
        text-align: left;
        white-space: normal !important;
        font-size: 16px !important;
        line-height: 1.3 !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden !important;
    }

    .st-key-upload_button_shell [data-testid="stFileUploaderDropzone"] {
        min-height: 60px;
        border-radius: 22px !important;
        border: 2px solid var(--ssa-border) !important;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(244, 244, 249, 0.92)) !important;
        padding: 0 !important;
        position: relative !important;
        overflow: hidden !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
    }

    .st-key-upload_button_shell [data-testid="stFileUploaderDropzone"]::after {
        content: "Add File";
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--ssa-navy);
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.02em;
        pointer-events: none;
        font-family: "Aptos", "Segoe UI", sans-serif !important;
    }

    .st-key-upload_button_shell [data-testid="stFileUploaderDropzoneInstructions"],
    .st-key-upload_button_shell [data-testid="stFileUploader"] small,
    .st-key-upload_button_shell [data-testid="stFileUploader"] svg,
    .st-key-upload_button_shell [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
        display: none !important;
    }

    .st-key-upload_button_shell [data-testid="stFileUploaderDropzone"] button {
        width: 100%;
        min-height: 58px;
        border-radius: 20px !important;
        border: 0 !important;
        background: transparent !important;
        color: transparent !important;
        box-shadow: none !important;
        position: relative;
        font-size: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
    }

    .st-key-upload_button_shell [data-testid="stFileUploaderDropzone"] p,
    .st-key-upload_button_shell [data-testid="stFileUploaderDropzone"] span {
        color: transparent !important;
        font-size: 0 !important;
        opacity: 0 !important;
    }

    .st-key-upload_button_shell [data-testid="stFileUploader"] {
        width: 100%;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        min-height: 62px;
        font-size: 18px !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background: rgba(255, 255, 255, 0.98) !important;
        color: var(--ssa-navy) !important;
        border: 1.5px solid rgba(10, 25, 47, 0.22) !important;
        border-radius: 20px !important;
        box-shadow: none !important;
    }

    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] *,
    ul[role="listbox"] * {
        color: var(--ssa-navy) !important;
    }

    li[role="option"],
    div[role="option"] {
        background: rgba(255, 255, 255, 0.98) !important;
        color: var(--ssa-navy) !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    li[role="option"]:hover,
    div[role="option"]:hover {
        background: rgba(0, 51, 153, 0.08) !important;
    }

    iframe[title^="components.html"] {
        border-radius: 22px;
        display: block;
        margin: 0 !important;
    }

    .st-key-copy_output_shell iframe[title^="components.html"] {
        height: 60px !important;
    }

    @media (max-width: 1400px) {
        .ssa-brand {
            font-size: 38px;
        }

        .ssa-claim {
            font-size: 24px;
        }
    }
    </style>
    """
    )
