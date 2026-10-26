
# ============================================================
# DESCARGA IMERG EARLY Y GENERACIÓN DE RASTER HORARIOS
# TUMBES - PERÚ
#
# Salida:
# E:\tumbes_262\backend\data\
#
# Estructura:
# data/
#   YYYY-MM-DD/
#       IMERG_YYYYMMDD_HH00.tif
#
# Cada raster representa lluvia horaria en mm/h.
# ============================================================

import os
import re
import sys
import time
import requests
import h5py
import numpy as np
import rasterio
from rasterio.transform import from_origin
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone


# ============================================================
# CONFIGURACIÓN (DINÁMICA - NÚCLEO)
# ============================================================

from pathlib import Path
try:
    from config import DATA_DIR, NASA_USER, NASA_PASSWORD
    OUTPUT_DIR = str(DATA_DIR)
    USER = NASA_USER
    PASSWORD = NASA_PASSWORD
except ImportError:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    OUTPUT_DIR = str(BASE_DIR / "backend" / "data")
    USER = os.getenv("UCAR_EMAIL", "")
    PASSWORD = os.getenv("UCAR_PASS", "")

# Servidor IMERG Early
BASE_URL = "https://jsimpsonhttps.pps.eosdis.nasa.gov/imerg"


# ============================================================
# DOMINIO ORIGINAL
# ============================================================

# Dominio amplio utilizado para descargar IMERG
#
# latitud:
# -4.5 a -3.0
#
# longitud:
# -80.9 a -79.0
# ============================================================

DOMAIN_LAT_MIN = -4.5
DOMAIN_LAT_MAX = -3.0

DOMAIN_LON_MIN = -80.9
DOMAIN_LON_MAX = -79.0


# ============================================================
# DOMINIO EXACTO DEL MODELO / TUMBES
# ============================================================

LAT_MIN = -4.301953918877448
LAT_MAX = -3.4350468028792765

LON_MIN = -80.72647555796104
LON_MAX = -79.31569609475404


# ============================================================
# CONFIGURACIÓN TEMPORAL
# ============================================================

# Cuántos días hacia atrás descargar
#
# Ejemplo:
# 7  = última semana
# 30 = último mes
# ============================================================

DAYS_BACK = 2


# ============================================================
# SESIÓN HTTP
# ============================================================

session = requests.Session()

session.auth = (USER, PASSWORD)

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})


# ============================================================
# CACHE DE DIRECTORIOS
# ============================================================

directory_cache = {}


# ============================================================
# CREAR CARPETA PRINCIPAL
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# OBTENER ARCHIVOS DISPONIBLES EN NASA PPS
# ============================================================

def get_directory_files(year, month):

    key = f"{year}{month}"

    if key in directory_cache:
        return directory_cache[key]

    url = f"{BASE_URL}/early/{year}{month}/"

    print()
    print("=" * 70)
    print("CONSULTANDO NASA PPS")
    print("=" * 70)
    print(f"URL: {url}")

    try:

        response = session.get(
            url,
            timeout=30
        )

        if response.status_code != 200:

            print(
                f"No se pudo consultar {year}-{month}. "
                f"HTTP {response.status_code}"
            )

            directory_cache[key] = []

            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        files = []

        for a in soup.find_all("a", href=True):

            href = a["href"]

            filename = os.path.basename(href)

            if filename:

                files.append(filename)

        directory_cache[key] = files

        print(
            f"Archivos encontrados: {len(files)}"
        )

        return files

    except Exception as e:

        print(
            f"ERROR consultando directorio "
            f"{year}-{month}: {e}"
        )

        directory_cache[key] = []

        return []


# ============================================================
# BUSCAR ARCHIVO IMERG PARA UNA FECHA/HORA
# ============================================================

def find_imerg_file(dt):

    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")

    hour = dt.strftime("%H")
    minute = dt.strftime("%M")

    # Ejemplo:
    #
    # 20261026- S120000
    #
    # significa:
    # 26 octubre 2026
    # 12:00:00 UTC

    pattern = (
        f"{year}{month}{day}"
        f"-S{hour}{minute}00"
    )

    files = get_directory_files(
        year,
        month
    )

    pattern_lower = pattern.lower()

    candidates = []

    for filename in files:

        name_lower = filename.lower()

        if pattern_lower in name_lower:

            if (
                name_lower.endswith(".h5")
                or name_lower.endswith(".rt-h5")
            ):

                candidates.append(filename)

    if not candidates:

        return None

    # Si existen varios, tomar el primero
    candidates.sort()

    return candidates[0]


