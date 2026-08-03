"""Localidades de Argentina por provincia, vía la API oficial y gratuita
Georef (Ministerio del Interior): https://apis.datos.gob.ar/georef

No requiere clave. Se cachea por provincia para no golpear la API en cada
rerun de Streamlit. Los fallos NO se cachean (para poder reintentar en la
próxima llamada en vez de quedar vacío por 24hs).
"""

import requests
import streamlit as st

# Nuestros nombres de provincia (más simples/coloquiales) -> nombre oficial en Georef
_NOMBRE_GEOREF = {
    "CABA": "Ciudad Autónoma de Buenos Aires",
    "Tierra del Fuego": "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
}


@st.cache_data(ttl=86400, show_spinner=False)
def _consultar_georef(nombre_georef: str) -> list:
    """Puede lanzar una excepción; st.cache_data no cachea en ese caso."""
    r = requests.get(
        "https://apis.datos.gob.ar/georef/api/localidades",
        params={"provincia": nombre_georef, "campos": "nombre", "max": 5000},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    nombres = [loc["nombre"] for loc in data.get("localidades", [])]
    return sorted(set(nombres))


def localidades_de_provincia(provincia: str) -> list:
    """Devuelve la lista ordenada de localidades de una provincia. Lista vacía si falla."""
    nombre_georef = _NOMBRE_GEOREF.get(provincia, provincia)
    try:
        resultado = _consultar_georef(nombre_georef)
        print(f"georef: OK, {len(resultado)} localidades para '{nombre_georef}'")
        return resultado
    except Exception as e:
        print(f"georef: fallo al consultar localidades de '{nombre_georef}': {type(e).__name__}: {e}")
        return []
