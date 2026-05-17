# app.py — Dashboard Mortalidad Colombia 2019 con filtros interactivos y callbacks

```python
import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# =====================================================
# APP
# =====================================================

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# =====================================================
# PALETAS
# =====================================================

PALETA = ["#0984e3", "#00cec9", "#6c5ce7", "#fdcb6e", "#e17055"]

COLORES_SEXO = {
    "Femenino": "#ff6bcb",
    "Masculino": "#0984e3",
    "Indeterminado": "#6c5ce7"
}

# =====================================================
# CARGA DATOS
# =====================================================

print("Cargando archivos...")

# Puedes cambiar luego a CSV para mejorar rendimiento

df = pd.read_excel("data/Anexo1.NoFetal2019_CE_15-03-23.xlsx")
codigos = pd.read_excel("data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx")
divipola = pd.read_excel("data/Divipola_CE_.xlsx")

print("Archivos cargados correctamente")

# =====================================================
# LIMPIEZA
# =====================================================

sexo_map = {
    1: "Masculino",
    2: "Femenino",
    3: "Indeterminado"
}

df["SEXO_NOMBRE"] = df["SEXO"].map(sexo_map)

# Ajustar códigos

divipola["COD_DEPARTAMENTO"] = divipola["COD_DEPARTAMENTO"].astype(str).str.zfill(2)
divipola["COD_DANE"] = divipola["COD_DANE"].astype(str).str.zfill(5)

df["COD_DEPARTAMENTO"] = df["COD_DEPARTAMENTO"].astype(str).str.zfill(2)
df["COD_DANE"] = df["COD_DANE"].astype(str).str.zfill(5)

# Merge departamentos

departamentos = divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates()

df = df.merge(
    departamentos,
    on="COD_DEPARTAMENTO",
    how="left"
)

# Limpiar

df = df.dropna(subset=["MES", "SEXO_NOMBRE", "GRUPO_EDAD1"])

# =====================================================
# MESES
# =====================================================

meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

# =====================================================
# CLASIFICACION EDADES
# =====================================================


def clasificar_edad(codigo):
    try:
        codigo = int(codigo)

        if 0 <= codigo <= 4:
            return "Mortalidad neonatal"
        elif 5 <= codigo <= 6:
            return "Mortalidad infantil"
        elif 7 <= codigo <= 8:
            return "Primera infancia"
        elif 9 <= codigo <= 10:
            return "Niñez"
        elif codigo == 11:
            return "Adolescencia"
        elif 12 <= codigo <= 13:
            return "Juventud"
        elif 14 <= codigo <= 16:
            return "Adultez temprana"
        elif 17 <= codigo <= 19:
            return "Adultez intermedia"
        elif 20 <= codigo <= 24:
            return "Vejez"
        elif 25 <= codigo <= 28:
            return "Longevidad / Centenarios"
        elif codigo == 29:
            return "Edad desconocida"
        else:
            return "Sin clasificar"

    except:
        return "Sin clasificar"


# =====================================================
# EDADES
# =====================================================


df["GRUPO_EDAD1"] = pd.to_numeric(df["GRUPO_EDAD1"], errors="coerce")

df["CATEGORIA_EDAD"] = df["GRUPO_EDAD1"].apply(clasificar_edad)

# =====================================================
# MAPA
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

# =====================================================
# FUNCION ESTILO
# =====================================================


def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13),
        margin=dict(l=30, r=30, t=50, b=30)
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

    return fig

# =====================================================
# OPCIONES FILTROS
# =====================================================

opciones_departamentos = [
    {"label": d, "value": d}
    for d in sorted(df["DEPARTAMENTO"].dropna().unique())
]

opciones_sexo = [
    {"label": s, "value": s}
    for s in sorted(df["SEXO_NOMBRE"].dropna().unique())
]

# =====================================================
# LAYOUT
# =====================================================

app.layout = dbc.Container([

    html.H1(
        "Dashboard Mortalidad Colombia 2019",
        className="text-center my-4"
    ),

    # ==============================================
    # FILTROS
    # ==============================================

    dbc.Card([

        dbc.CardBody([

            dbc.Row([

                dbc.Col([
                    html.Label("Departamento"),
                    dcc.Dropdown(
                        id="filtro_departamento",
                        options=opciones_departamentos,
                        multi=True,
                        placeholder="Seleccione departamentos"
                    )
                ], md=6),

                dbc.Col([
                    html.Label("Sexo"),
                    dcc.Dropdown(
                        id="filtro_sexo",
                        options=opciones_sexo,
                        multi=True,
                        placeholder="Seleccione sexo"
                    )
                ], md=6),

            ])

        ])

    ], className="mb-4"),

    # ==============================================
    # KPIS
    # ==============================================

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Muertes"),
                    html.H2(id="kpi_total_muertes")
                ])
            ])
        ], md=4),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Homicidios"),
                    html.H2(id="kpi_homicidios")
                ])
            ])
        ], md=4),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Mes Más Crítico"),
                    html.H2(id="kpi_mes")
                ])
            ])
        ], md=4),

    ], className="mb-4"),

    # ==============================================
    # MAPA
    # ==============================================

    dbc.Row([
        dbc.Col([
            dcc.Graph(id="grafico_mapa")
        ], md=12)
    ]),

    # ==============================================
    # GRAFICOS
    # ==============================================

    dbc.Row([

        dbc.Col([
            dcc.Graph(id="grafico_lineas")
        ], md=6),

        dbc.Col([
            dcc.Graph(id="grafico_pie")
        ], md=6),

    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id="grafico_stack")
        ], md=6),

        dbc.Col([
            dcc.Graph(id="grafico_homicidios")
        ], md=6),

    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id="grafico_histograma")
        ], md=6),

        dbc.Col([
            html.H4("Top 10 Causas de Muerte"),
            dash_table.DataTable(
                id="tabla_causas",
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "center",
                    "padding": "8px"
                },
                style_header={
                    "fontWeight": "bold"
                },
                page_size=10
            )
        ], md=6),

    ])

], fluid=True)

# =====================================================
# CALLBACK PRINCIPAL
# =====================================================

@app.callback(
    [
        Output("kpi_total_muertes", "children"),
        Output("kpi_homicidios", "children"),
        Output("kpi_mes", "children"),
        Output("grafico_mapa", "figure"),
        Output("grafico_lineas", "figure"),
        Output("grafico_pie", "figure"),
        Output("grafico_stack", "figure"),
        Output("grafico_homicidios", "figure"),
        Output("grafico_histograma", "figure"),
        Output("tabla_causas", "data"),
        Output("tabla_causas", "columns")
    ],
    [
        Input("filtro_departamento", "value"),
        Input("filtro_sexo", "value")
    ]
)
def actualizar_dashboard(departamentos_seleccionados, sexo_seleccionado):

    dff = df.copy()

    # ==========================================
    # FILTROS
    # ==========================================

    if departamentos_seleccionados:
        dff = dff[
            dff["DEPARTAMENTO"].isin(departamentos_seleccionados)
        ]

    if sexo_seleccionado:
        dff = dff[
            dff["SEXO_NOMBRE"].isin(sexo_seleccionado)
        ]

    # ==========================================
    # KPIS
    # ==========================================

    total_muertes = len(dff)

    homicidios = dff[
        dff["COD_MUERTE"].astype(str).str.startswith("X9")
    ]

    total_homicidios = len(homicidios)

    muertes_mes = (
        dff.groupby("MES")
        .size()
        .reset_index(name="TOTAL")
    )

    if len(muertes_mes) > 0:

        muertes_mes["MES_NOMBRE"] = muertes_mes["MES"].map(meses)

        mes_critico = (
            muertes_mes
            .sort_values(by="TOTAL", ascending=False)
            .iloc[0]["MES_NOMBRE"]
        )

    else:
        mes_critico = "Sin datos"

    # ==========================================
    # MAPA
    # ==========================================

    muertes_departamento = (
        dff.groupby("COD_DEPARTAMENTO")
        .size()
        .reset_index(name="TOTAL")
    )

    muertes_departamento = muertes_departamento.merge(
        departamentos,
        on="COD_DEPARTAMENTO",
        how="left"
    )

    muertes_departamento = muertes_departamento[
        muertes_departamento["COD_DEPARTAMENTO"].isin(centroides.keys())
    ]

    muertes_departamento["lat"] = muertes_departamento[
        "COD_DEPARTAMENTO"
    ].map(lambda x: centroides[x][0])

    muertes_departamento["lon"] = muertes_departamento[
        "COD_DEPARTAMENTO"
    ].map(lambda x: centroides[x][1])

    fig_mapa = px.scatter_mapbox(
        muertes_departamento,
        lat="lat",
        lon="lon",
        size="TOTAL",
        hover_name="DEPARTAMENTO",
        hover_data={"TOTAL": True},
        size_max=45,
        zoom=4.5,
        title="Distribución de Muertes por Departamento",
        color_discrete_sequence=["#0984e3"]
    )

    fig_mapa.update_layout(
        mapbox_style="carto-positron"
    )

    # ==========================================
    # LINEAS
    # ==========================================

    muertes_mes["MES_NOMBRE"] = pd.Categorical(
        muertes_mes["MES_NOMBRE"],
        categories=list(meses.values()),
        ordered=True
    )

    muertes_mes = muertes_mes.sort_values("MES")

    fig_lineas = px.line(
        muertes_mes,
        x="MES_NOMBRE",
        y="TOTAL",
        markers=True,
        title="Muertes por Mes"
    )

    fig_lineas.update_traces(
        line=dict(color=PALETA[0])
    )

    fig_lineas = style_fig(fig_lineas)

    # ==========================================
    # PIE
    # ==========================================

    menor_mortalidad = (
        dff.groupby("COD_DANE")
        .size()
        .reset_index(name="TOTAL")
        .sort_values(by="TOTAL", ascending=True)
        .head(10)
    )

    menor_mortalidad = menor_mortalidad.merge(
        divipola[["COD_DANE", "MUNICIPIO"]],
        on="COD_DANE",
        how="left"
    )

    fig_pie = px.pie(
        menor_mortalidad,
        names="MUNICIPIO",
        values="TOTAL",
        title="10 Ciudades con Menor Mortalidad",
        hole=0.5,
        color_discrete_sequence=PALETA * 2
    )

    fig_pie = style_fig(fig_pie)

    # ==========================================
    # STACK
    # ==========================================

    sexo_departamento = (
        dff.groupby(["DEPARTAMENTO", "SEXO_NOMBRE"])
        .size()
        .reset_index(name="TOTAL")
    )

    fig_stack = px.bar(
        sexo_departamento,
        x="DEPARTAMENTO",
        y="TOTAL",
        color="SEXO_NOMBRE",
        barmode="stack",
        title="Muertes por Sexo y Departamento",
        color_discrete_map=COLORES_SEXO
    )

    fig_stack = style_fig(fig_stack)

    # ==========================================
    # HOMICIDIOS
    # ==========================================

    homicidios_top = (
        homicidios.groupby("COD_DANE")
        .size()
        .reset_index(name="TOTAL")
        .sort_values(by="TOTAL", ascending=False)
        .head(5)
    )

    homicidios_top = homicidios_top.merge(
        divipola[["COD_DANE", "MUNICIPIO"]],
        on="COD_DANE",
        how="left"
    )

    fig_homicidios = px.bar(
        homicidios_top,
        x="MUNICIPIO",
        y="TOTAL",
        title="Top 5 Ciudades con Homicidios"
    )

    fig_homicidios.update_traces(
        marker_color=PALETA[0]
    )

    fig_homicidios = style_fig(fig_homicidios)

    # ==========================================
    # HISTOGRAMA
    # ==========================================

    histograma_edad = (
        dff.groupby("CATEGORIA_EDAD")
        .size()
        .reset_index(name="TOTAL")
    )

    orden_edades = [
        "Mortalidad neonatal",
        "Mortalidad infantil",
        "Primera infancia",
        "Niñez",
        "Adolescencia",
        "Juventud",
        "Adultez temprana",
        "Adultez intermedia",
        "Vejez",
        "Longevidad / Centenarios",
        "Edad desconocida"
    ]

    fig_histograma = px.bar(
        histograma_edad,
        x="CATEGORIA_EDAD",
        y="TOTAL",
        category_orders={"CATEGORIA_EDAD": orden_edades},
        title="Distribución por Grupo de Edad"
    )

    fig_histograma.update_traces(
        marker_color=PALETA
    )

    fig_histograma = style_fig(fig_histograma)

    # ==========================================
    # TABLA
    # ==========================================

    causas = (
        dff.groupby("COD_MUERTE")
        .size()
        .reset_index(name="TOTAL")
        .sort_values(by="TOTAL", ascending=False)
        .head(10)
    )

    codigos.columns = codigos.columns.str.upper()

    try:
        causas = causas.merge(
            codigos,
            on="COD_MUERTE",
            how="left"
        )
    except:
        pass

    columnas = [
        {"name": col, "id": col}
        for col in causas.columns
    ]

    # ==========================================
    # RETURN
    # ==========================================

    return (
        f"{total_muertes:,}",
        f"{total_homicidios:,}",
        mes_critico,
        fig_mapa,
        fig_lineas,
        fig_pie,
        fig_stack,
        fig_homicidios,
        fig_histograma,
        causas.to_dict("records"),
        columnas
    )

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)