"""Localidades de Argentina por provincia, vía la API oficial y gratuita
Georef (Ministerio del Interior): https://apis.datos.gob.ar/georef

No requiere clave. Se cachea por provincia para no golpear la API en cada
rerun de Streamlit.
"""

import requests
import streamlit as st

# Nuestros nombres de provincia (más simples/coloquiales) -> nombre oficial en Georef
_NOMBRE_GEOREF = {
    "CABA": "Ciudad Autónoma de Buenos Aires",
    "Tierra del Fuego": "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
}


@st.cache_data(ttl=86400, show_spinner=False)
def localidades_de_provincia(provincia: str) -> list:
    """Devuelve la lista ordenada de localidades de una provincia. Lista vacía si falla."""
    nombre_georef = _NOMBRE_GEOREF.get(provincia, provincia)
    try:
        r = requests.get(
            "https://apis.datos.gob.ar/georef/api/localidades",
            params={"provincia": nombre_georef, "campos": "nombre", "max": 5000},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        nombres = [loc["nombre"] for loc in data.get("localidades", [])]
        return sorted(set(nombres))
    except Exception:
        return []
