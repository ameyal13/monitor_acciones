# config.py - Configuración general del proyecto

# Acciones a monitorear
ACCIONES = ["AAPL", "NFLX", "MSFT", "GOOGL"]

# Intervalo de monitoreo en segundos
INTERVALO_SEGUNDOS = 60

# Periodo de datos históricos para calcular indicadores
PERIODO_HISTORICO = "5d"
INTERVALO_DATOS = "1h"  # datos cada 1 hora

# Configuración de indicadores
MEDIA_CORTA = 9    # periodos para media móvil corta
MEDIA_LARGA = 21   # periodos para media móvil larga
RSI_PERIODO = 14   # periodos para el RSI
RSI_SOBRECOMPRA = 70
RSI_SOBREVENTA = 30

import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")