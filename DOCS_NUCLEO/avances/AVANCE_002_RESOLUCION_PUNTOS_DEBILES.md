# Bitácora de Avance 002 - Resolución de Puntos Débiles Críticos

- **Fecha:** 26 de Octubre de 2026
- **Agente:** NÚCLEO PRINCIPAL
- **Objetivo:** Subsanar las fallas estructurales y vulnerabilidades críticas del proyecto.

---

## 🛠️ Puntos Débiles Resueltos

### 1. Eliminación Total de Rutas Hardcodeadas (`E:\tumbes_262\...`)
- **Problema:** El código dependía de una unidad `E:\` que causaba errores inmediatos al ejecutarse en otros entornos.
- **Acción:**
  - Se creó el módulo centralizador [`backend/codes/config.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/backend/codes/config.py) con resolución dinámica usando `Path(__file__).resolve().parent...`.
  - Se actualizaron todos los componentes:
    - [`backend/codes/orquestador_tumbes.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/backend/codes/orquestador_tumbes.py)
    - [`backend/codes/descargar_imerg_early.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/backend/codes/descargar_imerg_early.py)
    - [`backend/codes/descarga_q_tigre.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/backend/codes/descarga_q_tigre.py)
    - [`backend/codes/extraccion_areal.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/backend/codes/extraccion_areal.py)
    - [`backend/codes/extraer_lluvia_estaciones.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/backend/codes/extraer_lluvia_estaciones.py)
    - [`frontend/app.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/frontend/app.py) y [`frontend/app1.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/frontend/app1.py)

### 2. Gestión Segura de Credenciales y Variables de Entorno
- **Problema:** Credenciales en texto plano dentro de los scripts de descarga.
- **Acción:**
  - Implementación de lectura desacoplada mediante `python-dotenv` en [`config.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/backend/codes/config.py) enlazado al archivo [`.env`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/.env).

### 3. Estandarización de Dependencias (`requirements.txt`)
- **Problema:** Inexistencia de archivo de dependencias explícito para entornos de despliegue.
- **Acción:**
  - Generación de [`requirements.txt`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/requirements.txt) congelando las versiones operativas de `rasterio`, `geopandas`, `h5py`, `shapely`, `streamlit` y utilidades.

### 4. Corrección de Compatibilidad de Codificación (Charmap Windows)
- **Problema:** Caracteres Unicode incompatibles con `charmap` (`\u2193`) que provocaban crash en terminales Windows estándar.
- **Acción:**
  - Reemplazo y sanitización de caracteres para garantizar ejecución fluida en PowerShell / CMD.

---

## 📈 Verificación
Se ejecutó la validación formal del orquestador:
- `descargar_imerg_early.py`: **OK**
- `descarga_q_tigre.py`: **OK**
- `extraer_lluvia_estaciones.py`: **OK**
- `extraccion_areal.py`: **OK**
- **Resultado:** Scripts encontrados y rutas relativas validadas exitosamente.
