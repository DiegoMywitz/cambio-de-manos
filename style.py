from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

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
            text-shadow: 0 1px 0 rgba(255,255,255,0.65), 0 2px 4px rgba(15,38,71,0.18);
        }}

        p, span, label, div, li {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
        }}

        [data-testid="stSidebar"] {{
            background-color: {NAVY_DARK};
            border-right: 1px solid {NAVY};
            min-width: 320px !important;
            width: 320px !important;
        }}
        [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}
        [data-testid="stSidebar"] * {{
            color: #e8ebef !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #ffffff !important;
        }}
        [data-testid="stSidebar"] .cdm-logo-word {{
            color: {NAVY_DARK} !important;
        }}
        [data-testid="stSidebar"] .cdm-logo-tagline {{
            color: {ICON_BLUE} !important;
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
        [data-testid="stSidebarUserContent"] {{
            padding-top: 1rem;
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

        .st-key-login_top_btn {{
            display: flex;
            justify-content: flex-end;
        }}
        .st-key-login_top_btn .stButton > button {{
            font-size: 0.75rem;
            padding: 0.15rem 0.7rem;
            border-radius: 999px;
            color: {SLATE};
            border-color: {BORDER};
        }}
        .st-key-login_top_btn .stButton > button:hover {{
            color: {ACCENT_BLUE};
            border-color: {ACCENT_BLUE};
        }}

        .st-key-logo_click_wrap {{
            position: relative;
        }}
        .st-key-logo_click_wrap [data-testid="stButton"] {{
            position: absolute;
            inset: 0;
            z-index: 2;
            margin: 0 !important;
        }}
        .st-key-logo_click_wrap [data-testid="stButton"] button {{
            width: 100%;
            height: 100%;
            opacity: 0;
            border: none;
            padding: 0;
        }}

        .cdm-logo-panel {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
            background-color: {BG};
            border-radius: 4px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
            cursor: pointer;
        }}
        .cdm-logo-panel.cdm-logo-panel--static {{
            cursor: default;
            padding: 0.4rem 0 1.1rem 0;
            background-color: transparent;
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
            text-shadow: 0 1px 0 rgba(255,255,255,0.7), 0 2px 3px rgba(15,38,71,0.2);
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
            letter-spacing: 1.4px;
            font-size: 1rem;
            color: {GOLD};
            font-weight: 700;
            margin-bottom: 0.2rem;
            text-shadow: 0 1px 0 rgba(255,255,255,0.6), 0 1px 2px rgba(15,38,71,0.15);
        }}

        [data-testid="stVerticalBlockBorderWrapper"]:has(.cdm-badge-destacado) {{
            border-left: 4px solid {GOLD} !important;
        }}

        .cdm-badge-franquicia {{
            display: inline-block;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-size: 0.75rem;
            font-weight: 700;
            color: #ffffff;
            background-color: {ACCENT_BLUE};
            border-radius: 999px;
            padding: 0.2rem 0.7rem;
            margin-bottom: 0.4rem;
        }}

        [data-testid="stVerticalBlockBorderWrapper"]:has(.cdm-badge-franquicia):not(:has(.cdm-badge-destacado)) {{
            border-left: 4px solid {ACCENT_BLUE} !important;
        }}

        /* En celulares el sidebar fijo de 320px y sin botón para cerrar tapa toda la
           pantalla. Restauramos el comportamiento normal (colapsable) solo en mobile. */
        @media (max-width: 640px) {{
            [data-testid="stSidebar"] {{
                width: 85vw !important;
                min-width: 0 !important;
            }}
            [data-testid="stSidebarCollapseButton"] {{
                display: flex !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_pwa():
    """Agrega el manifest.json y los meta tags de PWA al <head> real de la página,
    para que el celular ofrezca 'Agregar a la pantalla de inicio'. Streamlit no
    da control directo sobre el <head>, así que se inyecta vía JS desde un
    componente (su iframe es del mismo origen, por eso puede tocar el documento
    padre)."""
    components.html(
        """
        <script>
        (function() {
            const d = window.parent.document;
            if (d.querySelector('link[rel="manifest"]')) { return; }

            const manifest = d.createElement('link');
            manifest.rel = 'manifest';
            manifest.href = '/app/static/manifest.json';
            d.head.appendChild(manifest);

            const themeColor = d.createElement('meta');
            themeColor.name = 'theme-color';
            themeColor.content = '#0f2647';
            d.head.appendChild(themeColor);

            const appleIcon = d.createElement('link');
            appleIcon.rel = 'apple-touch-icon';
            appleIcon.href = '/app/static/icon-192.png';
            d.head.appendChild(appleIcon);

            const appleCapable = d.createElement('meta');
            appleCapable.name = 'apple-mobile-web-app-capable';
            appleCapable.content = 'yes';
            d.head.appendChild(appleCapable);

            const appleTitle = d.createElement('meta');
            appleTitle.name = 'apple-mobile-web-app-title';
            appleTitle.content = 'Cambio de Manos';
            d.head.appendChild(appleTitle);
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def kicker(text: str):
    st.markdown(f'<div class="cdm-kicker">{text}</div>', unsafe_allow_html=True)


def badge_destacado():
    st.markdown('<div class="cdm-badge-destacado">★ Destacado</div>', unsafe_allow_html=True)


def badge_franquicia():
    st.markdown('<div class="cdm-badge-franquicia">◆ Franquicia</div>', unsafe_allow_html=True)


_LOGO_B64 = None


def _logo_base64() -> str:
    global _LOGO_B64
    if _LOGO_B64 is None:
        import base64
        svg_bytes = (ASSETS_DIR / "logo.svg").read_bytes()
        _LOGO_B64 = base64.b64encode(svg_bytes).decode("ascii")
    return _LOGO_B64


def main_logo():
    st.markdown(
        f'<div class="cdm-logo-panel cdm-logo-panel--static"><img src="data:image/svg+xml;base64,{_logo_base64()}" alt="Cambio de Manos"><div><div class="cdm-logo-word">CAMBIO<br>DE MANOS</div><div class="cdm-logo-tagline">COMPRAVENTA DE EMPRESAS</div></div></div>',
        unsafe_allow_html=True,
    )


def sidebar_logo():
    with st.sidebar.container(key="logo_click_wrap"):
        st.markdown(
            f'<div class="cdm-logo-panel"><img src="data:image/svg+xml;base64,{_logo_base64()}" alt="Cambio de Manos"><div><div class="cdm-logo-word">CAMBIO<br>DE MANOS</div><div class="cdm-logo-tagline">COMPRAVENTA DE EMPRESAS</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Ir al inicio", key="logo_home_btn", use_container_width=True):
            st.session_state.vista = "buscar"
            st.session_state.pub_seleccionada = None
            st.rerun()
