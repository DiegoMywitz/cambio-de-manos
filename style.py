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
CORAL = "#e2725b"

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
        [data-testid="stMain"] {{
            overflow-anchor: none;
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
            color: #ffffff !important;
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
            gap: 0.7rem;
            background: none;
            border-radius: 4px;
            padding: 0.5rem 0.2rem;
            margin-bottom: 1rem;
            cursor: pointer;
            position: relative;
        }}
        .cdm-logo-panel img {{
            height: 58px;
            width: auto;
            flex-shrink: 0;
        }}
        .cdm-logo-word {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-weight: 700;
            font-size: 1.05rem;
            line-height: 1.08;
            letter-spacing: 0.3px;
            color: {NAVY_DARK} !important;
            text-shadow: none !important;
        }}
        .cdm-logo-tagline {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 0.58rem;
            letter-spacing: 1.3px;
            color: {ICON_BLUE} !important;
            margin-top: 0.15rem;
        }}

        /* El logo de la portada (estático, arriba de la búsqueda): centrado,
           más grande, sobre una tarjeta con degradé suave — el adorno animado
           queda como fondo detrás en vez de competir por el centro. */
        .cdm-logo-panel.cdm-logo-panel--static {{
            cursor: default;
            padding: 1.8rem 2rem;
            background-color: {BG};
            background-image:
                radial-gradient(circle at 12% 20%, rgba(15,38,71,0.05) 0%, transparent 45%),
                radial-gradient(circle at 88% 80%, rgba(224,163,14,0.08) 0%, transparent 45%);
            border-radius: 18px;
            box-shadow: 0 1px 0 rgba(255,255,255,0.7) inset, 0 10px 28px rgba(15,38,71,0.07);
            justify-content: center;
            gap: 1.3rem;
            margin-bottom: 0.5rem;
            position: relative;
            overflow: hidden;
        }}
        .cdm-logo-panel--static img {{
            height: 104px;
            width: auto;
            position: relative;
            z-index: 1;
        }}
        .cdm-logo-panel--static .cdm-logo-word {{
            font-size: 2.4rem;
            position: relative;
            z-index: 1;
        }}
        .cdm-logo-panel--static .cdm-logo-tagline {{
            font-size: 0.85rem;
            letter-spacing: 2px;
            margin-top: 0.25rem;
            position: relative;
            z-index: 1;
        }}

        .block-container {{
            padding-top: 1.5rem !important;
        }}
        .cdm-logo-panel--static .cdm-logo-decor {{
            position: absolute;
            right: 2.5rem;
            bottom: 1.4rem;
            flex: none;
            opacity: 0.75;
        }}
        .cdm-logo-decor {{
            flex: 1;
            display: flex;
            align-items: flex-end;
            justify-content: flex-end;
            gap: 0.5rem;
            padding-right: 1.2rem;
            min-width: 0;
            height: 64px;
        }}
        .cdm-logo-decor span {{
            display: block;
            width: 12px;
            border-radius: 3px 3px 0 0;
            background: linear-gradient(180deg, {GOLD} 0%, {ACCENT_BLUE} 100%);
            opacity: 0.9;
            animation: cdmLogoGrow 2.4s ease-in-out infinite;
            transform-origin: bottom;
        }}
        .cdm-logo-decor span:nth-child(1) {{ height: 22px; animation-delay: 0s; background: linear-gradient(180deg, {ACCENT_BLUE} 0%, {GOLD} 100%); }}
        .cdm-logo-decor span:nth-child(2) {{ height: 38px; animation-delay: 0.2s; background: linear-gradient(180deg, {GOLD} 0%, {CORAL} 100%); }}
        .cdm-logo-decor span:nth-child(3) {{ height: 55px; animation-delay: 0.4s; background: linear-gradient(180deg, {CORAL} 0%, {ACCENT_BLUE} 100%); }}
        .cdm-logo-decor span:nth-child(4) {{ height: 32px; animation-delay: 0.6s; background: linear-gradient(180deg, {ACCENT_BLUE} 0%, {GOLD} 100%); }}
        .cdm-logo-decor span:nth-child(5) {{ height: 46px; animation-delay: 0.8s; background: linear-gradient(180deg, {GOLD} 0%, {ACCENT_BLUE} 100%); }}
        @keyframes cdmLogoGrow {{
            0%, 100% {{ transform: scaleY(0.55); opacity: 0.55; }}
            50% {{ transform: scaleY(1); opacity: 1; }}
        }}
        @media (max-width: 640px) {{
            .cdm-logo-decor {{ display: none; }}
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
    scrollHeight/clientHeight de los elementos).

    Los reintentos con setTimeout de la versión anterior no servían: Streamlit
    destruye y vuelve a crear este mismo iframe cada vez que sigue llegando
    contenido a la vista nueva (por ejemplo, mientras se cargan los resultados
    de la búsqueda), así que casi ningún setTimeout llegaba a dispararse antes
    de que su propio iframe muriera. En cambio, un MutationObserver reacciona
    a cada cambio real del DOM mientras el iframe esté vivo, y además corrige
    apenas se monta — así, aunque Streamlit lo destruya y lo vuelva a crear
    varias veces seguidas, cada instancia nueva corrige el scroll al nacer."""
    components.html(
        """
        <script>
        function irArriba() {
            var doc = window.parent.document;
            var main = doc.querySelector('[data-testid="stMain"]');
            if (main) { main.scrollTop = 0; }
            window.parent.scrollTo(0, 0);
        }
        irArriba();
        var doc = window.parent.document;
        var objetivo = doc.querySelector('[data-testid="stMain"]') || doc.body;
        var observer = new MutationObserver(irArriba);
        observer.observe(objetivo, {childList: true, subtree: true});
        setTimeout(function() { observer.disconnect(); }, 4000);
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


_LOGO_B64_CACHE = {}


def _logo_base64(nombre_archivo: str) -> str:
    if nombre_archivo not in _LOGO_B64_CACHE:
        import base64
        contenido = (ASSETS_DIR / nombre_archivo).read_bytes()
        _LOGO_B64_CACHE[nombre_archivo] = base64.b64encode(contenido).decode("ascii")
    return _LOGO_B64_CACHE[nombre_archivo]


def main_logo():
    st.markdown(
        f'<div class="cdm-logo-panel cdm-logo-panel--static">'
        f'<img src="data:image/png;base64,{_logo_base64("logo_icon_navy.png")}" alt="Cambio de Manos">'
        f'<div><div class="cdm-logo-word">CAMBIO<br>DE MANOS</div><div class="cdm-logo-tagline">COMPRAVENTA DE EMPRESAS</div></div>'
        f'<div class="cdm-logo-decor"><span></span><span></span><span></span><span></span><span></span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def sidebar_logo(on_click=None, args=None):
    with st.sidebar.container(key="logo_click_wrap"):
        st.markdown(
            f'<div class="cdm-logo-panel"><img src="data:image/png;base64,{_logo_base64("logo_icon_cream.png")}" alt="Cambio de Manos"><div><div class="cdm-logo-word">CAMBIO<br>DE MANOS</div><div class="cdm-logo-tagline">COMPRAVENTA DE EMPRESAS</div></div></div>',
            unsafe_allow_html=True,
        )
        st.button("Ir al inicio", key="logo_home_btn", use_container_width=True,
                   on_click=on_click, args=args or ())
