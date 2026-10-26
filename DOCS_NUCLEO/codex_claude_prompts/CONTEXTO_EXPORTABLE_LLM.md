# PROMPT MAESTRO Y CONTEXTO EXPORTABLE (PARA CLAUDE / CODEX)

> **Instrucciones para el Operador:**
> Puedes copiar y pegar todo el contenido de este archivo en una conversación con Claude (Anthropic) o OpenAI Codex / ChatGPT para que continúe trabajando exactamente donde NÚCLEO lo dejó, con pleno conocimiento de la arquitectura y variables del proyecto.

---

```markdown
# CONTEXTO DEL PROYECTO: Visor TUMBES (POI 2026) - NÚCLEO PRINCIPAL

## 1. DESCRIPCIÓN GENERAL
Eres el agente colaborador de NÚCLEO PRINCIPAL para el proyecto **Visor_TUMBES**.
Este proyecto es un sistema de monitoreo hidrometeorológico y visor geoespacial en tiempo real para la cuenca del Río Tumbes (Perú).

## 2. ESTRUCTURA DEL PROYECTO
- `backend/codes/`:
  - `descargar_imerg_early.py`: Descarga y procesa precipitación satelital NASA IMERG Early.
  - `descarga_q_tigre.py`: Pipeline para datos de caudal de la estación El Tigre.
  - `extraccion_areal.py`: Procesamiento espacial y zonal de lluvia.
  - `extraer_lluvia_estaciones.py`: Extracción de lluvia en estaciones de superficie.
  - `orquestador_tumbes.py`: Script coordinador que ejecuta los pipelines periódicamente.
- `backend/data_*/`: Carpetas donde residen los datos raw y procesados (`data_lluvia`, `data_caudal`, `data_espacial`).
- `backend/model/`: Modelos y calibraciones numéricas.
- `frontend/`:
  - `app.py`: Tablero principal interactivo (Streamlit).
  - `app1.py`: Versión alterna / experimental de la interfaz.
- `DOCS_NUCLEO/`: Bitácoras, análisis y directivas del proyecto.

## 3. LINEAMIENTOS DE CODIFICACIÓN PARA CLAUDE / CODEX
1. Mantener código modular, con manejo robusto de excepciones (bloques try/except y logging detallado).
2. Preservar las rutas relativas basadas en el directorio raíz del proyecto.
3. Al modificar código, entregar el código completo o bloques reproducibles para evitar desajustes de indentación.
4. Cualquier script nuevo debe ser compatible con Python 3.10+ y documentar claramente sus dependencias.

## 4. TAREA ESPECÍFICA A EJECUTAR:
[INSERTA AQUÍ LA TAREA ESPECÍFICA QUE QUIERES QUE CLAUDE O CODEX RESUELVA]
```
