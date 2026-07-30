import plotly.graph_objects as go

from database import PROVINCIAS, listar_conteo_por_provincia

# [longitud, latitud] del centroide de cada provincia (fuente: Georef API, Ministerio del Interior).
# Tierra del Fuego se ajustó manualmente: el centroide oficial cae en la Antártida.
PROVINCIA_COORDS = {
    "CABA": (-58.4459, -34.6144),
    "Neuquén": (-70.1199, -38.6420),
    "San Luis": (-66.0252, -33.7611),
    "Santa Fe": (-60.9507, -30.7088),
    "La Rioja": (-67.1818, -29.6849),
    "Catamarca": (-66.9479, -27.3360),
    "Tucumán": (-65.3648, -26.9483),
    "Chaco": (-60.7651, -26.3870),
    "Formosa": (-59.9322, -24.8951),
    "Santa Cruz": (-69.9558, -48.8155),
    "Chubut": (-68.5267, -43.7886),
    "Mendoza": (-68.5829, -34.6304),
    "Entre Ríos": (-59.2013, -32.0589),
    "San Juan": (-68.8882, -30.8657),
    "Jujuy": (-65.7644, -23.3200),
    "Santiago del Estero": (-63.2526, -27.7834),
    "Río Negro": (-67.2297, -40.4051),
    "Corrientes": (-57.8011, -28.7742),
    "Misiones": (-54.6516, -26.8753),
    "Salta": (-64.8142, -24.2993),
    "Córdoba": (-63.8020, -32.1448),
    "Buenos Aires": (-60.5585, -36.6774),
    "La Pampa": (-65.4476, -37.1351),
    "Tierra del Fuego": (-67.7000, -54.4000),
}


def mapa_provincias():
    conteos = dict(listar_conteo_por_provincia())

    provincias, lons, lats, cantidades, textos = [], [], [], [], []
    for prov in PROVINCIAS:
        if prov not in PROVINCIA_COORDS:
            continue
        lon, lat = PROVINCIA_COORDS[prov]
        cantidad = conteos.get(prov, 0)
        provincias.append(prov)
        lons.append(lon)
        lats.append(lat)
        cantidades.append(cantidad)
        textos.append(f"{prov}: {cantidad} negocio(s)")

    tamanios = [14 + c * 6 for c in cantidades]

    fig = go.Figure(go.Scattergeo(
        lon=lons, lat=lats, text=textos, hoverinfo="text",
        mode="markers",
        marker=dict(
            size=tamanios,
            color=cantidades,
            colorscale=[[0, "#c9d2de"], [1, "#0f2647"]],
            line=dict(width=1, color="#ffffff"),
            sizemode="diameter",
        ),
    ))
    fig.update_geos(
        scope="south america",
        center=dict(lon=-65, lat=-38),
        projection_scale=2.6,
        showland=True, landcolor="#f0f2f5",
        showocean=True, oceancolor="#f7f8fa",
        showcountries=True, countrycolor="#c9d2de",
        showsubunits=True, subunitcolor="#dde2e8",
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
