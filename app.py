# app.py — Dashboard Mortalidad Colombia 2019 (Layout 2B, moderno y reorganizado)

import json
import pandas as pd
from dash import Dash, html, dcc, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# =====================================================
# PALETAS DE COLORES
# =====================================================

PALETA = ["#0984e3", "#00cec9", "#6c5ce7", "#fdcb6e", "#e17055"]

COLORES_SEXO = {
    "Femenino": "#ff6bcb",
    "Masculino": "#0984e3",
    "Indeterminado": "#6c5ce7"
}

# =====================================================
# LEER DATOS
# =====================================================

df = pd.read_excel("data/Anexo1.NoFetal2019_CE_15-03-23.xlsx")
codigos = pd.read_excel("data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx")
divipola = pd.read_excel("data/Divipola_CE_.xlsx")

# =====================================================
# CENTROIDES PARA EL MAPA
# =====================================================

centroides = {
    "05": (7.1986, -75.3412),
    "08": (10.9639, -74.7964),
    "11": (4.7110, -74.0721),
    "13": (10.3997, -75.5144),
    "15": (5.4545, -73.3620),
    "17": (5.2983, -75.2479),
    "18": (0.8707, -73.8419),
    "19": (2.4448, -76.6147),
    "20": (9.3373, -75.2856),
    "23": (8.7575, -75.8850),
    "25": (4.4389, -74.6380),
    "27": (5.6947, -76.6613),
    "41": (2.7800, -75.2500),
    "44": (11.5444, -72.9070),
    "47": (11.2408, -74.1990),
    "50": (3.2700, -73.0850),
    "52": (1.2136, -77.2811),
    "54": (7.9463, -72.8988),
    "63": (4.5339, -75.6811),
    "66": (4.8133, -75.6961),
    "68": (7.1254, -73.1198),
    "70": (9.3047, -75.3978),
    "73": (4.4389, -75.2322),
    "76": (3.4516, -76.5320),
    "81": (7.0847, -70.7591),
    "85": (5.7589, -71.5724),
    "86": (0.5297, -76.5087),
    "88": (12.5833, -81.7000),
    "91": (3.8940, -67.0660),
    "94": (2.5700, -69.9900),
    "95": (0.3833, -70.7667),
    "97": (4.5793, -70.0420),
}

# Ajustar códigos
divipola["COD_DEPARTAMENTO"] = divipola["COD_DEPARTAMENTO"].astype(str).str.zfill(2)
divipola["COD_DANE"] = divipola["COD_DANE"].astype(str).str.zfill(5)
df["COD_DEPARTAMENTO"] = df["COD_DEPARTAMENTO"].astype(str).str.zfill(2)
df["COD_DANE"] = df["COD_DANE"].astype(str).str.zfill(5)

# =====================================================
# TRADUCIR SEXO
# =====================================================

sexo_map = {1: "Masculino", 2: "Femenino", 3: "Indeterminado"}
df["SEXO_NOMBRE"] = df["SEXO"].map(sexo_map)

# =====================================================
# LIMPIEZA BASICA
# =====================================================

df = df.dropna(subset=["MES", "SEXO_NOMBRE", "GRUPO_EDAD1"])

# =====================================================
# FUNCION ESTILO GRAFICOS
# =====================================================

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=14),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
    return fig

# =====================================================
# MAPA TIPO BUBBLE MAP (CORRECTO)
# =====================================================

muertes_departamento = (
    df.groupby("COD_DEPARTAMENTO")
    .size()
    .reset_index(name="TOTAL")
)

muertes_departamento = muertes_departamento.merge(
    divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates(),
    on="COD_DEPARTAMENTO",
    how="left"
)

# Filtrar solo departamentos con coordenadas
muertes_departamento = muertes_departamento[
    muertes_departamento["COD_DEPARTAMENTO"].isin(centroides.keys())
].copy()

# Agregar lat/lon
muertes_departamento["lat"] = muertes_departamento["COD_DEPARTAMENTO"].map(lambda x: centroides[x][0])
muertes_departamento["lon"] = muertes_departamento["COD_DEPARTAMENTO"].map(lambda x: centroides[x][1])

fig_mapa = px.scatter_mapbox(
    muertes_departamento,
    lat="lat",
    lon="lon",
    size="TOTAL",
    hover_name="DEPARTAMENTO",
    hover_data={"TOTAL": True, "lat": False, "lon": False},
    color_discrete_sequence=["#0984e3"],
    size_max=50,
    zoom=4.5,
    title="Distribución de Muertes por Departamento"
)

