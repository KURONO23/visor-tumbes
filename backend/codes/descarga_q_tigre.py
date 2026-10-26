
# =============================================================================
# DESCARGA DE CAUDAL SENAMHI - EL TIGRE
# =============================================================================
#
# Descarga las últimas 72 horas de caudal horario
# de la estación EL TIGRE desde la API de SENAMHI.
#
# SALIDA:
# E:\tumbes_262\backend\data_caudal\caudal_el_tigre_72h.csv
#
# HORA:
# Perú / America-Lima / UTC-5
#
# CREDENCIAL:
# E:\tumbes_262\.env
#
# Contenido del .env:
# SENAMHI_API_KEY=TU_API_KEY
#
# =============================================================================

import os
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from dotenv import load_dotenv


# =============================================================================
# 1. CONFIGURACIÓN
# =============================================================================

# Proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# Carpeta de salida
OUTPUT_DIR = PROJECT_ROOT / "backend" / "data_caudal"

# Crear carpeta automáticamente si no existe
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Archivo CSV final
CSV_PATH = OUTPUT_DIR / "caudal_el_tigre_72h.csv"


# =============================================================================
# 2. ARCHIVO .ENV
# =============================================================================

ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(
    ENV_PATH
)


# API KEY de SENAMHI
API_KEY = os.getenv(
    "SENAMHI_API_KEY",
    ""
).strip()


# =============================================================================
# 3. API SENAMHI
# =============================================================================

API_URL = (
    "https://www.senamhi.gob.pe/dev/phisis/v2/"
    "ms-interoperabilidad/api/v1/estaciones/datos"
)


# =============================================================================
# 4. CONFIGURACIÓN DE LA ESTACIÓN
# =============================================================================

ESTACION_OBJETIVO = "EL TIGRE"


# =============================================================================
# 5. CONFIGURACIÓN TEMPORAL
# =============================================================================

HORAS_A_DESCARGAR = 72

TZ_PERU = ZoneInfo(
    "America/Lima"
)


# Tiempo máximo de espera de la API
TIMEOUT = 60


# =============================================================================
# 6. ERROR PERSONALIZADO
# =============================================================================

class SenamhiAPIError(Exception):

    pass


# =============================================================================
# 7. NORMALIZAR TEXTO
# =============================================================================

