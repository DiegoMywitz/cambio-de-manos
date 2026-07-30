import json
from pathlib import Path

import plotly.graph_objects as go

from database import PROVINCIAS, listar_conteo_por_provincia, listar_publicaciones

GEOJSON_PATH = Path(__file__).parent / "assets" / "provincias.geojson"

_GEOJSON = None


def _cargar_geojson():
    global _GEOJSON
    if _GEOJSON is None:
        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            _GEOJSON = json.load(f)
    return _GEOJSON


def _texto_hover(provincia: str, cantidad: int) -> str:
    if cantidad == 0:
        return f"<b>{provincia}</b><br>Sin negocios publicados"

    ejemplos = listar_publicaciones(provincia=provincia)[:5]
    lineas = [f"<b>{provincia}</b>", f"{cantidad} negocio(s) publicado(s)", ""]
    for pub in ejemplos:
        titulo = pub["titulo"][:40] + ("…" if len(pub["titulo"]) > 40 else "")
        lineas.append(f"• {titulo} ({pub['rubro']})")
    if cantidad > len(ejemplos):
        lineas.append(f"...y {cantidad - len(ejemplos)} más")
    return "<br>".join(lineas)


def mapa_provincias():
    geojson = _cargar_geojson()
    conteos = dict(listar_conteo_por_provincia())

    provincias, cantidades, hovers = [], [], []
    for prov in PROVINCIAS:
        cantidad = conteos.get(prov, 0)
        provincias.append(prov)
        cantidades.append(cantidad)
        hovers.append(_texto_hover(prov, cantidad))

    fig = go.Figure(go.Choropleth(
        geojson=geojson,
        featureidkey="properties.provincia",
        locations=provincias,
        z=cantidades,
        text=hovers,
        hoverinfo="text",
        colorscale=[[0, "#cfe3f5"], [0.5, "#5b84b1"], [1, "#c0392b"]],
        marker_line_color="#ffffff",
        marker_line_width=0.8,
        colorbar=dict(title="Negocios", thickness=14, len=0.75),
    ))
    fig.update_geos(
        scope="south america",
        center=dict(lon=-65, lat=-38),
        projection_scale=2.6,
        showland=True, landcolor="#f0f2f5",
        showocean=True, oceancolor="#f7f8fa",
        showcountries=True, countrycolor="#c9d2de",
        showsubunits=False,
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
        fitbounds=False,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=440,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
