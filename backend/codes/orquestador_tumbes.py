# =============================================================================
# ORQUESTADOR COMPLETO - SISTEMA TUMBES
# =============================================================================
#
# GUARDAR ESTE ARCHIVO EN:
# E:\tumbes_262\backend\codes\orquestador_tumbes.py
#
# SCRIPTS QUE YA TIENES EN LA MISMA CARPETA:
#
#   descargar_imerg_early.py
#   descarga_q_tigre.py
#   extraer_lluvia_estaciones.py
#   extraccion_areal.py
#
# ORDEN:
#
#   1. IMERG
#   2. CAUDAL EL TIGRE
#   3. LLUVIA DE ESTACIONES
#   4. PRECIPITACIÓN AREAL
#
# El orquestador NO modifica esos cuatro scripts.
# Solamente los ejecuta uno después del otro.
#
# =============================================================================

from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime


# =============================================================================
# RUTA DE ESTA CARPETA (DINÁMICA - NÚCLEO)
# =============================================================================

CODES_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CODES_DIR.parent.parent


# =============================================================================
# SCRIPTS
# =============================================================================

SCRIPT_IMERG = CODES_DIR / "descargar_imerg_early.py"

SCRIPT_CAUDAL = CODES_DIR / "descarga_q_tigre.py"

SCRIPT_ESTACIONES = CODES_DIR / "extraer_lluvia_estaciones.py"

SCRIPT_AREAL = CODES_DIR / "extraccion_areal.py"


# =============================================================================
# PAUSA ENTRE PROCESOS
# =============================================================================

PAUSA = 2


# =============================================================================
# FUNCIÓN PARA MOSTRAR ENCABEZADOS
# =============================================================================

def encabezado(numero, titulo):

    print()
    print()
    print("=" * 90)
    print(f" PASO {numero}: {titulo}")
    print("=" * 90)
    print()


# =============================================================================
# VALIDAR SCRIPTS
# =============================================================================

def validar_scripts():

    scripts = [
        SCRIPT_IMERG,
        SCRIPT_CAUDAL,
        SCRIPT_ESTACIONES,
        SCRIPT_AREAL,
    ]

    print()
    print("=" * 90)
    print("VERIFICANDO SCRIPTS")
    print("=" * 90)
    print()

    todos_ok = True

    for script in scripts:

        if script.exists():

            print(f"OK     {script.name}")

        else:

            print(f"FALTA  {script}")

            todos_ok = False

    print()

    if not todos_ok:

        raise FileNotFoundError(
            f"No se encontraron todos los scripts necesarios en {CODES_DIR}"
        )


# =============================================================================
# EJECUTAR SCRIPT
# =============================================================================

def ejecutar_script(numero, titulo, script):

    encabezado(numero, titulo)

    print("Ejecutando:")
    print(script)
    print()

    inicio = time.time()

    # Se utiliza exactamente el mismo Python con el que
    # se ejecuta este orquestador.
    resultado = subprocess.run(
        [
            sys.executable,
            str(script),
        ],
        cwd=str(CODES_DIR),
    )

    segundos = time.time() - inicio

    print()
    print("-" * 90)
    print(f"FIN DEL PASO {numero}")
    print(f"Script : {script.name}")
    print(f"Tiempo : {segundos / 60:.2f} minutos")
    print(f"Código : {resultado.returncode}")
    print("-" * 90)

    # Si falla un paso, detener todo.
    if resultado.returncode != 0:

        raise RuntimeError(
            f"El paso {numero} falló: {script.name}"
        )


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():

    inicio_total = time.time()

    print()
    print("=" * 90)
    print(" SISTEMA DE ACTUALIZACIÓN HIDROLÓGICA - TUMBES")
    print("=" * 90)

    print()
    print(f"Fecha/hora de ejecución: {datetime.now():%Y-%m-%d %H:%M:%S}")

    print()
    print("Carpeta de códigos:")
    print(CODES_DIR)

    print()
    print("FLUJO:")
    print()
    print("  1. Descargar / actualizar IMERG Early")
    print("                  |")
    print("  2. Descargar caudal El Tigre")
    print("                  |")
    print("  3. Extraer lluvia de estaciones")
    print("                  |")
    print("  4. Calcular precipitación areal")
    print()

    # -------------------------------------------------------------------------
    # VERIFICAR
    # -------------------------------------------------------------------------

    validar_scripts()

    # -------------------------------------------------------------------------
    # PASO 1
    # -------------------------------------------------------------------------

    ejecutar_script(
        1,
        "IMERG EARLY",
        SCRIPT_IMERG,
    )

    time.sleep(PAUSA)

    # -------------------------------------------------------------------------
    # PASO 2
    # -------------------------------------------------------------------------

    ejecutar_script(
        2,
        "CAUDAL EL TIGRE - SENAMHI",
        SCRIPT_CAUDAL,
    )

    time.sleep(PAUSA)

    # -------------------------------------------------------------------------
    # PASO 3
    # -------------------------------------------------------------------------

    ejecutar_script(
        3,
        "LLUVIA IMERG PARA ESTACIONES",
        SCRIPT_ESTACIONES,
    )

    time.sleep(PAUSA)

    # -------------------------------------------------------------------------
    # PASO 4
    # -------------------------------------------------------------------------

    ejecutar_script(
        4,
        "PRECIPITACIÓN MEDIA AREAL DE LA CUENCA",
        SCRIPT_AREAL,
    )

    # -------------------------------------------------------------------------
    # FINAL
    # -------------------------------------------------------------------------

    tiempo_total = time.time() - inicio_total

    print()
    print()
    print("=" * 90)
    print(" ACTUALIZACIÓN COMPLETA TERMINADA")
    print("=" * 90)

    print()
    print("Los cuatro procesos terminaron correctamente.")

    print()
    print(f"Tiempo total: {tiempo_total / 60:.2f} minutos")

    print()
    print("=" * 90)
    print(" LISTO")
    print("=" * 90)
    print()


# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print()
        print("=" * 90)
        print(" PROCESO CANCELADO POR EL USUARIO")
        print("=" * 90)
        print()

        sys.exit(130)

    except Exception as error:

        print()
        print()
        print("=" * 90)
        print(" ERROR EN LA ACTUALIZACIÓN")
        print("=" * 90)

        print()
        print(str(error))

        print()
        print("=" * 90)

        sys.exit(1)
