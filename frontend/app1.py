
# -*- coding: utf-8 -*-
"""
Dashboard Streamlit - Sistema de Pronóstico de Inundaciones - Tumbes

Frontend:
    E:\tumbes_262\frontend\app.py

Datos IMERG:
    E:\tumbes_262\backend\data

Precipitación areal:
    E:\tumbes_262\backend\data_lluvia\YYYY-MM-DD\IMERG_TUMBES_AREAL_YYYYMMDD.csv
"""

from pathlib import Path
from datetime import datetime
import re
import io

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Dependencias espaciales
try:
    import rasterio
    import geopandas as gpd
    from shapely.geometry import mapping
    SPATIAL_OK = True
except Exception:
    SPATIAL_OK = False


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

DATA_IMERG = BACKEND / "data"
DATA_LLUVIA = BACKEND / "data_lluvia"
DATA_ESPACIAL = BACKEND / "data_espacial" / "shp"

CUENCA_SHP = DATA_ESPACIAL / "tumbes_cuenca.shp"
RIO_SHP = DATA_ESPACIAL / "river_tumbes.shp"
HYDRO_SHP = DATA_ESPACIAL / "hydro.shp"

# Imagen de cabecera: si existe se utiliza automáticamente.
HEADER_CANDIDATES = [
    BACKEND / "foto" / "primero.png",
    BACKEND / "foto" / "tumbes.png",
    BACKEND / "foto" / "header.png",
]

