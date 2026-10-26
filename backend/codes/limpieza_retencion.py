# -*- coding: utf-8 -*-
"""
Modulo de Limpieza y Control de Peso - NUCLEO PRINCIPAL
Aplica la politica de ventana deslizante (Rolling Window de 72 horas)
para evitar la acumulacion de datos en GitHub.
"""

from pathlib import Path
from datetime import datetime, timedelta
import shutil
import os
import sys

# Asegurar path
CODES_DIR = Path(__file__).resolve().parent
if str(CODES_DIR) not in sys.path:
    sys.path.append(str(CODES_DIR))

from config import DATA_DIR, DATA_LLUVIA

def purgar_datos_antiguos(dias_retencion=3, ejecutar_borrado=False):
    """
    Control de retencion de carpetas diarias (YYYY-MM-DD).
    Si ejecutar_borrado es False, solo simula (dry-run).
    Si es True, elimina fisicamente.
    """
    fecha_limite = datetime.now() - timedelta(days=dias_retencion)
    fecha_limite_str = fecha_limite.strftime("%Y-%m-%d")

    print()
    print("=" * 80)
    modo = "EJECUCION REAL" if ejecutar_borrado else "MODO SIMULACION (DRY-RUN)"
    print(f"POLITICA DE RETENCION ACTIVA ({modo}): Ultimos {dias_retencion} dias")
    print(f"Fecha de corte: {fecha_limite_str}")
    print("=" * 80)

    carpetas_a_revisar = [DATA_DIR, DATA_LLUVIA]
    total_encontradas = 0

    for base in carpetas_a_revisar:
        if not base.exists():
            continue
        for item in sorted(base.iterdir()):
            if item.is_dir() and item.name != "_temp":
                try:
                    fecha_dir = datetime.strptime(item.name, "%Y-%m-%d")
                    if fecha_dir < fecha_limite:
                        total_encontradas += 1
                        if ejecutar_borrado:
                            print(f"[PURGADO] Carpeta historica: {item.name} en {base.name}")
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            print(f"[DETECTADA PARA PURGAR] Carpeta historica: {item.name} en {base.name}")
                except ValueError:
                    pass

    print(f"Total carpetas identificadas fuera de la ventana: {total_encontradas}")
    print("=" * 80)
    print()
    return total_encontradas

if __name__ == "__main__":
    purgar_datos_antiguos(dias_retencion=3, ejecutar_borrado=False)
