# ============================================================
# EXTRAER PRECIPITACIÓN AREAL DE LA CUENCA DE TUMBES
# DESDE RASTER IMERG GEOTIFF
#
# PARA CADA RASTER HORARIO:
#   1. Lee el raster
#   2. Lee tumbes_cuenca.shp
#   3. Reproyecta la cuenca al CRS del raster
#   4. Obtiene los píxeles dentro de la cuenca
#   5. Calcula la precipitación media areal
#
# SALIDA:
#
# E:\tumbes_262\backend\data_lluvia\
#     2026-10-26\
#         IMERG_TUMBES_AREAL_20261026.csv
#
# CSV:
#
# fecha,PP_areal
# 2026-10-26 00:00,0.1234
# 2026-10-26 01:00,0.5678
# ...
#
# ============================================================


import os
import glob
import numpy as np
import pandas as pd
import rasterio

from rasterio.mask import mask
from rasterio.warp import transform_geom

import geopandas as gpd

from shapely.geometry import mapping

from pathlib import Path
from datetime import datetime


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

# Carpeta donde están los raster IMERG
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = str(BASE_DIR / "backend" / "data")

# Shapefile de la cuenca
BASIN_SHP = str(BASE_DIR / "backend" / "data_espacial" / "shp" / "tumbes_cuenca.shp")

# Carpeta base de salida
OUTPUT_BASE_DIR = str(BASE_DIR / "backend" / "data_lluvia")


# ============================================================
# 2. FECHA DE EJECUCIÓN
# ============================================================

execution_date = datetime.now().strftime(
    "%Y-%m-%d"
)


# ============================================================
# 3. CARPETA DE SALIDA
# ============================================================

