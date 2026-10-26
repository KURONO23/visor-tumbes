# 01. Arquitectura y Diagnóstico Inicial del Proyecto Visor TUMBES

**Fecha de análisis:** 26 de Octubre de 2026  
**Responsable:** NÚCLEO PRINCIPAL  
**Proyecto:** POI 2026 - Visor TUMBES  

---

## 1. Visión General del Proyecto
El proyecto **Visor_TUMBES** es un sistema hidro-meteorológico de monitoreo y visualización enfocado en la cuenca del Río Tumbes. Integra descarga automatizada de precipitación satelital (IMERG Early), estaciones pluviométricas e hidrológicas locales (caudal en estación El Tigre), procesamiento espacial areal y una interfaz interactiva basada en Streamlit.

---

## 2. Radiografía de Componentes

### 2.1 Backend (`backend/`)
- **`codes/descargar_imerg_early.py`**: Pipeline de ingesta para precipitación satelital NASA GPM IMERG Early.
- **`codes/descarga_q_tigre.py`**: Descarga y procesamiento de series de caudal hidrográfico de la estación El Tigre.
- **`codes/extraccion_areal.py`**: Cálculo de precipitación media areal por subcuencas/zonas usando geodatos.
- **`codes/extraer_lluvia_estaciones.py`**: Extracción y homogenización de datos de estaciones de lluvia en tierra.
- **`codes/orquestador_tumbes.py`**: Coordinador central de tareas automatizadas de extracción y procesamiento.
- **Directorios de Almacenamiento**:
  - `data_lluvia/`: Series temporales y raw data de precipitación.
  - `data_caudal/`: Series temporales de caudal.
  - `data_espacial/`: Capas vectoriales/raster geográficas de Tumbes.
  - `model/`: Modelos hidrológicos, calibraciones o pesos predictivos.
  - `foto/`: Recursos multimedia o capturas operativas.

### 2.2 Frontend (`frontend/`)
- **`app.py`** & **`app1.py`**: Aplicaciones interactivas (Streamlit) para visualización de mapas, series de caudal, umbrales de alerta y monitoreo en tiempo real.

---

## 3. Estado y Próximos Pasos del NÚCLEO
1. Revisión exhaustiva del flujo de orquestación (`orquestador_tumbes.py`).
2. Modularización y empaquetado de funciones críticas para ejecución limpia en **Codex** y **Claude**.
3. Creación de tests unitarios y estandarización del entorno virtual (`requirements.txt` / dependencias).
