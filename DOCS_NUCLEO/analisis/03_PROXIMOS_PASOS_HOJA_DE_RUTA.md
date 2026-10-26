# Hoja de Ruta Operativa y Próximos Pasos - Visor TUMBES

- **Fecha:** 26 de Octubre de 2026
- **Agente:** NÚCLEO PRINCIPAL
- **Misión:** Transición de sistema local estático a plataforma hidrológica operativa y automatizada.

---

## Hallazgo Clave en el Frontend (`app.py`)
Al analizar las 1,372 líneas de `app.py`, se descubrió que:
1. **La sección 1 (Precipitación y Monitoreo Espacial)** funciona con mapas satelitales y rasters.
2. **La sección 2 (Pronóstico de Caudal - 72 horas)** tiene la gráfica vacía (`fig_caudal = go.Figure()`, marcada como placeholder). No está leyendo aún el archivo `caudal_el_tigre_72h.csv` que ya descargamos con éxito.
3. **Las secciones 3 y 4 (Áreas de inundación e Impactos)** están en paneles provisionales esperando capas e indicadores.

---

## 3 Rutas de Trabajo Inmediatas

### 🎯 Opción 1: Conectar los Datos Reales al Visor (Frontend Operativo)
- Conectar `backend/data_caudal/caudal_el_tigre_72h.csv` a la sección 2 de Streamlit para graficar la serie histórica y los umbrales de alerta (Amarillo: 600 m³/s, Naranja: 1000 m³/s, Rojo: 1500 m³/s).
- Visualizar en la cabecera el último caudal registrado en El Tigre en tiempo real.

### ⚙️ Opción 2: Automatización en Segundo Plano (Daemon / Scheduler)
- Crear un script autónomo de ejecución periódica (`scheduler_tumbes.py` o tarea de Windows Task Scheduler).
- Configurado para ejecutar el orquestador cada 1h o 3h de forma silenciosa, manteniendo los datos y mapas al día sin requerir intervención del usuario.

### 🤖 Opción 3: Módulo Predictivo y Alertas Tempranas (Model / Early Warning)
- Estructurar el directorio `backend/model/eltigre` para incorporar el modelo hidrológico / IA que proyecte el caudal futuro a partir de la lluvia IMERG acumulada en la cuenca.
- Crear disparador de alertas (por consola, Telegram o correo) ante crecidas repentinas.
