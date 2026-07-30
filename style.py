from pathlib import Path

import streamlit as st

NAVY = "#0f2647"
NAVY_DARK = "#0a1b33"
SLATE = "#4a5568"
SLATE_LIGHT = "#8b96a5"
BORDER = "#dde2e8"
BG = "#f7f8fa"
GOLD = "#e0a30e"
ICON_BLUE = "#5b84b1"
ACCENT_BLUE = "#2d6cdf"
GOLD_LIGHT = "#fdf1d6"

ASSETS_DIR = Path(__file__).parent / "assets"


def inject():
    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-family: 'Georgia', 'Times New Roman', serif;
        }}

        .stApp {{
            background-color: {BG};
        }}

        h1, h2, h3 {{
            font-family: 'Georgia', 'Times New Roman', serif !important;
            color: {NAVY_DARK} !important;
            letter-spacing: 0.2px;
        }}

        p, span, label, div, li {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
        }}

        [data-testid="stSidebar"] {{
            background-color: {NAVY_DARK};
            border-right: 1px solid {NAVY};
        }}
        [data-testid="stSidebar"] * {{
            color: #e8ebef !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #ffffff !important;
        }}
        [data-testid="stSidebar"] .stButton button {{
            background-color: transparent;
            color: #e8ebef;
            border: 1px solid {SLATE_LIGHT}55;
            text-align: left;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-weight: 500;
            letter-spacing: 0.3px;
        }}
        [data-testid="stSidebar"] .stButton button:hover {{
            border-color: {GOLD};
            color: #ffffff;
        }}
        [data-testid="stSidebarUserContent"] hr {{
            border-color: {SLATE_LIGHT}44;
        }}

        .stButton > button[kind="primary"] {{
            background-color: {ACCENT_BLUE};
            border: 1px solid {ACCENT_BLUE};
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-weight: 600;
            letter-spacing: 0.3px;
            border-radius: 4px;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {NAVY_DARK};
            border-color: {NAVY_DARK};
        }}
        .stButton > button:not([kind="primary"]) {{
            border-radius: 4px;
            border: 1px solid {BORDER};
            color: {NAVY_DARK};
        }}
        .stButton > button:not([kind="primary"]):hover {{
            border-color: {ACCENT_BLUE};
            color: {ACCENT_BLUE};
        }}

        [data-testid="stMetricValue"] {{
            color: {ACCENT_BLUE};
            font-family: 'Georgia', serif;
            font-weight: 700;
        }}
        [data-testid="stMetricLabel"] {{
            color: {SLATE};
            font-family: 'Helvetica Neue', Arial, sans-serif;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
        }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: {BORDER} !important;
            border-radius: 3px !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(button):hover {{
            border-color: {SLATE_LIGHT} !important;
            box-shadow: 0 2px 10px rgba(15, 38, 71, 0.08);
        }}

        hr {{
            border-color: {BORDER};
        }}

        .cdm-kicker {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-size: 0.75rem;
            color: {GOLD};
            font-weight: 600;
            margin-bottom: -0.5rem;
        }}

        .cdm-logo-panel {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
            background-color: {BG};
            border-radius: 4px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
        }}
        .cdm-logo-panel img {{
            width: 44px;
            height: 44px;
            flex-shrink: 0;
        }}
        .cdm-logo-word {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-weight: 700;
            font-size: 1.05rem;
            line-height: 1.05;
            letter-spacing: 0.3px;
            color: {NAVY_DARK} !important;
        }}
        .cdm-logo-tagline {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 0.56rem;
            letter-spacing: 1.3px;
            color: {ICON_BLUE} !important;
            margin-top: 0.15rem;
        }}

        .cdm-badge-destacado {{
            display: inline-block;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            text-transform: uppercase;
            letter-spacing: 1.3px;
            font-size: 0.8rem;
            color: {NAVY_DARK};
            background-color: {GOLD_LIGHT};
            border: 1px solid {GOLD};
            border-radius: 20px;
            padding: 0.2rem 0.7rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }}

        [data-testid="stVerticalBlockBorderWrapper"]:has(.cdm-badge-destacado) {{
            border-left: 4px solid {GOLD} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kicker(text: str):
    st.markdown(f'<div class="cdm-kicker">{text}</div>', unsafe_allow_html=True)


def badge_destacado():
    st.markdown('<div class="cdm-badge-destacado">★ Destacado</div>', unsafe_allow_html=True)


_LOGO_B64 = None


def _logo_base64() -> str:
    global _LOGO_B64
    if _LOGO_B64 is None:
        import base64
        svg_bytes = (ASSETS_DIR / "logo.svg").read_bytes()
        _LOGO_B64 = base64.b64encode(svg_bytes).decode("ascii")
    return _LOGO_B64


def sidebar_logo():
    st.sidebar.markdown(
        f"""
        <div class="cdm-logo-panel">
            <img src="data:image/svg+xml;base64,{_logo_base64()}" alt="Cambio de Manos">
            <div>
                <div class="cdm-logo-word">CAMBIO<br>DE MANOS</div>
                <div class="cdm-logo-tagline">COMPRAVENTA DE EMPRESAS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