# ============================================================
# DESCARGAR ARCHIVO
# ============================================================

def download_file(url, output_file):

    try:

        response = session.get(
            url,
            stream=True,
            timeout=60
        )

        if response.status_code != 200:

            print(
                f"HTTP {response.status_code}"
            )

            return False

        with open(
            output_file,
            "wb"
        ) as f:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:

                    f.write(chunk)

        return True

    except Exception as e:

        print(
            f"Error descargando: {e}"
        )

        return False


# ============================================================
# LEER IMERG Y RECORTAR DOMINIO
# ============================================================

def read_imerg(
    h5_file
):

    with h5py.File(
        h5_file,
        "r"
    ) as h5:

        # ---------------------------------------------
        # PRECIPITACIÓN
        # ---------------------------------------------

        rain = h5[
            "/Grid/precipitation"
        ][0]

        # ---------------------------------------------
        # COORDENADAS
        # ---------------------------------------------

        lat = h5[
            "/Grid/lat"
        ][:]

        lon = h5[
            "/Grid/lon"
        ][:]

    # ========================================================
    # IMERG normalmente almacena la precipitación
    # como tasa/acumulación correspondiente al intervalo.
    #
    # Para media hora:
    # precipitación horaria se obtiene posteriormente
    # sumando dos archivos.
    # ========================================================

    rain = rain / 2.0

    # ========================================================
    # BUSCAR ÍNDICES ESPACIALES
    # ========================================================

    lat_idx = np.where(
        (lat >= DOMAIN_LAT_MIN) &
        (lat <= DOMAIN_LAT_MAX)
    )[0]

    lon_idx = np.where(
        (lon >= DOMAIN_LON_MIN) &
        (lon <= DOMAIN_LON_MAX)
    )[0]

    if len(lat_idx) == 0:

        raise ValueError(
            "No se encontraron latitudes "
            "dentro del dominio."
        )

    if len(lon_idx) == 0:

        raise ValueError(
            "No se encontraron longitudes "
            "dentro del dominio."
        )

    # ========================================================
    # RECORTE
    # ========================================================

    rain_crop = rain[
        lon_idx[:, None],
        lat_idx
    ]

    # Actualmente:
    #
    # lon x lat
    #
    # Convertir a:
    #
    # lat x lon

    rain_crop = rain_crop.T

    lat_crop = lat[lat_idx]

    lon_crop = lon[lon_idx]

    # ========================================================
    # ORDEN LATITUD
    # ========================================================

    # Para GeoTIFF normalmente queremos
    # latitudes descendentes:
    #
    # norte
    # |
    # sur

    if lat_crop[0] < lat_crop[-1]:

        lat_crop = lat_crop[::-1]

        rain_crop = np.flipud(
            rain_crop
        )

    return (
        rain_crop.astype(
            np.float32
        ),
        lat_crop,
        lon_crop
    )


# ============================================================
# CREAR RASTER GEOTIFF
# ============================================================

def save_geotiff(
    output_file,
    data,
    lat,
    lon
):

    # ========================================================
    # RESOLUCIÓN ESPACIAL
    # ========================================================

    if len(lon) > 1:

        res_x = abs(
            lon[1] - lon[0]
        )

    else:

        raise ValueError(
            "No hay suficientes "
            "longitudes."
        )


    if len(lat) > 1:

        res_y = abs(
            lat[1] - lat[0]
        )

    else:

        raise ValueError(
            "No hay suficientes "
            "latitudes."
        )


    # ========================================================
    # TRANSFORMACIÓN GEOGRÁFICA
    # ========================================================

    transform = from_origin(
        lon[0] - res_x / 2,
        lat[0] + res_y / 2,
        res_x,
        res_y
    )


    # ========================================================
    # VALORES NO VÁLIDOS
    # ========================================================

    data = np.asarray(
        data,
        dtype=np.float32
    )

    # Valores negativos de precipitación
    # se consideran inválidos

    data[data < 0] = 0


    # ========================================================
    # ESCRIBIR GEOTIFF
    # ========================================================

    with rasterio.open(

        output_file,

        "w",

        driver="GTiff",

        height=data.shape[0],

        width=data.shape[1],

        count=1,

        dtype="float32",

        crs="EPSG:4326",

        transform=transform,

        compress="lzw",

        nodata=-9999.0

    ) as dst:

        dst.write(
            data,
            1
        )


