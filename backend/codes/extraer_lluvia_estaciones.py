
# ============================================================
# EXTRAER LLUVIA IMERG DESDE RASTER GEOTIFF
# PARA ESTACIONES DE TUMBES
#
# ENTRADA:
# E:\tumbes_262\backend\data
#
# Los raster están organizados así:
#
# data/
#   2026-10-19/
#       IMERG_20261019_0000.tif
#       IMERG_20261019_0100.tif
#       IMERG_20261019_0200.tif
#       ...
#
#   2026-10-20/
#       IMERG_20261020_0000.tif
#       ...
#
# SALIDA:
# E:\tumbes_262\backend\data_lluvia
#
#   2026-10-26/
#       IMERG_TUMBES_ESTACIONES_20261026.csv
#
# ============================================================

import os
import glob
import numpy as np
import pandas as pd
import rasterio
from pathlib import Path
from datetime import datetime


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = str(BASE_DIR / "backend" / "data")

OUTPUT_BASE_DIR = str(BASE_DIR / "backend" / "data_lluvia")


# ============================================================
# 2. ESTACIONES
# ============================================================
#
# Coordenadas proporcionadas
#
# IMPORTANTE:
# longitudes negativas = oeste
# latitudes negativas = sur
# ============================================================

STATIONS = {

    "CampamentoSede": {
        "lat": -3.5512,
        "lon": -80.4296
    },

    "ElTigre": {
        "lat": -3.7687,
        "lon": -80.4569
    },

    "Matapalo": {
        "lat": -3.6828,
        "lon": -80.1986
    },

    "RicaPlaya": {
        "lat": -3.8133,
        "lon": -80.4575
    },

    "Canaveral": {
        "lat": -3.9391,
        "lon": -80.6506
    },

    "CaboIngaH": {
        "lat": -3.9797,
        "lon": -80.3989
    },

    "CaboIngaM": {
        "lat": -3.9759,
        "lon": -80.4019
    },

    "Huasimo": {
        "lat": -3.9981,
        "lon": -80.5039
    },

    "PteTumbes": {
        "lat": -3.5709,
        "lon": -80.4607
    },

    "Alamor": {
        "lat": -4.4775,
        "lon": -80.4775
    },

    "Ardilla": {
        "lat": -4.4909,
        "lon": -80.4909
    },

    "ElCiruelOANA": {
        "lat": -4.2995,
        "lon": -80.2995
    },

    "Macara": {
        "lat": -4.3934,
        "lon": -80.3934
    }
}


# ============================================================
# 3. CREAR CARPETA DE SALIDA
# ============================================================

# Fecha en que se ejecuta el programa
execution_date = datetime.now().strftime("%Y-%m-%d")

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
print("EXTRACCIÓN DE LLUVIA IMERG DESDE RASTER")
print("=" * 80)

print()
print("CARPETA DE RASTER:")
print(INPUT_DIR)

print()
print("CARPETA DE SALIDA:")
print(OUTPUT_DIR)

print()
print("ESTACIONES:")
print("-" * 80)

for name, coord in STATIONS.items():

    print(
        f"{name:20s} "
        f"Lat: {coord['lat']:10.4f} "
        f"Lon: {coord['lon']:10.4f}"
    )


# ============================================================
# 5. BUSCAR TODOS LOS RASTER
# ============================================================

print()
print("=" * 80)
print("BUSCANDO RASTER")
print("=" * 80)


# Buscar todos los .tif dentro de las carpetas
# incluyendo subcarpetas

raster_files = glob.glob(
    os.path.join(
        INPUT_DIR,
        "**",
        "*.tif"
    ),
    recursive=True
)


# También buscar .tiff

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


# Ordenar

raster_files.sort()


print()
print(
    f"Raster encontrados: {len(raster_files)}"
)


if len(raster_files) == 0:

    raise RuntimeError(
        "NO SE ENCONTRARON ARCHIVOS .TIF "
        "EN LA CARPETA DE ENTRADA."
    )


# ============================================================
# 6. FUNCIÓN PARA OBTENER FECHA DEL RASTER
# ============================================================

def get_datetime_from_filename(filepath):

    filename = os.path.basename(
        filepath
    )

    # ========================================================
    # FORMATO ESPERADO:
    #
    # IMERG_20261026_0700.tif
    #
    # ========================================================

    try:

        name_without_ext = os.path.splitext(
            filename
        )[0]

        parts = name_without_ext.split("_")


        # Buscar bloque YYYYMMDD

        date_part = None
        time_part = None

        for part in parts:

            if (
                len(part) == 8
                and part.isdigit()
            ):

                # YYYYMMDD

                if (
                    part.startswith("20")
                ):

                    date_part = part


            if (
                len(part) == 4
                and part.isdigit()
            ):

                # HHMM

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


    # ========================================================
    # SI NO SE PUDO OBTENER DEL NOMBRE,
    # USAR FECHA DE MODIFICACIÓN
    # ========================================================

    timestamp = os.path.getmtime(
        filepath
    )

    return datetime.fromtimestamp(
        timestamp
    )


# ============================================================
# 7. ORDENAR LOS RASTER POR FECHA/HORA
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
# 8. MOSTRAR PRIMER Y ÚLTIMO RASTER
# ============================================================

first_dt = get_datetime_from_filename(
    raster_files[0]
)

last_dt = get_datetime_from_filename(
    raster_files[-1]
)


print()
print(
    "PRIMER RASTER:"
)

print(
    first_dt.strftime(
        "%Y-%m-%d %H:%M"
    )
)


print()
print(
    "ÚLTIMO RASTER:"
)

print(
    last_dt.strftime(
        "%Y-%m-%d %H:%M"
    )
)


