from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class SystemMetrics:
    """Modelo para métricas do sistema"""

    timestamp: datetime
    cpu_percent: float
    memory_total: int
    memory_used: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int


@dataclass
class Alert:
    """Modelo para alertas"""

    id: str
    type: str
    level: str
    message: str
    timestamp: datetime
    resolved: bool = False


@dataclass
class ServerInfo:
    """Informações do servidor"""

    hotname: str
    platform: str
    cpu_count: int
    boot_time: datetime
    uptime: str


class MetricsStorage:
    """Class para gerenciar armazenamento de métricas"""

    def __init__(self, max_points: int = 100):
        self.max_points = max_points
        self.metrics_history: List[SystemMetrics] = []
        self.alerts_history: List[Alert] = []

    def add_metrics(self, metrics: SystemMetrics):
        """Adiciona métricas ao histórico"""
        self.metrics_history.append(metrics)

        if len(self.metrics_history) > self.max_points:
            self.metrics_history = self.metrics_history[-self.max_points :]

    def add_alert(self, alert: Alert):
        """Adiciona alerta ao histórico"""
        self.alerts_history.append(alert)

        # Manter apens os últimos 50 alertas
        if len(self.alerts_history) > 50:
            self.alerts_history = self.alerts_history[-50:]

    def get_recent_metrics(self, limit: int = 50) -> List[SystemMetrics]:
        """Retorna métricas recentes"""
        return self.metrics_history[-limit:] if self.metrics_history else []

    def get_recent_alerts(self, limit: int = 20) -> List[Alert]:
        """Retorna alertas recentes"""
        return self.alerts_history[-limit:] if self.alerts_history else []
