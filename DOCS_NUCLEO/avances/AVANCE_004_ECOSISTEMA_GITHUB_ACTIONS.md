# Bitácora de Avance 004 - Preparación del Ecosistema GitHub & GitHub Actions

- **Fecha:** 26 de Octubre de 2026
- **Agente:** NÚCLEO PRINCIPAL
- **Referencia de Arquitectura:** Sistema AMARU-POI (`AMARU-POI/.github/workflows/main.yml`)
- **Objetivo:** Garantizar que el proyecto esté protegido en GitHub y automatizado en la nube mediante Actions.

---

## 🚀 Acciones Realizadas

1. **Análisis de la Arquitectura de AMARU-POI:**
   - Se revisó el workflow maestro de AMARU (`.github/workflows/main.yml`), identificando el uso de runners Ubuntu, inyección de Secrets, instalación limpia de dependencias y commits automáticos con `git push`.

2. **Creación del `.gitignore` Estratégico:**
   - Protege credenciales (`.env`), cachés y carpetas temporales (`backend/data/_temp/`).
   - Mantiene bajo control de versiones el código, la documentación de `DOCS_NUCLEO/`, las series consolidadas y los shapefiles.

3. **Creación del Workflow Maestro para GitHub Actions:**
   - Archivo: [`.github/workflows/actualizacion_automatica.yml`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/.github/workflows/actualizacion_automatica.yml)
   - **Disparadores (Triggers):**
     - Manual: `workflow_dispatch` (un clic desde GitHub).
     - Automático: `cron: "0 */3 * * *"` (cada 3 horas).
   - **Instalación:** Drivers GDAL de Linux + dependencias Python.
   - **Ejecución:** Invoca de manera nativa [`backend/codes/orquestador_tumbes.py`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/backend/codes/orquestador_tumbes.py).
   - **Persistencia:** Commit y push automático de `backend/data_caudal/` y `backend/data_lluvia/`.

---

## 📋 Pasos para la Publicación Inicial en GitHub
1. Inicializar git: `git init` y vincular con tu repositorio remoto.
2. Cargar en GitHub Secrets:
   - `SENAMHI_API_KEY`
   - `UCAR_EMAIL`
   - `UCAR_PASS`
3. Desplegar en Streamlit Cloud apuntando a `frontend/app.py`.