OUTPUT_DIR = os.path.join(
    OUTPUT_BASE_DIR,
    execution_date
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# 4. MOSTRAR CONFIGURACIÓN
# ============================================================

print()
print("=" * 80)
print("EXTRACCIÓN DE PRECIPITACIÓN AREAL - CUENCA DE TUMBES")
print("=" * 80)

print()
print("CARPETA DE RASTER:")
print(INPUT_DIR)

print()
print("SHAPEFILE DE LA CUENCA:")
print(BASIN_SHP)

print()
print("CARPETA DE SALIDA:")
print(OUTPUT_DIR)


# ============================================================
# 5. VALIDAR SHAPEFILE
# ============================================================

if not os.path.exists(BASIN_SHP):

    raise FileNotFoundError(
        "NO SE ENCONTRÓ EL SHAPEFILE DE LA CUENCA:\n"
        f"{BASIN_SHP}"
    )


# ============================================================
# 6. LEER CUENCA
# ============================================================

print()
print("=" * 80)
print("LEYENDO CUENCA")
print("=" * 80)

try:

    basin = gpd.read_file(
        BASIN_SHP
    )

except Exception as e:

    raise RuntimeError(
        "ERROR AL LEER EL SHAPEFILE:\n"
        f"{e}"
    )


# ============================================================
# 7. VALIDAR GEOMETRÍA
# ============================================================

if basin.empty:

    raise RuntimeError(
        "EL SHAPEFILE DE LA CUENCA ESTÁ VACÍO."
    )


print()
print("Número de geometrías:")
print(len(basin))

print()
print("CRS de la cuenca:")
print(basin.crs)


# ============================================================
# 8. UNIR TODAS LAS GEOMETRÍAS
# ============================================================

print()
print("Uniendo geometrías de la cuenca...")

try:

    basin_geometry = basin.geometry.union_all()

except AttributeError:

    # Compatibilidad con versiones antiguas
    basin_geometry = basin.geometry.unary_union


# ============================================================
# 9. VALIDAR GEOMETRÍA
# ============================================================

if basin_geometry is None:

    raise RuntimeError(
        "NO SE PUDO OBTENER LA GEOMETRÍA DE LA CUENCA."
    )


if basin_geometry.is_empty:

    raise RuntimeError(
        "LA GEOMETRÍA DE LA CUENCA ESTÁ VACÍA."
    )


print()
print("Geometría de cuenca:")
print(basin_geometry.geom_type)


# ============================================================
# 10. BUSCAR TODOS LOS RASTER
# ============================================================

print()
print("=" * 80)
print("BUSCANDO RASTER")
print("=" * 80)


# Buscar .tif
raster_files = glob.glob(
    os.path.join(
        INPUT_DIR,
        "**",
        "*.tif"
    ),
    recursive=True
)


# Buscar .tiff
raster_files += glob.glob(
    os.path.join(
        INPUT_DIR,
        "**",
        "*.tiff"
    ),
    recursive=True
)


# Eliminar duplicados
raster_files = list(
    set(raster_files)
)


# Ordenar inicialmente
raster_files.sort()


print()
print(
    f"Raster encontrados: {len(raster_files)}"
)


if len(raster_files) == 0:

    raise RuntimeError(
        "NO SE ENCONTRARON ARCHIVOS .TIF "
        "O .TIFF EN LA CARPETA:\n"
        f"{INPUT_DIR}"
    )


# ============================================================
# 11. FUNCIÓN PARA OBTENER FECHA/HORA
# ============================================================

def get_datetime_from_filename(filepath):

    filename = os.path.basename(
        filepath
    )

    try:

        name_without_ext = os.path.splitext(
            filename
        )[0]

        parts = name_without_ext.split("_")


        # ----------------------------------------------------
        # Buscar YYYYMMDD
        # ----------------------------------------------------

        date_part = None

        for part in parts:

            if (
                len(part) == 8
                and part.isdigit()
                and part.startswith("20")
            ):

                date_part = part

                break


        # ----------------------------------------------------
        # Buscar HHMM
        # ----------------------------------------------------

        time_part = None

        for part in parts:

            if (
                len(part) == 4
                and part.isdigit()
            ):

                hour = int(
                    part[:2]
                )

                minute = int(
                    part[2:]
                )

                if (
                    0 <= hour <= 23
                    and 0 <= minute <= 59
                ):

                    time_part = part

                    break


        # ----------------------------------------------------
        # Construir fecha
        # ----------------------------------------------------

        if date_part is not None:

            if time_part is None:

                time_part = "0000"


            dt = datetime.strptime(
                date_part + time_part,
                "%Y%m%d%H%M"
            )

            return dt


    except Exception:

        pass


    # --------------------------------------------------------
    # Si no se pudo obtener del nombre,
    # usar fecha de modificación
    # --------------------------------------------------------

    timestamp = os.path.getmtime(
        filepath
    )

    return datetime.fromtimestamp(
        timestamp
    )


# ============================================================
# 12. ORDENAR RASTER CRONOLÓGICAMENTE
# ============================================================

print()
print(
    "Ordenando raster cronológicamente..."
)


raster_files = sorted(
    raster_files,
    key=get_datetime_from_filename
)


# ============================================================
# 13. MOSTRAR PRIMER Y ÚLTIMO RASTER
# ============================================================

first_dt = get_datetime_from_filename(
    raster_files[0]
)

last_dt = get_datetime_from_filename(
    raster_files[-1]
)


print()
print("PRIMER RASTER:")
print(
    first_dt.strftime(
        "%Y-%m-%d %H:%M"
    )
)


print()
print("ÚLTIMO RASTER:")
print(
    last_dt.strftime(
        "%Y-%m-%d %H:%M"
    )
)


# ============================================================
# 14. FUNCIÓN PARA CALCULAR PRECIPITACIÓN AREAL
# ============================================================

def extract_areal_precipitation(
    raster_file,
    basin_geometry
):

    """
    Calcula la precipitación media areal
    dentro de la cuenca.

    El procedimiento es:

        Raster
           |
        Máscara de cuenca
           |
        Píxeles dentro de cuenca
           |
        Eliminar NoData / NaN / negativos
           |
        Media espacial
           |
        PP_areal
    """


    with rasterio.open(
        raster_file
    ) as src:


        # ====================================================
        # CRS DEL RASTER
        # ====================================================

        raster_crs = src.crs


        if raster_crs is None:

            raise RuntimeError(
                "El raster no tiene CRS."
            )


        # ====================================================
        # TRANSFORMAR CUENCA AL CRS DEL RASTER
        # ====================================================

        # El shapefile normalmente puede estar
        # en coordenadas geográficas EPSG:4326.
        #
        # Se transforma automáticamente al CRS
        # que tenga el raster.

        basin_geom_raster = transform_geom(
            basin.crs,
            raster_crs,
            mapping(basin_geometry),
            precision=6
        )


        # ====================================================
        # RECORTAR / ENMASCARAR RASTER
        # ====================================================

        masked_data, masked_transform = mask(
            src,
            [basin_geom_raster],
            crop=True,
            filled=False
        )


        # ====================================================
        # OBTENER BANDA 1
        # ====================================================

        data = masked_data[0]


        # ====================================================
        # CONVERTIR A ARRAY FLOAT
        # ====================================================

        data = data.astype(
            np.float64
        )


        # ====================================================
        # CONSTRUIR MÁSCARA VÁLIDA
        # ====================================================

        valid_mask = np.ones(
            data.shape,
            dtype=bool
        )


        # ----------------------------------------------------
        # Máscara de Rasterio
        # ----------------------------------------------------

        if np.ma.isMaskedArray(
            masked_data[0]
        ):

            valid_mask = (
                ~masked_data[0].mask
            )


        # ====================================================
        # ELIMINAR NaN
        # ====================================================

        valid_mask &= np.isfinite(
            data
        )


        # ====================================================
        # ELIMINAR LLUVIA NEGATIVA
        # ====================================================

        valid_mask &= (
            data >= 0
        )


        # ====================================================
        # ELIMINAR NODATA
        # ====================================================

        if src.nodata is not None:

            valid_mask &= ~np.isclose(
                data,
                src.nodata
            )


        # ====================================================
        # EXTRAER VALORES VÁLIDOS
        # ====================================================

        valid_values = data[
            valid_mask
        ]


        # ====================================================
        # SI NO HAY DATOS
        # ====================================================

        if len(valid_values) == 0:

            return np.nan, 0


        # ====================================================
        # PRECIPITACIÓN MEDIA AREAL
        # ====================================================

        areal_precipitation = float(
            np.mean(
                valid_values
            )
        )


        # ====================================================
        # NÚMERO DE PÍXELES
        # ====================================================

        number_pixels = len(
            valid_values
        )


        return (
            areal_precipitation,
            number_pixels
        )


# ============================================================
# 15. PROCESAR TODOS LOS RASTER
# ============================================================

records = []


print()
print("=" * 80)
print("CALCULANDO PRECIPITACIÓN AREAL")
print("=" * 80)


for i, raster_file in enumerate(
    raster_files,
    start=1
):


    # ========================================================
    # FECHA/HORA
    # ========================================================

    dt = get_datetime_from_filename(
        raster_file
    )


    print()
    print(
        f"[{i}/{len(raster_files)}] "
        f"{dt.strftime('%Y-%m-%d %H:%M')}"
    )


    print(
        os.path.basename(
            raster_file
        )
    )


    # ========================================================
    # REGISTRO
    # ========================================================

    record = {

        "fecha": dt,

        "PP_areal": np.nan,

        "n_pixeles": 0

    }


    try:


        # ====================================================
        # CALCULAR PRECIPITACIÓN AREAL
        # ====================================================

        pp_areal, n_pixels = (
            extract_areal_precipitation(
                raster_file,
                basin_geometry
            )
        )


        record[
            "PP_areal"
        ] = pp_areal


        record[
            "n_pixeles"
        ] = n_pixels


        # ====================================================
        # MOSTRAR RESULTADO
        # ====================================================

        if np.isnan(pp_areal):

            print(
                "  PP_areal: NaN"
            )

        else:

            print(
                f"  PP_areal: "
                f"{pp_areal:.4f}"
            )


        print(
            f"  Píxeles válidos: "
            f"{n_pixels}"
        )


    except Exception as e:


        print()
        print(
            "ERROR PROCESANDO RASTER:"
        )

        print(
            e
        )


    # ========================================================
    # AGREGAR REGISTRO
    # ========================================================

    records.append(
        record
    )


# ============================================================
# 16. CREAR DATAFRAME
# ============================================================

print()
print("=" * 80)
print("CREANDO DATAFRAME")
print("=" * 80)


df = pd.DataFrame(
    records
)


# ============================================================
# 17. ORDENAR CRONOLÓGICAMENTE
# ============================================================

df = df.sort_values(
    "fecha"
).reset_index(
    drop=True
)


# ============================================================
# 18. ELIMINAR DUPLICADOS
# ============================================================

df = df.drop_duplicates(
    subset=["fecha"],
    keep="last"
)


# ============================================================
# 19. CONVERTIR FECHA
# ============================================================

df["fecha"] = pd.to_datetime(
    df["fecha"]
)


# ============================================================
# 20. REORDENAR COLUMNAS
# ============================================================

df = df[
    [
        "fecha",
        "PP_areal",
        "n_pixeles"
    ]
]


# ============================================================
# 21. GENERAR NOMBRE DEL CSV
# ============================================================

csv_filename = (
    "IMERG_TUMBES_AREAL_"
    f"{execution_date.replace('-', '')}.csv"
)


csv_path = os.path.join(
    OUTPUT_DIR,
    csv_filename
)


# ============================================================
# 22. GUARDAR CSV
# ============================================================

df.to_csv(
    csv_path,
    index=False,
    encoding="utf-8-sig",
    date_format="%Y-%m-%d %H:%M"
)


# ============================================================
# 23. RESUMEN
# ============================================================

print()
print()
print("=" * 80)
print("PROCESO TERMINADO")
print("=" * 80)


print()
print(
    f"Total de raster procesados: "
    f"{len(raster_files)}"
)


print()
print(
    f"Total de registros: "
    f"{len(df)}"
)


print()
print("Fecha inicial:")

print(
    df["fecha"].min().strftime(
        "%Y-%m-%d %H:%M"
    )
)


print()
print("Fecha final:")

print(
    df["fecha"].max().strftime(
        "%Y-%m-%d %H:%M"
    )
)


# ============================================================
# 24. DATOS FALTANTES
# ============================================================

print()
print("=" * 80)
print("DATOS FALTANTES")
print("=" * 80)


missing = df[
    "PP_areal"
].isna().sum()


total = len(df)


percentage = (
    missing / total * 100
    if total > 0
    else 0
)


print()
print(
    f"PP_areal: "
    f"{missing} "
    f"de {total} "
    f"({percentage:.2f} %)"
)


# ============================================================
# 25. ESTADÍSTICAS DE PRECIPITACIÓN
# ============================================================

valid_pp = df[
    "PP_areal"
].dropna()


print()
print("=" * 80)
print("ESTADÍSTICAS DE PRECIPITACIÓN AREAL")
print("=" * 80)


if len(valid_pp) > 0:

    print()
    print(
        f"Mínimo:  "
        f"{valid_pp.min():.4f}"
    )

    print(
        f"Máximo:  "
        f"{valid_pp.max():.4f}"
    )

    print(
        f"Media:   "
        f"{valid_pp.mean():.4f}"
    )

    print(
        f"Mediana: "
        f"{valid_pp.median():.4f}"
    )

    print(
        f"Desv.Std:"
        f" {valid_pp.std():.4f}"
    )


# ============================================================
# 26. MOSTRAR PRIMERAS FILAS
# ============================================================

print()
print("=" * 80)
print("PRIMERAS FILAS")
print("=" * 80)


print()


print(
    df.head(10).to_string(
        index=False
    )
)


# ============================================================
# 27. MOSTRAR ÚLTIMAS FILAS
# ============================================================

print()
print("=" * 80)
print("ÚLTIMAS FILAS")
print("=" * 80)


print()


print(
    df.tail(10).to_string(
        index=False
    )
)


# ============================================================
# 28. UBICACIÓN DEL CSV
# ============================================================

print()
print("=" * 80)
print("CSV GENERADO")
print("=" * 80)


print()
print(csv_path)


print()
print("=" * 80)
print("LISTO")
print("=" * 80)


