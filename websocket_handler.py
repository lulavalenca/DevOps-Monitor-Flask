from flask_socketio import emit
from flask import request
from datetime import datetime


class WebSocketHandler:
    """Gerenciador de eventos WebSocket"""

    def __init__(self, socketio, system_monitor, config):
        self.socketio = socketio
        self.system_monitor = system_monitor
        self.config = config
        self.connected_clients = set()

        # Registrar eventos
        self.register_events()

    def register_events(self):
        """Registra todos os eventos WebSocket"""

        @self.socketio.on("connect")
        def handle_connect():
            return self.on_connect()

        @self.socketio.on("disconnect")
        def handle_disconnect():
            return self.on_disconnect()

        @self.socketio.on("request_update")
        def handle_request_update():
            return self.on_request_update()

        @self.socketio.on("pause_monitoring")
        def handle_pause():
            return self.on_pause_monitoring()

        @self.socketio.on("resume_monitoring")
        def handle_resume():
            return self.on_resume_monitoring()

    def on_connect(self):
        """Evento: Cliente conectado via WebSocket"""
        client_id = request.sid
        self.connected_clients.add(client_id)

        print(
            f"🔌 Cliente conectado: {client_id} (Total: {len(self.connected_clients)})"
        )

        # Enviar dados iniciais
        try:
            metrics = self.system_monitor.get_all_metrics()
            history = self.system_monitor.get_history()

            emit(
                "initial_data",
                {
                    "metrics": metrics,
                    "history": history,
                    "config": {
                        "update_interval": self.config["MONITORING_INTERVAL"],
                        "thresholds": {
                            "cpu": self.config["CPU_ALERT_THRESHOLD"],
                            "memory": self.config["MEMORY_ALERT_THRESHOLD"],
                            "disk": self.config["DISK_ALERT_THRESHOLD"],
                        },
                    },
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            return {"status": "connected", "client_id": client_id}

        except Exception as e:
            error_msg = f"Erro ao carregar dados iniciais: {str(e)}"
            print(f"❌ {error_msg}")
            emit("error", {"message": error_msg})
            return {"status": "error", "message": str(e)}

    def on_disconnect(self):
        """Evento: Cliente desconectado"""
        client_id = request.sid

        if client_id in self.connected_clients:
            self.connected_clients.remove(client_id)

        print(
            f"🔌 Cliente desconectado: {client_id} (Total: {len(self.connected_clients)})"
        )

    def on_request_update(self):
        """Evento: Cliente solicitou atualização manual"""
        try:
            metrics = self.system_monitor.get_all_metrics()
            history = self.system_monitor.get_history()

            # Verificar alertas
            thresholds = {
                "cpu": self.config["CPU_ALERT_THRESHOLD"],
                "memory": self.config["MEMORY_ALERT_THRESHOLD"],
                "disk": self.config["DISK_ALERT_THRESHOLD"],
            }
            alerts = self.system_monitor.check_alerts(metrics, thresholds)

            emit(
                "system_metrics",
                {
                    "metrics": metrics,
                    "history": history,
                    "alerts": alerts,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            return {"status": "success"}

        except Exception as e:
            error_msg = f"Erro ao atualizar dados: {str(e)}"
            print(f"❌ {error_msg}")
            emit("error", {"message": error_msg})
            return {"status": "error", "message": str(e)}

    def on_pause_monitoring(self):
        """Evento: Cliente pausou o monitoramento"""
        print(f"⏸️  Monitoramento pausado para cliente: {request.sid}")
        emit(
            "monitoring_paused",
            {"status": "paused", "timestamp": datetime.now().isoformat()},
        )
        return {"status": "paused"}

    def on_resume_monitoring(self):
        """Evento: Cliente retomou o monitoramento"""
        print(f"▶️  Monitoramento retomado para cliente: {request.sid}")
        emit(
            "monitoring_resumed",
            {"status": "resumed", "timestamp": datetime.now().isoformat()},
        )
        return {"status": "resumed"}

    def broadcast_metrics(self, metrics, alerts):
        """Envia métricas para todos os clientes conectados"""
        if len(self.connected_clients) > 0:
            self.socketio.emit(
                "system_metrics",
                {
                    "metrics": metrics,
                    "alerts": alerts,
                    "history": self.system_monitor.get_history(),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    def broadcast_alert(self, alert):
        """Envia alerta específico para todos os clientes"""
        self.socketio.emit(
            "new_alert", {"alert": alert, "timestamp": datetime.now().isoformat()}
        )

    def get_connected_clients_count(self):
        """Retorna número de clientes conectados"""
        return len(self.connected_clients)

    def get_connected_clients(self):
        """Retorna lista de IDs dos clientes conectados"""
        return list(self.connected_clients)
