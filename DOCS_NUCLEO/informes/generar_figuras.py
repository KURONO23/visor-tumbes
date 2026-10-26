# -*- coding: utf-8 -*-
"""
Generación de Figuras y Gráficos Hidrológicos para el Informe Técnico Word
NÚCLEO PRINCIPAL - POI 2026
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pathlib import Path

FIG_DIR = Path("DOCS_NUCLEO/informes/figuras")
FIG_DIR.mkdir(parents=True, exist_ok=True)

# 1. Gráfico de Caudal El Tigre con Umbrales
caudal_csv = Path("backend/data_caudal/caudal_el_tigre_72h.csv")
if caudal_csv.exists():
    df_q = pd.read_csv(caudal_csv)
    df_q['fecha_hora'] = pd.to_datetime(df_q['fecha_hora'])
    df_q = df_q.dropna(subset=['caudal_m3s'])

    plt.figure(figsize=(10, 4.5), dpi=300)
    plt.plot(df_q['fecha_hora'], df_q['caudal_m3s'], color='#008ED6', linewidth=2.2, label='Caudal Observado (El Tigre)')

    # Umbrales
    plt.axhline(600, color='#E6AF2E', linestyle='--', linewidth=1.5, label='Umbral Amarillo (600 m³/s)')
    plt.axhline(1000, color='#F18805', linestyle='--', linewidth=1.5, label='Umbral Naranja (1000 m³/s)')
    plt.axhline(1500, color='#D90429', linestyle='--', linewidth=1.5, label='Umbral Rojo (1500 m³/s)')

    plt.title('Monitoreo Horario de Caudal - Estación El Tigre (Últimas 72 Horas)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Fecha y Hora (Perú)', fontsize=10)
    plt.ylabel('Caudal (m³/s)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:00'))
    plt.gcf().autofmt_xdate()
    plt.legend(loc='upper right', frameon=True, fontsize=8.5)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "figura1_caudal_el_tigre.png")
    plt.close()
    print("Figura 1 generada.")

# 2. Gráfico de Lluvia Areal de la Cuenca
areal_csv = list(Path("backend/data_lluvia").rglob("*AREAL*.csv"))
if areal_csv:
    df_a = pd.read_csv(areal_csv[0])
    df_a['fecha'] = pd.to_datetime(df_a['fecha'])

    plt.figure(figsize=(10, 4.2), dpi=300)
    plt.bar(df_a['fecha'], df_a['PP_areal'], color='#102638', width=0.03, label='Precipitación Areal Media (mm/h)')
    plt.title('Hietograma Areal de Precipitación IMERG Early - Cuenca Tumbes', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Fecha y Hora', fontsize=10)
    plt.ylabel('Precipitación (mm/h)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:00'))
    plt.gcf().autofmt_xdate()
    plt.legend(loc='upper right', frameon=True, fontsize=8.5)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "figura2_lluvia_areal.png")
    plt.close()
    print("Figura 2 generada.")

# 3. Gráfico de Lluvia Acumulada por Estación
est_csv = list(Path("backend/data_lluvia").rglob("*ESTACIONES*.csv"))
if est_csv:
    df_e = pd.read_csv(est_csv[0])
    cols = [c for c in df_e.columns if c != 'fecha']
    ultimas_72h = df_e.tail(72)[cols].sum().sort_values(ascending=False)

    plt.figure(figsize=(10, 4.5), dpi=300)
    bars = plt.bar(ultimas_72h.index, ultimas_72h.values, color='#00A896', edgecolor='#028090')
    plt.title('Precipitación Acumulada en 72 Horas por Estación (Red Tumbes)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Estación Hidrometeorológica', fontsize=10)
    plt.ylabel('Lluvia Acumulada (mm)', fontsize=10)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{yval:.1f}", ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "figura3_acumulado_estaciones.png")
    plt.close()
    print("Figura 3 generada.")