# ============================================================
# PROCESAR UNA HORA
# ============================================================

def process_one_hour(
    dt_utc,
    temp_dir
):

    print()
    print("-" * 70)

    print(
        f"Procesando UTC: "
        f"{dt_utc.strftime('%Y-%m-%d %H:%M')}"
    )


    # ========================================================
    # NECESITAMOS DOS ARCHIVOS:
    #
    # HORA 00:00
    # HORA 00:30
    #
    # para obtener:
    #
    # 00:00 - 01:00
    # ========================================================

    dt_30_1 = dt_utc

    dt_30_2 = dt_utc + timedelta(
        minutes=30
    )


    # ========================================================
    # BUSCAR PRIMER ARCHIVO
    # ========================================================

    file1 = find_imerg_file(
        dt_30_1
    )

    if not file1:

        print(
            "No existe IMERG para:"
        )

        print(
            dt_30_1
        )

        return False


    # ========================================================
    # BUSCAR SEGUNDO ARCHIVO
    # ========================================================

    file2 = find_imerg_file(
        dt_30_2
    )

    if not file2:

        print(
            "No existe IMERG para:"
        )

        print(
            dt_30_2
        )

        return False


    # ========================================================
    # URLS
    # ========================================================

    url1 = (
        f"{BASE_URL}/early/"
        f"{dt_30_1.strftime('%Y%m')}/"
        f"{file1}"
    )

    url2 = (
        f"{BASE_URL}/early/"
        f"{dt_30_2.strftime('%Y%m')}/"
        f"{file2}"
    )


    # ========================================================
    # ARCHIVOS TEMPORALES
    # ========================================================

    local1 = os.path.join(
        temp_dir,
        file1
    )

    local2 = os.path.join(
        temp_dir,
        file2
    )


    # ========================================================
    # DESCARGAR PRIMER ARCHIVO
    # ========================================================

    print(
        f"Descargando: {file1}"
    )

    ok1 = download_file(
        url1,
        local1
    )

    if not ok1:

        return False


    # ========================================================
    # DESCARGAR SEGUNDO ARCHIVO
    # ========================================================

    print(
        f"Descargando: {file2}"
    )

    ok2 = download_file(
        url2,
        local2
    )

    if not ok2:

        try:
            os.remove(local1)
        except:
            pass

        return False


    try:

        # ====================================================
        # LEER PRIMERA MEDIA HORA
        # ====================================================

        rain1, lat, lon = read_imerg(
            local1
        )


        # ====================================================
        # LEER SEGUNDA MEDIA HORA
        # ====================================================

        rain2, lat2, lon2 = read_imerg(
            local2
        )


        # ====================================================
        # VERIFICAR DIMENSIONES
        # ====================================================

        if rain1.shape != rain2.shape:

            raise ValueError(
                "Las dos grillas IMERG "
                "tienen diferente tamaño."
            )


        # ====================================================
        # LLUVIA HORARIA
        # ====================================================

        rain_hour = (
            rain1 +
            rain2
        )


        # ====================================================
        # HORA LOCAL PERÚ
        # ====================================================

        dt_peru = (
            dt_utc -
            timedelta(hours=5)
        )


        # ====================================================
        # CARPETA DEL DÍA
        # ====================================================

        date_folder = dt_peru.strftime(
            "%Y-%m-%d"
        )

        day_dir = os.path.join(
            OUTPUT_DIR,
            date_folder
        )

        os.makedirs(
            day_dir,
            exist_ok=True
        )


        # ====================================================
        # NOMBRE DEL RASTER
        # ====================================================

        output_name = (
            f"IMERG_"
            f"{dt_peru.strftime('%Y%m%d')}_"
            f"{dt_peru.strftime('%H')}00.tif"
        )


        output_file = os.path.join(
            day_dir,
            output_name
        )


        # ====================================================
        # SI YA EXISTE, NO VOLVER A DESCARGAR/PROCESAR
        # ====================================================

        if os.path.exists(
            output_file
        ):

            print(
                "Raster ya existe:"
            )

            print(
                output_file
            )

            return True


        # ====================================================
        # GUARDAR GEOTIFF
        # ====================================================

        save_geotiff(
            output_file,
            rain_hour,
            lat,
            lon
        )


        print()
        print(
            "RASTER GENERADO CORRECTAMENTE"
        )

        print(
            f"Hora Perú: "
            f"{dt_peru.strftime('%Y-%m-%d %H:%M')}"
        )

        print(
            f"Archivo: "
            f"{output_file}"
        )

        print(
            f"Shape: "
            f"{rain_hour.shape}"
        )

        print(
            f"Min: "
            f"{np.nanmin(rain_hour):.4f} mm"
        )

        print(
            f"Max: "
            f"{np.nanmax(rain_hour):.4f} mm"
        )

        print(
            f"Acumulado espacial: "
            f"{np.nansum(rain_hour):.4f}"
        )


        return True


    except Exception as e:

        print()
        print(
            "ERROR PROCESANDO:"
        )

        print(e)

        return False


    finally:

        # ====================================================
        # BORRAR TEMPORALES
        # ====================================================

        for f in [
            local1,
            local2
        ]:

            if os.path.exists(f):

                try:

                    os.remove(f)

                except PermissionError:

                    print(
                        f"No se pudo borrar: {f}"
                    )