st.set_page_config(
    page_title="Sistema de Pronóstico de Inundaciones - Tumbes",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #071827;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 0.8rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, p, label {
        color: #ffffff !important;
    }

    .section-title {
        color: white;
        font-size: 25px;
        font-weight: 800;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    .panel {
        background: #102638;
        border: 1px solid #29445a;
        border-radius: 14px;
        padding: 12px;
    }

    .metric-box {
        background: #173247;
        border-radius: 12px;
        padding: 12px 16px;
        border: 1px solid #2b4b61;
        min-height: 95px;
    }

    .metric-label {
        color: #b9cad6;
        font-size: 14px;
    }

    .metric-value {
        color: white;
        font-size: 27px;
        font-weight: 700;
    }

    .metric-sub {
        color: #91aabb;
        font-size: 12px;
    }

    div.stButton > button {
        border-radius: 9px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def encontrar_header():
    for p in HEADER_CANDIDATES:
        if p.exists():
            return p
    return None


def obtener_fecha_hoy():
    return datetime.now()


def leer_csv_robusto(path):
    """
    Lee el CSV real generado por el proceso de precipitación areal.

    Ejemplo real:
        fecha,PP_areal,n_pixeles
        2026-10-18 19:00,0.0192045444,44

    Se acepta coma, punto y coma y distintas codificaciones.
    """
    errores = []

    for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
        for sep in [",", ";", "\t"]:
            try:
                df = pd.read_csv(
                    path,
                    sep=sep,
                    encoding=encoding,
                    engine="python",
                )

                df.columns = [
                    str(c).replace("\ufeff", "").strip()
                    for c in df.columns
                ]

                # Si el separador fue incorrecto, normalmente queda una
                # sola columna con todo el encabezado.
                if len(df.columns) == 1 and "," in str(df.columns[0]):
                    continue

                if "fecha" not in df.columns:
                    # Buscar columna ignorando mayúsculas/minúsculas.
                    mapa = {str(c).strip().lower(): c for c in df.columns}
                    if "fecha" in mapa:
                        df = df.rename(columns={mapa["fecha"]: "fecha"})

                if "pp_areal" not in df.columns:
                    mapa = {str(c).strip().lower(): c for c in df.columns}
                    if "pp_areal" in mapa:
                        df = df.rename(columns={mapa["pp_areal"]: "PP_areal"})

                if "fecha" not in df.columns:
                    errores.append(f"{sep=} {encoding=}: falta columna fecha")
                    continue

                if "PP_areal" not in df.columns:
                    # Intento adicional por posición.
                    candidatos = [
                        c for c in df.columns
                        if "pp" in str(c).lower()
                        or "areal" in str(c).lower()
                    ]
                    if candidatos:
                        df = df.rename(columns={candidatos[0]: "PP_areal"})
                    else:
                        errores.append(
                            f"{sep=} {encoding=}: falta columna PP_areal"
                        )
                        continue

                df["fecha"] = pd.to_datetime(
                    df["fecha"],
                    errors="coerce",
                    dayfirst=False,
                )

                df["PP_areal"] = pd.to_numeric(
                    df["PP_areal"],
                    errors="coerce",
                )

                df = df.dropna(subset=["fecha"]).copy()
                df["PP_areal"] = df["PP_areal"].fillna(0).clip(lower=0)
                df = df.sort_values("fecha").reset_index(drop=True)

                if len(df) > 0:
                    return df

            except Exception as e:
                errores.append(str(e))

    raise ValueError(
        "No fue posible leer el CSV. "
        + " | ".join(errores[-4:])
    )


def buscar_csv_areal():
    """
    Busca el CSV siguiendo la estructura REAL:

        data_lluvia/
            2026-10-26/
                IMERG_TUMBES_AREAL_20261026.csv

    No depende de una única fecha.
    Primero busca el día actual y después busca el archivo más reciente
    disponible recursivamente.
    """

    # --------------------------------------------------------
    # 1. Buscar carpeta del día actual
    # --------------------------------------------------------
    hoy = datetime.now()
    fecha_dir = hoy.strftime("%Y-%m-%d")
    fecha_file = hoy.strftime("%Y%m%d")

    carpeta_hoy = DATA_LLUVIA / fecha_dir
    archivo_hoy = carpeta_hoy / f"IMERG_TUMBES_AREAL_{fecha_file}.csv"

    if archivo_hoy.is_file():
        return archivo_hoy

    # --------------------------------------------------------
    # 2. Buscar dentro de la carpeta del día actual ignorando
    #    mayúsculas y posibles pequeñas diferencias del nombre.
    # --------------------------------------------------------
    if carpeta_hoy.is_dir():
        candidatos_hoy = [
            p for p in carpeta_hoy.iterdir()
            if p.is_file()
            and p.suffix.lower() == ".csv"
            and "imerg" in p.name.lower()
            and "areal" in p.name.lower()
        ]

        if candidatos_hoy:
            candidatos_hoy.sort(
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            return candidatos_hoy[0]

    # --------------------------------------------------------
    # 3. Buscar recursivamente todos los IMERG areal.
    # --------------------------------------------------------
    candidatos = []

    if DATA_LLUVIA.exists():
        for p in DATA_LLUVIA.rglob("*.csv"):
            if not p.is_file():
                continue

            nombre = p.name.lower()

            if "imerg" not in nombre:
                continue

            if "areal" not in nombre:
                continue

            if "estaciones" in nombre:
                continue

            candidatos.append(p)

    if not candidatos:
        return None

    # --------------------------------------------------------
    # 4. Intentar ordenar por fecha YYYYMMDD del nombre.
    #    Si no existe, usar fecha de modificación.
    # --------------------------------------------------------
    def clave(p):
        m = re.search(r"(\d{8})", p.stem)
        if m:
            try:
                return datetime.strptime(m.group(1), "%Y%m%d")
            except Exception:
                pass
        return datetime.fromtimestamp(p.stat().st_mtime)

    candidatos.sort(key=clave, reverse=True)

    return candidatos[0]


def cargar_precipitacion_areal():
    archivo = buscar_csv_areal()

    if archivo is None:
        st.error(
            "No se encontró el CSV de precipitación areal.\n\n"
            f"Se buscó recursivamente en:\n{DATA_LLUVIA}\n\n"
            "Estructura esperada:\n"
            "YYYY-MM-DD/IMERG_TUMBES_AREAL_YYYYMMDD.csv"
        )
        return None, None

    try:
        df = leer_csv_robusto(archivo)
    except Exception as e:
        st.error(
            f"Se encontró el archivo, pero no se pudo leer:\n\n"
            f"{archivo}\n\n"
            f"Error: {e}"
        )
        return None, archivo

    return df, archivo


def ultimas_48_horas(df):
    if df is None or df.empty:
        return df

    df = df.sort_values("fecha").copy()

    # Si el archivo contiene muchas semanas, las últimas 48 horas
    # corresponden a las 48 observaciones horarias más recientes.
    return df.tail(48).copy()


# ============================================================
# SHAPEFILES
# ============================================================

@st.cache_data(show_spinner=False)
def cargar_shapes():
    if not SPATIAL_OK:
        return None, None, None

    def cargar(path):
        if not path.exists():
            return None

        try:
            gdf = gpd.read_file(path)

            if gdf.empty:
                return None

            if gdf.crs is None:
                # Se asume WGS84 si el archivo no tiene CRS definido.
                gdf = gdf.set_crs("EPSG:4326", allow_override=True)
            else:
                gdf = gdf.to_crs("EPSG:4326")

            return gdf
        except Exception:
            return None

    return (
        cargar(CUENCA_SHP),
        cargar(RIO_SHP),
        cargar(HYDRO_SHP),
    )


def extraer_nombre_estacion(row):
    posibles = [
        "nombre",
        "NOMBRE",
        "name",
        "NAME",
        "estacion",
        "ESTACION",
        "station",
        "STATION",
    ]

    for c in posibles:
        if c in row.index:
            valor = row[c]
            if pd.notna(valor):
                return str(valor)

    return ""


# ============================================================
# MAPA IMERG
# ============================================================

def obtener_rasters_48h():
    """
    Busca rasters IMERG por las carpetas diarias.

    Formato esperado:
        data/YYYY-MM-DD/IMERG_YYYYMMDD_HHMM.tif
    """
    if not DATA_IMERG.exists():
        return []

    archivos = []

    for p in DATA_IMERG.rglob("*.tif"):
        if not p.is_file():
            continue

        if "IMERG" not in p.name.upper():
            continue

        m = re.search(
            r"IMERG_(\d{8})_(\d{2})(\d{2})",
            p.stem,
            re.IGNORECASE,
        )

        if m:
            try:
                fecha = datetime.strptime(
                    m.group(1) + m.group(2) + m.group(3),
                    "%Y%m%d%H%M",
                )
                archivos.append((fecha, p))
            except Exception:
                pass

    if not archivos:
        return []

    archivos.sort(key=lambda x: x[0])

    return archivos[-48:]


@st.cache_data(show_spinner=False)
def leer_raster(path_str):
    if not SPATIAL_OK:
        return None

    try:
        with rasterio.open(path_str) as src:
            data = src.read(1).astype(float)
            bounds = src.bounds
            transform = src.transform

            nodata = src.nodata

            if nodata is not None:
                data[data == nodata] = np.nan

            data[~np.isfinite(data)] = np.nan
            data[data < 0] = 0

            return {
                "data": data,
                "bounds": bounds,
                "transform": transform,
            }
    except Exception:
        return None


def aplicar_mascara_cuenca(data, transform, cuenca):
    """
    Deja visible únicamente la precipitación dentro de la cuenca.
    """
    if cuenca is None:
        return data

    try:
        from rasterio.features import geometry_mask

        geometrias = [
            mapping(g)
            for g in cuenca.geometry
            if g is not None and not g.is_empty
        ]

        if not geometrias:
            return data

        mask = geometry_mask(
            geometrias,
            out_shape=data.shape,
            transform=transform,
            invert=True,
        )

        salida = data.copy()
        salida[~mask] = np.nan

        return salida

    except Exception:
        return data


def crear_figura_mapa_lluvia():
    if not SPATIAL_OK:
        return None, "Faltan rasterio/geopandas."

    registros = obtener_rasters_48h()

    if not registros:
        return None, (
            f"No se encontraron rasters IMERG en:\n{DATA_IMERG}"
        )

    cuenca, rio, hydro = cargar_shapes()

    frames = []
    primer_raster = None

    # --------------------------------------------------------
    # Cargar todos los rasters
    # --------------------------------------------------------
    for fecha, path in registros:
        r = leer_raster(str(path))

        if r is None:
            continue

        data = r["data"]

        data = aplicar_mascara_cuenca(
            data,
            r["transform"],
            cuenca,
        )

        if primer_raster is None:
            primer_raster = {
                "fecha": fecha,
                "path": path,
                "data": data,
                "bounds": r["bounds"],
            }

        frames.append(
            {
                "fecha": fecha,
                "data": data,
                "bounds": r["bounds"],
            }
        )

    if not frames:
        return None, "No fue posible leer los rasters IMERG."

    # --------------------------------------------------------
    # Extensión del mapa: cuenca
    # --------------------------------------------------------
    if cuenca is not None:
        minx, miny, maxx, maxy = cuenca.total_bounds
    else:
        b = frames[0]["bounds"]
        minx, miny, maxx, maxy = b.left, b.bottom, b.right, b.top

    # Margen pequeño
    dx = (maxx - minx) * 0.04
    dy = (maxy - miny) * 0.04

    map_xmin = minx - dx
    map_xmax = maxx + dx
    map_ymin = miny - dy
    map_ymax = maxy + dy

    # --------------------------------------------------------
    # Escala fija de 10 intervalos
    # --------------------------------------------------------
    colores = [
        "#FFFFFF",  # sin lluvia
        "#E6F7FF",
        "#BDEFFF",
        "#7DD3FC",
        "#38BDF8",
        "#1683FF",
        "#00B050",
        "#FFE600",
        "#FF8C00",
        "#FF0000",
        "#990000",
    ]

    zmax = 20.0
    zmin = 0.0

    # Escala discreta de 0-20 mm.
    # IMPORTANTE: Plotly exige que los valores de colorscale
    # estén NORMALIZADOS entre 0 y 1, no en mm directamente.
    # Los niveles físicos siguen siendo 0, 0.1, 0.5, 1, 2,
    # 4, 6, 10, 15 y 20 mm.
    niveles_mm = [0.00, 0.0001, 0.10, 0.50, 1.00, 2.00,
                  4.00, 6.00, 10.00, 15.00, 20.00]

    escala = [
        [nivel / zmax, color]
        for nivel, color in zip(niveles_mm, colores)
    ]

    fig = go.Figure()

    # --------------------------------------------------------
    # Primer raster
    # --------------------------------------------------------
    f0 = frames[0]
    data0 = f0["data"]
    bounds0 = f0["bounds"]

    height, width = data0.shape

    x = np.linspace(
        bounds0.left,
        bounds0.right,
        width,
    )

    y = np.linspace(
        bounds0.bottom,
        bounds0.top,
        height,
    )

    fig.add_trace(
        go.Heatmap(
            z=data0,
            x=x,
            y=y,
            zmin=zmin,
            zmax=zmax,
            colorscale=escala,
            colorbar=dict(
                title=dict(
                    text="Lluvia<br>(mm)",
                    side="top",
                ),
                tickmode="array",
                tickvals=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
                ticktext=[
                    "0",
                    "2",
                    "4",
                    "6",
                    "8",
                    "10",
                    "12",
                    "14",
                    "16",
                    "18",
                    "20",
                ],
                len=0.72,
                thickness=18,
                x=1.015,
                y=0.48,
            ),
            hovertemplate=(
                "Precipitación: %{z:.2f} mm"
                "<extra></extra>"
            ),
            showscale=True,
        )
    )

    # --------------------------------------------------------
    # Función para añadir shapes a la figura
    # --------------------------------------------------------
    def agregar_gdf(gdf, line_color, line_width, fill_color=None):
        if gdf is None:
            return

        for geom in gdf.geometry:
            if geom is None or geom.is_empty:
                continue

            geoms = [geom]
            if hasattr(geom, "geoms"):
                geoms = list(geom.geoms)

            for g in geoms:
                if g.geom_type == "Polygon":
                    xs, ys = g.exterior.xy
                    fig.add_trace(
                        go.Scatter(
                            x=list(xs),
                            y=list(ys),
                            mode="lines",
                            line=dict(
                                color=line_color,
                                width=line_width,
                            ),
                            fill=(
                                "toself"
                                if fill_color is not None
                                else None
                            ),
                            fillcolor=fill_color,
                            hoverinfo="skip",
                            showlegend=False,
                        )
                    )

                elif g.geom_type == "LineString":
                    xs, ys = g.xy
                    fig.add_trace(
                        go.Scatter(
                            x=list(xs),
                            y=list(ys),
                            mode="lines",
                            line=dict(
                                color=line_color,
                                width=line_width,
                            ),
                            hoverinfo="skip",
                            showlegend=False,
                        )
                    )

    # Cuenca: borde oscuro
    agregar_gdf(
        cuenca,
        "#10202F",
        3.2,
        None,
    )

    # Río
    agregar_gdf(
        rio,
        "#00C9FF",
        2.0,
        None,
    )

    # Estaciones
    if hydro is not None:
        lons = []
        lats = []
        nombres = []

        for _, row in hydro.iterrows():
            geom = row.geometry

            if geom is None or geom.is_empty:
                continue

            if geom.geom_type == "Point":
                lons.append(geom.x)
                lats.append(geom.y)
                nombres.append(extraer_nombre_estacion(row))

        if lons:
            fig.add_trace(
                go.Scatter(
                    x=lons,
                    y=lats,
                    mode="markers+text",
                    marker=dict(
                        size=8,
                        color="white",
                        line=dict(
                            color="#008ED6",
                            width=2,
                        ),
                    ),
                    text=nombres,
                    textposition="top center",
                    textfont=dict(
                        size=10,
                        color="#15364A",
                    ),
                    hovertemplate=(
                        "%{text}<extra></extra>"
                    ),
                    showlegend=False,
                )
            )

    # --------------------------------------------------------
    # Frames de animación
    # --------------------------------------------------------
    plot_frames = []

    for i, f in enumerate(frames):
        d = f["data"]
        b = f["bounds"]

        h, w = d.shape

        xx = np.linspace(
            b.left,
            b.right,
            w,
        )

        yy = np.linspace(
            b.bottom,
            b.top,
            h,
        )

        plot_frames.append(
            go.Frame(
                name=str(i),
                data=[
                    go.Heatmap(
                        z=d,
                        x=xx,
                        y=yy,
                        zmin=zmin,
                        zmax=zmax,
                        colorscale=escala,
                        hovertemplate=(
                            "Precipitación: %{z:.2f} mm"
                            "<extra></extra>"
                        ),
                        showscale=True,
                        colorbar=dict(
                            title=dict(
                                text="Lluvia<br>(mm)",
                                side="top",
                            ),
                            tickmode="array",
                            tickvals=[
                                0, 2, 4, 6, 8,
                                10, 12, 14, 16,
                                18, 20
                            ],
                            ticktext=[
                                "0", "2", "4", "6",
                                "8", "10", "12",
                                "14", "16", "18",
                                "20"
                            ],
                            len=0.72,
                            thickness=18,
                            x=1.015,
                            y=0.48,
                        ),
                    )
                ],
                traces=[0],
                layout=go.Layout(
                    title=dict(
                        text=(
                            "IMERG Early | "
                            + f["fecha"].strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            + " | Últimas 48 horas"
                        )
                    )
                ),
            )
        )

    fig.frames = plot_frames

    # --------------------------------------------------------
    # Controles
    # --------------------------------------------------------
    fig.update_layout(
        title=dict(
            text=(
                "IMERG Early | "
                + f0["fecha"].strftime(
                    "%d/%m/%Y %H:%M"
                )
                + " | Últimas 48 horas"
            ),
            x=0.0,
            xanchor="left",
            y=0.97,
            font=dict(
                size=20,
                color="#10202F",
            ),
        ),

        # Sin longitud/latitud
        xaxis=dict(
            visible=False,
            range=[map_xmin, map_xmax],
            fixedrange=True,
        ),

        yaxis=dict(
            visible=False,
            range=[map_ymin, map_ymax],
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1,
        ),

        margin=dict(
            l=5,
            r=70,
            t=78,
            b=15,
        ),

        height=650,

        plot_bgcolor="white",
        paper_bgcolor="white",

        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.72,
                y=1.13,
                xanchor="left",
                yanchor="top",
                buttons=[
                    dict(
                        label="Reproducir",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {
                                    "duration": 650,
                                    "redraw": True,
                                },
                                "transition": {
                                    "duration": 250
                                },
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    ),
                    dict(
                        label="Pausar",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {
                                    "duration": 0,
                                    "redraw": False,
                                },
                                "mode": "immediate",
                            },
                        ],
                    ),
                ],
            )
        ],

        sliders=[
            dict(
                active=0,
                x=0.08,
                y=1.075,
                len=0.82,
                xanchor="left",
                yanchor="top",
                currentvalue=dict(
                    prefix="Hora: ",
                    visible=True,
                    xanchor="center",
                ),
                transition=dict(
                    duration=250,
                    easing="linear",
                ),
                steps=[
                    dict(
                        label=f["fecha"].strftime(
                            "%d/%m %H:%M"
                        ),
                        method="animate",
                        args=[
                            [str(i)],
                            {
                                "frame": {
                                    "duration": 250,
                                    "redraw": True,
                                },
                                "transition": {
                                    "duration": 150
                                },
                                "mode": "immediate",
                            },
                        ],
                    )
                    for i, f in enumerate(frames)
                ],
            )
        ],
    )

    return fig, None