fig_mapa.update_layout(
    mapbox_style="carto-positron",
    margin=dict(l=20, r=20, t=60, b=20)
)

# =====================================================
# GRAFICO 1 - MUERTES POR MES
# =====================================================

meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

muertes_mes = (
    df.groupby("MES")
    .size()
    .reset_index(name="TOTAL")
)

muertes_mes["MES"] = muertes_mes["MES"].astype(int)
muertes_mes["MES_NOMBRE"] = muertes_mes["MES"].map(meses)

orden_meses = list(meses.values())

muertes_mes["MES_NOMBRE"] = pd.Categorical(
    muertes_mes["MES_NOMBRE"],
    categories=orden_meses,
    ordered=True
)

muertes_mes = muertes_mes.sort_values("MES")

fig_lineas = px.line(
    muertes_mes,
    x="MES_NOMBRE",
    y="TOTAL",
    title="Total de Muertes por Mes",
    markers=True
)
fig_lineas.update_traces(line=dict(color=PALETA[0]))
fig_lineas = style_fig(fig_lineas)

# =====================================================
# PIE CHART - 10 CIUDADES CON MENOR MORTALIDAD
# =====================================================

menor_mortalidad = (
    df.groupby("COD_DANE")
    .size()
    .reset_index(name="TOTAL")
    .sort_values(by="TOTAL", ascending=True)
    .head(10)
)

menor_mortalidad = menor_mortalidad.merge(
    divipola[["COD_DANE", "MUNICIPIO", "DEPARTAMENTO"]],
    on="COD_DANE",
    how="left"
)

colores_pie = PALETA * 2

fig_pie = px.pie(
    menor_mortalidad,
    names="MUNICIPIO",
    values="TOTAL",
    title="10 ciudades con menor mortalidad registrada",
    hole=0.5,
    color_discrete_sequence=colores_pie
)

fig_pie.update_traces(
    textinfo="label+percent",
    hoverinfo="label+percent+value",
    marker=dict(line=dict(color="white", width=2)),
    pull=[0.05] * len(menor_mortalidad),
    showlegend=False
)

fig_pie = style_fig(fig_pie)

# =====================================================
# BARRAS APILADAS - MUERTES POR SEXO Y DEPARTAMENTO
# =====================================================

sexo_departamento = (
    df.groupby(["COD_DEPARTAMENTO", "SEXO_NOMBRE"])
    .size()
    .reset_index(name="TOTAL")
)

