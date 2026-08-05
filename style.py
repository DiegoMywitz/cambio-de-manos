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
            gap: 1rem;
            background-color: {BG};
            border-radius: 4px;
            padding: 1.1rem 1.2rem;
            margin-bottom: 1rem;
            cursor: pointer;
        }}
        .cdm-logo-panel.cdm-logo-panel--static {{
            cursor: default;
            padding: 0.5rem 0 1.3rem 0;
            background-color: transparent;
        }}
        .cdm-logo-panel img {{
            width: 62px;
            height: 62px;
            flex-shrink: 0;
        }}
        .cdm-logo-word {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-weight: 700;
            font-size: 1.35rem;
            line-height: 1.08;
            letter-spacing: 0.3px;
            color: {NAVY_DARK} !important;
            text-shadow: none !important;
        }}
        .cdm-logo-tagline {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 0.68rem;
            letter-spacing: 1.3px;
            color: {ICON_BLUE} !important;
            margin-top: 0.2rem;
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

        .cdm-como-funciona {{
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
            margin-top: 0.4rem;
        }}
        .cdm-como-funciona-paso {{
            display: flex;
            align-items: flex-start;
            gap: 0.7rem;
        }}
        .cdm-como-funciona-icono {{
            flex: none;
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 50%;
            background-color: {NAVY};
            border: 1px solid {ICON_BLUE};
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .cdm-como-funciona-icono svg {{
            width: 1.05rem;
            height: 1.05rem;
            stroke: {ICON_BLUE};
        }}
        .cdm-como-funciona-texto {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 0.82rem;
            line-height: 1.35;
            padding-top: 0.25rem;
            color: #d7dde5 !important;
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

            // El sitio ya está en español: le pedimos a Chrome que nunca
            // ofrezca traducirlo (la traducción automática rompe el estilo
            // del logo y de otros textos con formato).
            const noTranslate = d.createElement('meta');
            noTranslate.name = 'google';
            noTranslate.content = 'notranslate';
            d.head.appendChild(noTranslate);
            d.documentElement.setAttribute('translate', 'no');
            d.documentElement.classList.add('notranslate');
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def scroll_to_top():
    """Vuelve el scroll al principio de la página. Streamlit no navega de verdad
    entre pantallas (es todo la misma página), así que al cambiar de sección el
    navegador mantiene el scroll donde estaba.

    En esta versión de Streamlit, el scroll real no ocurre en `window` — ocurre
    en el contenedor interno `[data-testid="stMain"]` (confirmado inspeccionando
    scrollHeight/clientHeight de los elementos). `window.scrollTo()` no hacía
    nada porque apuntaba al lugar equivocado. Reintenta durante varios segundos
    por si un formulario (ej. login en la ficha de un negocio) autoenfoca un
    campo y vuelve a mover el scroll después de la primera corrección."""
    components.html(
        """
        <script>
        function irArriba() {
            var doc = window.parent.document;
            var main = doc.querySelector('[data-testid="stMain"]');
            if (main) { main.scrollTo(0, 0); }
            window.parent.scrollTo(0, 0);
        }
        var _intentos = [0, 100, 250, 500, 900, 1400, 2000, 2800];
        _intentos.forEach(function(ms) { setTimeout(irArriba, ms); });
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


_ICONO_PUBLICAR = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="5" y="3.5" width="14" height="17" rx="1.5"></rect>'
    '<line x1="8" y1="8" x2="16" y2="8"></line>'
    '<line x1="8" y1="12" x2="16" y2="12"></line>'
    '<line x1="8" y1="16" x2="13" y2="16"></line>'
    '</svg>'
)
_ICONO_BUSCAR = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="10.5" cy="10.5" r="6.5"></circle>'
    '<line x1="15.5" y1="15.5" x2="20.5" y2="20.5"></line>'
    '</svg>'
)
_ICONO_CONSULTA = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M4 5.5h16v11H9.5L5 20v-3.5H4v-11z"></path>'
    '</svg>'
)
_ICONO_ACUERDO = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="8.5"></circle>'
    '<path d="M8 12.5l2.5 2.5 5.5-5.5"></path>'
    '</svg>'
)

_PASOS_COMO_FUNCIONA = [
    (_ICONO_PUBLICAR, "El vendedor publica datos básicos del negocio, sin exponer información confidencial."),
    (_ICONO_BUSCAR, "El comprador filtra por rubro, ubicación y presupuesto."),
    (_ICONO_CONSULTA, "Si hay interés, deja sus datos y el vendedor evalúa si avanza."),
    (_ICONO_ACUERDO, "El contacto directo y la negociación quedan entre las partes."),
]


def como_funciona():
    pasos_html = "".join(
        f'<div class="cdm-como-funciona-paso">'
        f'<div class="cdm-como-funciona-icono">{icono}</div>'
        f'<div class="cdm-como-funciona-texto">{texto}</div>'
        f'</div>'
        for icono, texto in _PASOS_COMO_FUNCIONA
    )
    st.markdown(f'<div class="cdm-como-funciona">{pasos_html}</div>', unsafe_allow_html=True)


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


def sidebar_logo(on_click=None, args=None):
    with st.sidebar.container(key="logo_click_wrap"):
        st.markdown(
            f'<div class="cdm-logo-panel"><img src="data:image/svg+xml;base64,{_logo_base64()}" alt="Cambio de Manos"><div><div class="cdm-logo-word">CAMBIO<br>DE MANOS</div><div class="cdm-logo-tagline">COMPRAVENTA DE EMPRESAS</div></div></div>',
            unsafe_allow_html=True,
        )
        st.button("Ir al inicio", key="logo_home_btn", use_container_width=True,
                   on_click=on_click, args=args or ())
