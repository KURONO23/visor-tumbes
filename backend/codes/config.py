# -*- coding: utf-8 -*-
"""
Módulo de Configuración Central - NÚCLEO PRINCIPAL
Define dinámicamente las rutas raíz del proyecto y centraliza la carga de variables de entorno.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Detección dinámica: backend/codes/ -> backend/ -> raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
CODES_DIR = BACKEND_DIR / "codes"

DATA_DIR = BACKEND_DIR / "data"
DATA_LLUVIA = BACKEND_DIR / "data_lluvia"
DATA_CAUDAL = BACKEND_DIR / "data_caudal"
DATA_ESPACIAL = BACKEND_DIR / "data_espacial"
FOTO_DIR = BACKEND_DIR / "foto"
MODEL_DIR = BACKEND_DIR / "model"

# Cargar variables de entorno desde .env en la raíz
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

# Credenciales NASA PPS / UCAR
NASA_USER = os.getenv("UCAR_EMAIL", "")
NASA_PASSWORD = os.getenv("UCAR_PASS", "")

# Token SENAMHI
SENAMHI_TOKEN = os.getenv("SENAMHI_API_KEY", "")