def normalizar(texto):

    texto = unicodedata.normalize(
        "NFD",
        str(texto)
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = texto.upper().strip()

    texto = " ".join(
        texto.split()
    )

    return texto


# =============================================================================
# 8. HORA ACTUAL DE PERÚ
# =============================================================================

def obtener_hora_peru():

    return datetime.now(
        TZ_PERU
    )


# =============================================================================
# 9. EXTRAER EL TIGRE
# =============================================================================

def extraer_el_tigre(payload):

    registros = []


    # -------------------------------------------------------------------------
    # Verificar respuesta
    # -------------------------------------------------------------------------

    if not isinstance(
        payload,
        dict
    ):

        raise SenamhiAPIError(
            "La respuesta de SENAMHI no tiene formato JSON esperado."
        )


    # -------------------------------------------------------------------------
    # Recorrer estaciones
    # -------------------------------------------------------------------------

    estaciones = payload.get(
        "data",
        []
    )


    for estacion in estaciones:

        if not isinstance(
            estacion,
            dict
        ):
            continue


        # Nombre de estación
        nombre = str(
            estacion.get(
                "nombreEstacion",
                ""
            )
        ).strip()


        # ---------------------------------------------------------------------
        # Comparación con EL TIGRE
        # ---------------------------------------------------------------------

        if normalizar(nombre) != normalizar(
            ESTACION_OBJETIVO
        ):

            continue


        # Código de estación
        codigo = str(
            estacion.get(
                "codigoVinculado",
                ""
            )
        ).strip()


        # ---------------------------------------------------------------------
        # Valores horarios
        # ---------------------------------------------------------------------

        valores = estacion.get(
            "valores",
            []
        )


        for item in valores:

            if not isinstance(
                item,
                dict
            ):
                continue


            # Fecha
            fecha = item.get(
                "fechaHora",
                item.get("t")
            )


            # Caudal
            valor = item.get(
                "valor",
                item.get("v")
            )


            # Si no hay fecha, ignorar
            if fecha is None:
                continue


            # -----------------------------------------------------------------
            # Convertir caudal
            # -----------------------------------------------------------------

            try:

                if valor in (
                    None,
                    "",
                    "null"
                ):

                    caudal = None

                else:

                    caudal = float(
                        valor
                    )

            except (
                TypeError,
                ValueError
            ):

                caudal = None


            # -----------------------------------------------------------------
            # Guardar
            # -----------------------------------------------------------------

            registros.append(
                {
                    "estacion": nombre,

                    "codigo": codigo,

                    "fecha_hora": fecha,

                    "caudal_m3s": caudal,

                    "flag_update": item.get(
                        "flagUpdate",
                        item.get("f")
                    )
                }
            )


    return registros


# =============================================================================
# 10. CONSULTAR API SENAMHI
# =============================================================================

def consultar_senamhi(ahora_peru):


    # =========================================================================
    # Verificar API KEY
    # =========================================================================

    if not API_KEY:

        raise SenamhiAPIError(
            "\n"
            "NO SE ENCONTRO LA API KEY DE SENAMHI.\n\n"
            "Debes crear/revisar:\n"
            f"{ENV_PATH}\n\n"
            "Y colocar dentro:\n\n"
            "SENAMHI_API_KEY=TU_API_KEY\n"
        )


    # =========================================================================
    # CALCULAR LAS 72 HORAS ANTERIORES
    # =========================================================================

    inicio = (
        ahora_peru
        - timedelta(
            hours=HORAS_A_DESCARGAR
        )
    )


    # =========================================================================
    # FECHAS PARA SENAMHI
    # =========================================================================

    fecha_inicio = inicio.strftime(
        "%d/%m/%Y"
    )


    fecha_fin = ahora_peru.strftime(
        "%d/%m/%Y"
    )


    # =========================================================================
    # PARÁMETROS
    # =========================================================================

    params = {

        "formato": "string",

        "escala": "horario",

        "fechaInicio": fecha_inicio,

        "fechaFin": fecha_fin
    }


    # =========================================================================
    # HEADERS
    # =========================================================================

    headers = {

        "api-key": API_KEY,

        "Accept": "application/json"
    }


    # =========================================================================
    # MOSTRAR INFORMACIÓN
    # =========================================================================

    print()
    print("=" * 80)
    print("CONSULTA A SENAMHI")
    print("=" * 80)

    print(
        f"Estación       : {ESTACION_OBJETIVO}"
    )

    print(
        f"Hora Perú      : "
        f"{ahora_peru:%Y-%m-%d %H:%M:%S}"
    )

    print(
        f"Desde          : "
        f"{inicio:%Y-%m-%d %H:%M:%S}"
    )

    print(
        f"Hasta          : "
        f"{ahora_peru:%Y-%m-%d %H:%M:%S}"
    )

    print(
        f"Horas          : {HORAS_A_DESCARGAR}"
    )

    print()


    # =========================================================================
    # CONSULTA HTTP
    # =========================================================================

    try:

        response = requests.get(

            f"{API_URL}/caudal",

            headers=headers,

            params=params,

            timeout=TIMEOUT
        )


    except requests.RequestException as error:

        raise SenamhiAPIError(
            f"Error de conexión con SENAMHI:\n{error}"
        )


    # =========================================================================
    # AUTENTICACIÓN
    # =========================================================================

    if response.status_code in (
        401,
        403
    ):

        raise SenamhiAPIError(
            "\n"
            "SENAMHI rechazo la autenticación.\n\n"
            "Revisa la SENAMHI_API_KEY del archivo .env.\n"
            f"Archivo: {ENV_PATH}"
        )


    # =========================================================================
    # LIMITE DE CONSULTAS
    # =========================================================================

    if response.status_code == 429:

        raise SenamhiAPIError(
            "SENAMHI respondió HTTP 429: "
            "se alcanzó el límite de solicitudes."
        )


    # =========================================================================
    # OTROS ERRORES
    # =========================================================================

    if response.status_code != 200:

        raise SenamhiAPIError(
            f"\n"
            f"SENAMHI respondió HTTP "
            f"{response.status_code}\n\n"
            f"{response.text[:1000]}"
        )


    # =========================================================================
    # CONVERTIR A JSON
    # =========================================================================

    try:

        payload = response.json()

    except ValueError:

        raise SenamhiAPIError(
            "SENAMHI no devolvió una respuesta JSON válida."
        )


    # =========================================================================
    # EXTRAER EL TIGRE
    # =========================================================================

    registros = extraer_el_tigre(
        payload
    )


    # =========================================================================
    # DATAFRAME
    # =========================================================================

    df = pd.DataFrame(

        registros,

        columns=[
            "estacion",
            "codigo",
            "fecha_hora",
            "caudal_m3s",
            "flag_update"
        ]
    )


    if df.empty:

        return df


    # =========================================================================
    # CONVERTIR FECHA
    # =========================================================================

    df["fecha_hora"] = pd.to_datetime(

        df["fecha_hora"],

        dayfirst=True,

        errors="coerce"
    )


    # =========================================================================
    # CONVERTIR CAUDAL
    # =========================================================================

    df["caudal_m3s"] = pd.to_numeric(

        df["caudal_m3s"],

        errors="coerce"
    )


    # =========================================================================
    # ELIMINAR FECHAS INVALIDAS
    # =========================================================================

    df = df.dropna(
        subset=[
            "fecha_hora"
        ]
    )


    # =========================================================================
    # CONVERTIR A HORA PERÚ SI VIENE CON ZONA HORARIA
    # =========================================================================

    if getattr(
        df["fecha_hora"].dt,
        "tz",
        None
    ) is not None:

        df["fecha_hora"] = (

            df["fecha_hora"]

            .dt

            .tz_convert(
                TZ_PERU
            )

            .dt

            .tz_localize(
                None
            )
        )


    # =========================================================================
    # HORA PERÚ SIN ZONA
    # =========================================================================

    inicio_local = inicio.replace(
        tzinfo=None
    )

    ahora_local = ahora_peru.replace(
        tzinfo=None
    )


    # =========================================================================
    # FILTRAR LAS ÚLTIMAS 72 HORAS
    # =========================================================================

    df = df[

        (df["fecha_hora"] > inicio_local)

        &

        (df["fecha_hora"] <= ahora_local)

    ].copy()


    # =========================================================================
    # ORDENAR
    # =========================================================================

    df = df.sort_values(
        "fecha_hora"
    )


    # =========================================================================
    # ELIMINAR DUPLICADOS
    # =========================================================================

    df = (

        df

        .drop_duplicates(
            subset=[
                "fecha_hora"
            ],
            keep="last"
        )

        .reset_index(
            drop=True
        )
    )


    return df


# =============================================================================
# 11. GUARDAR CSV
# =============================================================================

def guardar_csv(df):


    # =========================================================================
    # VERIFICAR DATOS
    # =========================================================================

    if df.empty:

        print()
        print("=" * 80)
        print("ADVERTENCIA")
        print("=" * 80)

        print(
            "SENAMHI no devolvió datos de EL TIGRE "
            "para el periodo solicitado."
        )

        return False


    # =========================================================================
    # GUARDAR
    # =========================================================================

    df.to_csv(

        CSV_PATH,

        index=False,

        encoding="utf-8-sig"
    )


    # =========================================================================
    # INFORMACIÓN FINAL
    # =========================================================================

    print()
    print("=" * 80)
    print("DESCARGA COMPLETADA")
    print("=" * 80)

    print()

    print(
        f"Archivo generado:"
    )

    print(
        CSV_PATH
    )

    print()

    print(
        f"Registros descargados: {len(df)}"
    )

    print()

    print(
        f"Primera fecha: "
        f"{df['fecha_hora'].min()}"
    )

    print(
        f"Última fecha:  "
        f"{df['fecha_hora'].max()}"
    )

    print()

    print(
        f"Último caudal: "
        f"{df.iloc[-1]['caudal_m3s']} m³/s"
    )

    print()

    print("Últimos registros:")

    print()

    print(
        df[
            [
                "fecha_hora",
                "caudal_m3s"
            ]
        ]
        .tail(10)
        .to_string(
            index=False
        )
    )

    print()

    return True


# =============================================================================
# 12. PROGRAMA PRINCIPAL
# =============================================================================

def main():

    print()
    print("=" * 80)
    print("DESCARGA DE CAUDAL SENAMHI")
    print("ESTACIÓN EL TIGRE")
    print("=" * 80)


    # =========================================================================
    # HORA ACTUAL PERÚ
    # =========================================================================

    ahora = obtener_hora_peru()


    # =========================================================================
    # INFORMACIÓN
    # =========================================================================

    print()

    print(
        f"Hora actual Perú : "
        f"{ahora:%Y-%m-%d %H:%M:%S}"
    )

    print(
        f"Estación         : {ESTACION_OBJETIVO}"
    )

    print(
        f"Periodo          : últimas {HORAS_A_DESCARGAR} horas"
    )

    print(
        f"Salida           : {CSV_PATH}"
    )


    # =========================================================================
    # VERIFICAR API KEY
    # =========================================================================

    if not API_KEY:

        print()
        print("=" * 80)
        print("ERROR: FALTA API KEY")
        print("=" * 80)

        print()

        print(
            f"No se encontró SENAMHI_API_KEY en:"
        )

        print()

        print(
            ENV_PATH
        )

        print()

        print(
            "El archivo .env debe contener:"
        )

        print()

        print(
            "SENAMHI_API_KEY=TU_API_KEY"
        )

        print()

        return


    # =========================================================================
    # CONSULTAR
    # =========================================================================

    try:

        df = consultar_senamhi(
            ahora
        )


    except SenamhiAPIError as error:

        print()
        print("=" * 80)
        print("ERROR EN LA CONSULTA")
        print("=" * 80)

        print()

        print(error)

        print()

        return


    # =========================================================================
    # GUARDAR
    # =========================================================================

    guardar_csv(
        df
    )


# =============================================================================
# EJECUTAR
# =============================================================================

if __name__ == "__main__":

    main()
