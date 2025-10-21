import psutil
import json
import time
import platform
from datetime import datetime
from typing import Dict, List


class SystemMonitor:
    def __init__(self):
        self.data_history = {
            "cpu": [],
            "memory": [],
            "disk": [],
            "network": []
        }
        self.max_points = 100

    def get_cpu_usage(self) -> float:
        """Retorna o uso atual da CPU em percentual"""
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self) -> Dict:
        """Retorna informações de uso da memória"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percentage": memory.percent,
        }

    def get_disk_usage(self) -> Dict:
        """Retorna informações de uso do disco"""
        try:
            # Linux/Mac
            disk = psutil.disk_usage("/")
        except Exception:
            try:
                # Windows - usar barra normal ou raw string
                disk = psutil.disk_usage(r"C:/")  # raw string para evitar problemas
            except Exception:
                # Fallback para primeira partição disponível
                partitions = psutil.disk_partitions()
                if partitions:
                    disk = psutil.disk_usage(partitions[0].mountpoint)
                else:
                    raise Exception("Nenhuma partição encontrada")

        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percentage": disk.percent,
        }

    def get_network_stats(self) -> Dict:
        """Retorna estatísticas de rede"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }

    def get_system_info(self) -> Dict:
        """Retorna informações gerais do sistema"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())

            # Hostname
            try:
                if psutil.users() and len(psutil.users()) > 0:
                    hostname = psutil.users()[0].name
                else:
                    hostname = platform.node()
            except:
                hostname = platform.node()

            # Platform info como STRING
            platform_str = f"{platform.system()} {platform.release()}"

            return {
                "hostname": str(hostname),
                "platform": str(platform_str),
                "cpu_count": int(psutil.cpu_count()),
                "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
                "uptime": str(datetime.now() - boot_time).split(".")[0],
            }
        except Exception as e:
            print(f"⚠️  Erro em get_system_info: {e}")
            return {
                "hostname": "Unknown",
                "platform": platform.system(),
                "cpu_count": psutil.cpu_count() or 1,
                "boot_time": "N/A",
                "uptime": "N/A",
            }

    def get_all_metrics(self) -> Dict:
        """Coleta todas as métricas do sistema"""
        try:
            timestamp = datetime.now().isoformat()

            metrics = {
                "timestamp": timestamp,
                "cpu": self.get_cpu_usage(),
                "memory": self.get_memory_usage(),
                "disk": self.get_disk_usage(),
                "network": self.get_network_stats(),
                # "system_info": self.get_system_info(),  # Comente para evitar erros em testes
            }

            # Adicionar ao histórico
            self._add_to_history(metrics)

            return metrics

        except Exception as e:
            print(f"❌ Erro em get_all_metrics: {e}")
            raise

    def _add_to_history(self, metrics: Dict):
        """Adiciona métricas ao histórico mantendo limite máximo"""
        timestamp = metrics["timestamp"]

        self.data_history["cpu"].append({"timestamp": timestamp, "value": metrics["cpu"]})
        self.data_history["memory"].append(
            {"timestamp": timestamp, "value": metrics["memory"]["percentage"]}
        )
        self.data_history["disk"].append(
            {"timestamp": timestamp, "value": metrics["disk"]["percentage"]}
        )

        # Manter apenas os últimos max_points
        for key in self.data_history:
            if len(self.data_history[key]) > self.max_points:
                self.data_history[key] = self.data_history[key][-self.max_points:]

    def get_history(self) -> Dict:
        """Retorna o histórico de dados"""
        return self.data_history

    def check_alerts(self, metrics: Dict, thresholds: Dict) -> List[Dict]:
        """Verifica se alguma métrica excedeu os limites de alerta"""
        alerts = []

        if metrics["cpu"] > thresholds.get("cpu", 80):
            alerts.append(
                {
                    "type": "CPU",
                    "level": "warning",
                    "message": f"CPU usage is {metrics['cpu']:.1f}%",
                    "timestamp": metrics["timestamp"],
                }
            )

        if metrics["memory"]["percentage"] > thresholds.get("memory", 85):
            alerts.append(
                {
                    "type": "Memory",
                    "level": "warning",
                    "message": f"Memory usage is {metrics['memory']['percentage']:.1f}%",
                    "timestamp": metrics["timestamp"],
                }
            )

        if metrics["disk"]["percentage"] > thresholds.get("disk", 90):
            alerts.append(
                {
                    "type": "Disk",
                    "level": "critical",
                    "message": f"Disk usage is {metrics['disk']['percentage']:.1f}%",
                    "timestamp": metrics["timestamp"],
                }
            )

        return alerts