# ============================================================
# BUSCAR LA HORA MÁS RECIENTE DISPONIBLE
# ============================================================

def find_latest_available():

    now = datetime.now(
        timezone.utc
    ).replace(
        minute=0,
        second=0,
        microsecond=0
    )


    # Revisamos las últimas 72 horas
    # buscando el último archivo existente

    print()
    print("=" * 70)
    print("BUSCANDO IMERG MÁS RECIENTE")
    print("=" * 70)


    for i in range(0, 72):

        dt = now - timedelta(
            hours=i
        )

        # IMERG horario necesita:
        #
        # dt
        # dt + 30 min

        f1 = find_imerg_file(
            dt
        )

        f2 = find_imerg_file(
            dt + timedelta(
                minutes=30
            )
        )

        if f1 and f2:

            print()
            print(
                "ÚLTIMA HORA IMERG DISPONIBLE:"
            )

            print(
                dt.strftime(
                    "%Y-%m-%d %H:%M UTC"
                )
            )

            return dt


    return None


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 70)
    print("IMERG EARLY → RASTER HORARIO TUMBES")
    print("=" * 70)

    print()
    print(
        f"Salida:"
    )

    print(
        OUTPUT_DIR
    )

    print()
    print(
        f"Días hacia atrás: {DAYS_BACK}"
    )


    # ========================================================
    # CARPETA TEMPORAL
    # ========================================================

    temp_dir = os.path.join(
        OUTPUT_DIR,
        "_temp"
    )

    os.makedirs(
        temp_dir,
        exist_ok=True
    )


    # ========================================================
    # BUSCAR ÚLTIMA HORA DISPONIBLE
    # ========================================================

    latest = find_latest_available()


    if latest is None:

        print()
        print(
            "NO SE ENCONTRÓ NINGÚN "
            "ARCHIVO IMERG DISPONIBLE."
        )

        return


    # ========================================================
    # HORA INICIAL
    # ========================================================

    start = latest - timedelta(
        days=DAYS_BACK
    )


    # ========================================================
    # GENERAR TODAS LAS HORAS
    # ========================================================

    current = start

    total = 0
    success = 0
    failed = 0


    while current <= latest:

        total += 1

        print()
        print()
        print(
            "#" * 70
        )

        print(
            f"PROGRESO "
            f"{total}"
        )

        print(
            f"Hora UTC: "
            f"{current.strftime('%Y-%m-%d %H:%M')}"
        )

        print(
            "#" * 70
        )


        ok = process_one_hour(
            current,
            temp_dir
        )


        if ok:

            success += 1

        else:

            failed += 1


        current += timedelta(
            hours=1
        )


    # ========================================================
    # LIMPIAR CARPETA TEMPORAL
    # ========================================================

    try:

        if os.path.exists(
            temp_dir
        ):

            files = os.listdir(
                temp_dir
            )

            if len(files) == 0:

                os.rmdir(
                    temp_dir
                )

    except Exception:

        pass


    # ========================================================
    # RESUMEN
    # ========================================================

    print()
    print()
    print("=" * 70)
    print("PROCESO TERMINADO")
    print("=" * 70)

    print()
    print(
        f"Horas procesadas: {total}"
    )

    print(
        f"Raster generados/existentes: {success}"
    )

    print(
        f"Fallidos: {failed}"
    )

    print()
    print(
        "CARPETA DE SALIDA:"
    )

    print(
        OUTPUT_DIR
    )

    print()
    print("=" * 70)


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    main()