top10_deptos = (
    sexo_departamento.groupby("COD_DEPARTAMENTO")["TOTAL"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .index
)

sexo_departamento = sexo_departamento[
    sexo_departamento["COD_DEPARTAMENTO"].isin(top10_deptos)
]

departamentos = divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates()
sexo_departamento = sexo_departamento.merge(departamentos, on="COD_DEPARTAMENTO", how="left")

fig_stack = px.bar(
    sexo_departamento,
    x="DEPARTAMENTO",
    y="TOTAL",
    color="SEXO_NOMBRE",
    barmode="stack",
    title="Muertes por Sexo y Departamento (Top 10)",
    color_discrete_map=COLORES_SEXO
)
fig_stack = style_fig(fig_stack)

# =====================================================
# TOP 5 HOMICIDIOS
# =====================================================

df["COD_MUERTE"] = df["COD_MUERTE"].astype(str).str.strip().str.upper()
homicidios = df[df["COD_MUERTE"].str.startswith("X9")]

homicidios_top = (
    homicidios.groupby("COD_DANE")
    .size()
    .reset_index(name="TOTAL")
    .sort_values(by="TOTAL", ascending=False)
    .head(5)
)

municipios = divipola[["COD_DANE", "MUNICIPIO"]].drop_duplicates()
homicidios_top = homicidios_top.merge(municipios, on="COD_DANE", how="left")

fig_homicidios = px.bar(
    homicidios_top,
    x="MUNICIPIO",
    y="TOTAL",
    title="Top 5 Ciudades con Homicidios"
)
fig_homicidios.update_traces(marker_color=PALETA[0])
fig_homicidios = style_fig(fig_homicidios)

# =====================================================
# HISTOGRAMA GRUPOS DE EDAD
# =====================================================

df["GRUPO_EDAD1"] = pd.to_numeric(df["GRUPO_EDAD1"], errors="coerce")

def clasificar_edad(codigo):
    if 0 <= codigo <= 4: return "Mortalidad neonatal"
    elif 5 <= codigo <= 6: return "Mortalidad infantil"
    elif 7 <= codigo <= 8: return "Primera infancia"
    elif 9 <= codigo <= 10: return "Niñez"
    elif codigo == 11: return "Adolescencia"
    elif 12 <= codigo <= 13: return "Juventud"
    elif 14 <= codigo <= 16: return "Adultez temprana"
    elif 17 <= codigo <= 19: return "Adultez intermedia"
    elif 20 <= codigo <= 24: return "Vejez"
    elif 25 <= codigo <= 28: return "Longevidad / Centenarios"
    elif codigo == 29: return "Edad desconocida"
    else: return "Sin clasificar"

df["CATEGORIA_EDAD"] = df["GRUPO_EDAD1"].apply(clasificar_edad)

histograma_edad = (
    df.groupby("CATEGORIA_EDAD")
    .size()
    .reset_index(name="TOTAL")
)

orden_edades = [
    "Mortalidad neonatal", "Mortalidad infantil", "Primera infancia",
    "Niñez", "Adolescencia", "Juventud", "Adultez temprana",
    "Adultez intermedia", "Vejez", "Longevidad / Centenarios",
    "Edad desconocida"
]

fig_histograma = px.bar(
    histograma_edad,
    x="CATEGORIA_EDAD",
    y="TOTAL",
    category_orders={"CATEGORIA_EDAD": orden_edades},
    title="Distribución de Mortalidad por Grupo de Edad"
)
fig_histograma.update_traces(marker_color=PALETA)
fig_histograma = style_fig(fig_histograma)

# =====================================================
# TABLA TOP CAUSAS DE MUERTE
# =====================================================

causas = (
    df.groupby("COD_MUERTE")
    .size()
    .reset_index(name="TOTAL")
    .sort_values(by="TOTAL", ascending=False)
    .head(10)
)

codigos.columns = codigos.columns.str.upper()

try:
    causas = causas.merge(
        codigos,
        left_on="COD_MUERTE",
        right_on="COD_MUERTE",
        how="left"
    )
except:
    pass

tabla_causas = dash_table.DataTable(
    data=causas.to_dict("records"),
    columns=[{"name": i, "id": i} for i in causas.columns],
    style_table={"overflowX": "auto"},
    style_cell={"textAlign": "center", "padding": "10px"},
    style_header={"fontWeight": "bold"},
    page_size=10
)

# =====================================================
# KPIs
# =====================================================

total_muertes = len(df)
total_homicidios = len(homicidios)
mes_critico = muertes_mes.sort_values(by="TOTAL", ascending=False).iloc[0]["MES"]

# =====================================================
# APP DASH
# =====================================================

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# =====================================================
# LAYOUT 2B
# =====================================================

app.layout = dbc.Container([

    html.H1("Dashboard Mortalidad Colombia 2019", className="text-center my-4"),

    # Fila 1: KPIs
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Total Muertes"), html.H2(f"{total_muertes:,}")]))),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Total Homicidios"), html.H2(f"{total_homicidios:,}")]))),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Mes Más Crítico"), html.H2(str(mes_critico))]))),
    ], className="mb-4"),

    # Fila 2: Mapa
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(figure=fig_mapa), className="graph-container"), md=12)
    ], className="mb-4"),

    # Fila 3: Pie + Línea
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(figure=fig_pie), className="graph-container"), md=6),
        dbc.Col(html.Div(dcc.Graph(figure=fig_lineas), className="graph-container"), md=6),
    ], className="mb-4"),

    # Fila 4: Sexo/Depto + Homicidios
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(figure=fig_stack), className="graph-container"), md=6),
        dbc.Col(html.Div(dcc.Graph(figure=fig_homicidios), className="graph-container"), md=6),
    ], className="mb-4"),

    # Fila 5: Histograma + Tabla
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(figure=fig_histograma), className="graph-container"), md=6),
        dbc.Col(html.Div([html.H3("Top 10 Causas de Muerte"), tabla_causas], className="graph-container"), md=6),
    ], className="mb-4"),

], fluid=True)

# =====================================================
# EJECUTAR APP
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
