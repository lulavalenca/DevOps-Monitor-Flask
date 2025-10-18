import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"

    # Configurações de monitoramento
    MONITORING_INTERVAL = 5  # segundos
    MAX_DATA_POINTS = 100  # máximo de pontos no gráfico

    # Configurações de alertas
    CPU_ALERT_THRESHOLD = 80.0
    MEMORY_ALERT_THRESHOLD = 85.0
    DISK_ALERT_THRESHOLD = 90.0

    # WebSocket - THREADING para Windows
    SOCKETIO_ASYNC_MODE = "threading"
