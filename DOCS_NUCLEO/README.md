# NÚCLEO - PROYECTO PRINCIPAL: VISOR TUMBES (POI 2026)

Bienvenido al repositorio central de control, documentación y código interoperable del **NÚCLEO PRINCIPAL** para el proyecto **Visor_TUMBES**.

---

## 🎯 Propósito
Este espacio está preparado para centralizar:
1. **Auditorías y análisis del código base** (`backend` y `frontend`).
2. **Registro cronológico y bitácora de avances** (MDs estructurados).
3. **Paquetes listos para Codex / Claude**: Documentos modulares, prompts auto-contenidos, scripts limpios y contexto exportable para que cualquier modelo (Codex de OpenAI, Claude de Anthropic u otro agente) pueda continuar, iterar o ejecutar cambios sin pérdida de contexto.

---

## 📁 Estructura del Ecosistema `DOCS_NUCLEO/`

```text
DOCS_NUCLEO/
├── README.md                      <- Este archivo (Índice y Manifiesto)
├── analisis/                      <- Análisis técnico del backend, frontend, datos y modelos
│   └── 01_ARQUITECTURA_INICIAL.md <- Radiografía completa del proyecto actual
├── avances/                       <- Bitácoras de cambios, mejoras y estado de entregables
│   └── AVANCE_001_INICIALIZACION.md
└── codex_claude_prompts/          <- Archivos .md y scripts listos para copiar/pegar o inyectar a Claude / Codex
    └── CONTEXTO_EXPORTABLE_LLM.md <- Prompt maestro y contexto unificado
```

---

## 🧭 Flujo de Trabajo Interoperable (NÚCLEO <-> Codex / Claude)
Para llevar avances a Claude o Codex:
1. Dirígete a [`DOCS_NUCLEO/codex_claude_prompts/`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/DOCS_NUCLEO/codex_claude_prompts/).
2. Copia o referencia el archivo [`CONTEXTO_EXPORTABLE_LLM.md`](file:///c:/Users/mgutierrez/Documents/POI-MAX/POI%202026/Visor_TUMBES/DOCS_NUCLEO/codex_claude_prompts/CONTEXTO_EXPORTABLE_LLM.md) junto con la tarea específica.
3. El formato incluye variables, dependencias y fragmentos de código autocontenidos para cero fricción entre IAs.
