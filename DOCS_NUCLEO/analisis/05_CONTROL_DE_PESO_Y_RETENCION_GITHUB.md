# Estrategia de Control de Peso y Almacenamiento (Anti-Saturación de GitHub)

- **Fecha:** 26 de Octubre de 2026
- **Agente:** NÚCLEO PRINCIPAL
- **Objetivo:** Evitar que el repositorio crezca descontroladamente y supere los límites de GitHub (1 GB recomendado, 100 MB por archivo).

---

## 🔍 Diagnóstico del Almacenamiento Actual

1. **Tamaño real actual:**
   - La carpeta `backend/data/` contiene **174 archivos** y pesa únicamente **11.04 MB**.
   - Cada GeoTIFF es un recorte muy ligero (~600 bytes a 1 KB) porque ya está recortado al dominio exacto de Tumbes.
2. **Requerimiento del Visor (`frontend/app.py`):**
   - El visor utiliza la función `obtener_rasters_48h()`: **solo necesita y muestra las últimas 48 horas (48 rasters)**.
   - Cualquier raster de más de 48 o 72 horas atrás ya no es leído por la interfaz de usuario en tiempo real.

---

## 🛡️ La Solución Definitiva: "Ventana Deslizante (Rolling Retention)"

Para que el repositorio **NUNCA supere los 15-20 MB en toda su vida útil en GitHub**, implementamos una política de retención automática:

```text
[Día 1] -> [Día 2] -> [Día 3 (Hoy)] 
                         └── Se descargan nuevos rasters
                         └── Se eliminan automáticamente rasters con más de 72h
                         └── Repositorio SIEMPRE con tamaño plano constante (~15 MB)
```

### Reglas Técnicas:
1. **Lluvia IMERG (`backend/data/`):** Conservar únicamente los últimos 3 días (72 horas) necesarios para el visor. Las carpetas de días anteriores se purgan automáticamente en cada ciclo.
2. **Series Temporales CSV (`backend/data_caudal/`):** El archivo `caudal_el_tigre_72h.csv` siempre sobreescribe las 72 horas rodantes (pesa apenas 3 KB).
3. **Resúmenes Diarios (`backend/data_lluvia/`):** Solo conserva los resúmenes tabulares consolidados.
4. **Git LFS no es necesario:** Al mantener el repositorio limpio por rotación, no se requiere almacenamiento externo ni cuotas pagas.