# ============================================================
# 9. FUNCIÓN PARA ENCONTRAR EL PÍXEL
# ============================================================

def extract_station_value(
    dataset,
    lat,
    lon
):

    # ========================================================
    # CONVERTIR COORDENADA GEOGRÁFICA
    # AL ÍNDICE DE FILA/COLUMNA DEL RASTER
    # ========================================================

    row, col = dataset.index(
        lon,
        lat
    )


    # ========================================================
    # VALIDAR QUE ESTÉ DENTRO DEL RASTER
    # ========================================================

    if (
        row < 0
        or row >= dataset.height
        or col < 0
        or col >= dataset.width
    ):

        return np.nan


    # ========================================================
    # LEER SOLAMENTE EL PÍXEL NECESARIO
    # ========================================================

    value = dataset.read(
        1,
        window=rasterio.windows.Window(
            col,
            row,
            1,
            1
        )
    )[0, 0]


    # ========================================================
    # CONVERTIR A FLOAT
    # ========================================================

    value = float(value)


    # ========================================================
    # NODATA
    # ========================================================

    if dataset.nodata is not None:

        if np.isclose(
            value,
            dataset.nodata
        ):

            return np.nan


    # ========================================================
    # NaN
    # ========================================================

    if np.isnan(value):

        return np.nan


    # ========================================================
    # LLUVIA NEGATIVA NO ES VÁLIDA
    # ========================================================

    if value < 0:

        return np.nan


    return value


# ============================================================
# 10. PROCESAR CADA RASTER
# ============================================================

records = []


print()
print()
print("=" * 80)
print("EXTRAYENDO LLUVIA DE LAS ESTACIONES")
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

        "fecha": dt
    }


    try:

        # ====================================================
        # ABRIR RASTER
        # ====================================================

        with rasterio.open(
            raster_file
        ) as src:


            # ================================================
            # MOSTRAR INFORMACIÓN DEL PRIMER RASTER
            # ================================================

            if i == 1:

                print()
                print(
                    "INFORMACIÓN DEL RASTER:"
                )

                print(
                    f"CRS: {src.crs}"
                )

                print(
                    f"Width: {src.width}"
                )

                print(
                    f"Height: {src.height}"
                )

                print(
                    f"Nodata: {src.nodata}"
                )

                print(
                    f"Resolución: {src.res}"
                )


            # ================================================
            # EXTRAER CADA ESTACIÓN
            # ================================================

            for station_name, coord in STATIONS.items():

                value = extract_station_value(
                    src,
                    coord["lat"],
                    coord["lon"]
                )


                record[
                    station_name
                ] = value


                print(
                    f"  {station_name:20s}: "
                    f"{value:.4f}"
                    if not np.isnan(value)
                    else
                    f"  {station_name:20s}: NaN"
                )


    except Exception as e:

        print()
        print(
            "ERROR LEYENDO RASTER:"
        )

        print(
            e
        )


        # Si falla el raster,
        # guardar NaN en todas las estaciones

        for station_name in STATIONS:

            record[
                station_name
            ] = np.nan


    # ========================================================
    # AGREGAR REGISTRO
    # ========================================================

    records.append(
        record
    )


# ============================================================
# 11. CREAR DATAFRAME
# ============================================================

print()
print("=" * 80)
print("CREANDO DATAFRAME")
print("=" * 80)


df = pd.DataFrame(
    records
)


# ============================================================
# 12. ORDENAR CRONOLÓGICAMENTE
# ============================================================

df = df.sort_values(
    "fecha"
).reset_index(
    drop=True
)


# ============================================================
# 13. ELIMINAR DUPLICADOS
# ============================================================

df = df.drop_duplicates(
    subset=["fecha"],
    keep="last"
)


# ============================================================
# 14. FORMATO DE FECHA
# ============================================================

df["fecha"] = pd.to_datetime(
    df["fecha"]
)


# ============================================================
# 15. REORDENAR COLUMNAS
# ============================================================

column_order = [
    "fecha"
] + list(
    STATIONS.keys()
)


df = df[
    column_order
]


# ============================================================
# 16. GENERAR NOMBRE DEL CSV
# ============================================================

csv_filename = (
    "IMERG_TUMBES_ESTACIONES_"
    f"{execution_date.replace('-', '')}.csv"
)


csv_path = os.path.join(
    OUTPUT_DIR,
    csv_filename
)


# ============================================================
# 17. GUARDAR CSV
# ============================================================

df.to_csv(
    csv_path,
    index=False,
    encoding="utf-8-sig",
    date_format="%Y-%m-%d %H:%M"
)


# ============================================================
# 18. RESUMEN
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


print(
    f"Total de registros: "
    f"{len(df)}"
)


print()
print(
    "Fecha inicial:"
)

print(
    df["fecha"].min().strftime(
        "%Y-%m-%d %H:%M"
    )
)


print()
print(
    "Fecha final:"
)

print(
    df["fecha"].max().strftime(
        "%Y-%m-%d %H:%M"
    )
)


print()
print(
    "Número de estaciones:"
)

print(
    len(STATIONS)
)


print()
print(
    "CSV GENERADO:"
)

print(
    csv_path
)


# ============================================================
# 19. INFORMACIÓN DE DATOS FALTANTES
# ============================================================

print()
print("=" * 80)
print("DATOS FALTANTES")
print("=" * 80)


for station in STATIONS:

    missing = df[
        station
    ].isna().sum()

    total = len(df)

    percentage = (
        missing / total * 100
        if total > 0
        else 0
    )

    print(
        f"{station:20s}: "
        f"{missing:6d} "
        f"({percentage:6.2f} %)"
    )


# ============================================================
# 20. MOSTRAR PRIMERAS FILAS
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


print()
print("=" * 80)
print("LISTO")
print("=" * 80)


