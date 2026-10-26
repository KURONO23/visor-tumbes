# Arquitectura de Automatización en la Nube (Estilo AMARU) - Visor TUMBES

- **Fecha:** 26 de Octubre de 2026
- **Agente:** NÚCLEO PRINCIPAL
- **Referencia Técnica:** Patrón de implementación de **AMARU-POI** (`.github/workflows/main.yml`)

---

## 🎯 Visión y Filosofía de Integración
Al igual que en **AMARU-POI**, el objetivo es lograr que **Visor_TUMBES**:
1. Esté versionado y protegido en **GitHub** (código, datos procesados, shapefiles y frontend).
2. Se actualice de manera **autónoma en la nube mediante GitHub Actions**:
   - Ejecutando un cron programado (ej. cada hora o 3 horas).
   - Corriendo el orquestador sin depender de que tu laptop o PC esté encendida.
   - Haciendo `commit` y `push` automático de las salidas (`caudal_el_tigre_72h.csv`, rasters/tablas de lluvia).
3. Despliegue continuo del **Visor (Streamlit Cloud)**:
   - Streamlit Cloud detecta los nuevos commits con los datos actualizados y refresca el visor automáticamente para todo el público o equipo operativo.

---

## 🛠️ Requisitos Críticos para la Nube
Para que GitHub Actions funcione idéntico a AMARU sin fallar:
1. **Archivo `.gitignore` robusto:**
   - Evitar subir archivos temporales pesados (`_temp/`, `.env` con credenciales reales).
   - Proteger los shapefiles y series consolidadas.
2. **Uso de GitHub Secrets:**
   - `SENAMHI_API_KEY`, `UCAR_EMAIL`, `UCAR_PASS` configurados en *Settings > Secrets and variables > Actions*.
3. **Instalación de Drivers Geoespaciales en Ubuntu Runner:**
   - `gdal-bin`, `libgdal-dev` para que `rasterio` y `geopandas` se instalen limpiamente en `ubuntu-latest`.
4. **Workflow Maestro (`.github/workflows/actualizar_tumbes.yml`):**
   - Configurado con triggers `workflow_dispatch` (ejecución manual con 1 clic) y `schedule` (cron recurrente).