# ============================================================
# CABECERA
# ============================================================

header = encontrar_header()

if header is not None:
    try:
        st.image(
            str(header),
            use_container_width=True,
        )
    except Exception:
        pass

st.markdown(
    """
    <div style="
        margin-top:-155px;
        position:relative;
        padding:20px 30px 65px 30px;
        color:white;
    ">
        <div style="font-size:18px;">Sistema de</div>
        <div style="
            font-size:30px;
            font-weight:800;
            line-height:1.05;
        ">
            Sistema de Pronóstico de<br>
            Inundaciones - Tumbes
        </div>
        <div style="font-size:15px;">
            Cuenca del río Tumbes
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="height:30px;"></div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 1. PRECIPITACIÓN IMERG
# ============================================================

st.markdown(
    '<div class="section-title">1. Precipitación (IMERG Early)</div>',
    unsafe_allow_html=True,
)

fig_mapa, error_mapa = crear_figura_mapa_lluvia()

# Datos areales
df_areal, archivo_areal = cargar_precipitacion_areal()

col_mapa, col_grafico = st.columns(
    [1.65, 1.0],
    gap="medium",
)

with col_mapa:
    if fig_mapa is not None:
        st.plotly_chart(
            fig_mapa,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": False,
            },
        )
    else:
        st.error(error_mapa)

with col_grafico:
    st.markdown(
        """
        <div style="
            color:white;
            font-size:19px;
            font-weight:800;
            margin-bottom:8px;
        ">
            Precipitación areal
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df_areal is not None:
        df48 = ultimas_48_horas(df_areal)

        fig_bar = go.Figure()

        # Color progresivo por intensidad
        valores = df48["PP_areal"].to_numpy()

        def color_lluvia(v):
            if v <= 0:
                return "#F2F2F2"
            if v < 0.1:
                return "#DDF4FF"
            if v < 0.5:
                return "#A7E3FF"
            if v < 1:
                return "#4FC3F7"
            if v < 2:
                return "#1683FF"
            if v < 4:
                return "#00B050"
            if v < 6:
                return "#B7D334"
            if v < 10:
                return "#FFE600"
            if v < 15:
                return "#FF8C00"
            return "#E00000"

        colores_barra = [
            color_lluvia(float(v))
            for v in valores
        ]

        fig_bar.add_trace(
            go.Bar(
                x=df48["fecha"],
                y=df48["PP_areal"],
                marker=dict(
                    color=colores_barra,
                    line=dict(
                        width=0.25,
                        color="#FFFFFF",
                    ),
                ),
                hovertemplate=(
                    "<b>%{x|%d/%m/%Y %H:%M}</b><br>"
                    "Precipitación areal: "
                    "<b>%{y:.2f} mm</b>"
                    "<extra></extra>"
                ),
            )
        )

        acumulado = float(
            df48["PP_areal"].sum()
        )

        maximo = float(
            df48["PP_areal"].max()
        )

        fecha_max = df48.loc[
            df48["PP_areal"].idxmax(),
            "fecha"
        ]

        fig_bar.update_layout(
            height=650,
            margin=dict(
                l=55,
                r=10,
                t=25,
                b=55,
            ),
            paper_bgcolor="#102638",
            plot_bgcolor="#102638",
            font=dict(
                color="white",
            ),
            xaxis=dict(
                title="Fecha",
                tickformat="%d/%m\n%H:%M",
                gridcolor="#29445A",
                zeroline=False,
            ),
            yaxis=dict(
                title="Precipitación areal (mm)",
                gridcolor="#29445A",
                zeroline=False,
            ),
            bargap=0.08,
            showlegend=False,
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            config={
                "displaylogo": False,
            },
        )



# ============================================================
# 2. PRONÓSTICO DE CAUDAL
# ============================================================

st.markdown(
    '<div class="section-title">2. Pronóstico de caudal — 72 horas</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

for col, nombre in zip(
    [c1, c2, c3],
    ["El Tigre", "Cabo Inga", "Puente Tumbes"],
):
    with col:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">
                    {nombre}
                </div>
                <div class="metric-value">
                    --
                </div>
                <div class="metric-sub">
                    Máx. 72 h: --
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Placeholder limpio para conectar posteriormente el modelo IA.
fig_caudal = go.Figure()

fig_caudal.update_layout(
    height=380,
    paper_bgcolor="#102638",
    plot_bgcolor="#102638",
    font=dict(color="white"),
    margin=dict(l=50, r=20, t=20, b=50),
    xaxis=dict(
        title="Horas",
        gridcolor="#29445A",
    ),
    yaxis=dict(
        title="Caudal (m³/s)",
        gridcolor="#29445A",
    ),
)

st.plotly_chart(
    fig_caudal,
    use_container_width=True,
)


# ============================================================
# 3. ÁREAS DE INUNDACIÓN
# ============================================================

st.markdown(
    '<div class="section-title">3. Áreas de inundación</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="panel" style="
        height:430px;
        display:flex;
        align-items:center;
        justify-content:center;
        color:#91AABB;
        font-size:18px;
    ">
        Mapa de áreas de inundación
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 4. IMPACTOS
# ============================================================

st.markdown(
    '<div class="section-title">4. Impactos esperados</div>',
    unsafe_allow_html=True,
)

impactos = [
    ("Población", "--", "personas"),
    ("Viviendas", "--", "viviendas"),
    ("Carreteras", "--", "km afectados"),
    ("Salud", "--", "establecimientos"),
    ("Colegios", "--", "instituciones"),
    ("Área agrícola", "--", "hectáreas"),
]

cols = st.columns(6)

for col, (titulo, valor, unidad) in zip(cols, impactos):
    with col:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">
                    {titulo}
                </div>
                <div class="metric-value">
                    {valor}
                </div>
                <div class="metric-sub">
                    {unidad}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div style="height:25px;"></div>
    <div class="panel" style="
        height:430px;
        display:flex;
        align-items:center;
        justify-content:center;
        color:#91AABB;
        font-size:18px;
    ">
        Mapa de impactos potenciales
    </div>
    """,
    unsafe_allow_html=True,
)

