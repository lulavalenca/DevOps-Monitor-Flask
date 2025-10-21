from monitoring import SystemMonitor
from websocket_handler import WebSocketHandler
from config import Config
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import threading
import time
from datetime import datetime
from tasks import save_metrics_to_redis, send_alert


# Inicializar Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar SocketIO
socketio = SocketIO(
    app, cors_allowed_origins="*", async_mode=Config.SOCKETIO_ASYNC_MODE
)

# Instância global do monitor
system_monitor = SystemMonitor()

# Instância do WebSocket Handler
ws_handler = WebSocketHandler(socketio, system_monitor, app.config)

# Thread para monitoramento contínuo
monitoring_thread = None
monitoring_active = False


class MonitoringThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        global monitoring_active
        monitoring_active = True

        print("🔄 Thread de monitoramento iniciada")

        while monitoring_active:
            try:
                # Coletar métricas
                metrics = system_monitor.get_all_metrics()

                # Verificar alertas
                thresholds = {
                    "cpu": app.config["CPU_ALERT_THRESHOLD"],
                    "memory": app.config["MEMORY_ALERT_THRESHOLD"],
                    "disk": app.config["DISK_ALERT_THRESHOLD"],
                }
                alerts = system_monitor.check_alerts(metrics, thresholds)

                # Broadcast para todos os clientes conectados
                ws_handler.broadcast_metrics(metrics, alerts)

                # Log de clientes conectados (a cada minuto)
                if int(time.time()) % 60 == 0:
                    client_count = ws_handler.get_connected_clients_count()
                    if client_count > 0:
                        print(f"📊 Clientes conectados: {client_count}")

                # Aguardar próximo ciclo
                time.sleep(app.config["MONITORING_INTERVAL"])

            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(5)


# Routes da API REST
@app.route("/")
def index():
    """Página principal do dashboard"""
    return render_template("index.html")


@app.route("/api/metrics")
def get_metrics():
    """API REST para obter métricas atuais"""
    try:
        metrics = system_monitor.get_all_metrics()
        return jsonify(
            {
                "status": "success",
                "data": metrics,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/history")
def get_history():
    """API REST para obter histórico de métricas"""
    try:
        history = system_monitor.get_history()
        return jsonify(
            {
                "status": "success",
                "data": history,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/clients")
def get_clients():
    """API REST para obter clientes conectados"""
    try:
        clients = ws_handler.get_connected_clients()
        return jsonify(
            {
                "status": "success",
                "data": {"count": len(clients), "clients": clients},
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "DevOps Monitor",
            "version": "1.0.0",
            "clients_connected": ws_handler.get_connected_clients_count(),
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/test-celery")
def test_celery():
    """Testar Celery - Dispara uma task de teste"""
    try:
        # Disparar task assincrona
        result = save_metrics_to_redis.delay(
            {"test": "data", "timestamp": datetime.now().isoformat()}
        )

        return jsonify(
            {
                "status": "success",
                "message": "Task Celery disparada!",
                "task_id": result.id,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def start_monitoring():
    """Inicia thread de monitoramento"""
    global monitoring_thread
    if monitoring_thread is None:
        monitoring_thread = MonitoringThread()
        monitoring_thread.start()


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 DevOps Monitor - Sistema de Monitoramento em Tempo Real")
    print("=" * 70)

    # Iniciar monitoramento
    start_monitoring()

    print("\n📊 Dashboard: http://localhost:5000")
    print("🔌 WebSocket: ws://localhost:5000")
    print("📡 API REST: http://localhost:5000/api/*")
    print("\n🔄 Monitoramento ativo a cada 5 segundos")
    print("\n⚡ Endpoints disponíveis:")
    print("  • GET  /              - Dashboard web")
    print("  • GET  /api/metrics   - Métricas atuais")
    print("  • GET  /api/history   - Histórico de dados")
    print("  • GET  /api/clients   - Clientes conectados")
    print("  • GET  /api/health    - Status do sistema")
    print("\nPressione Ctrl+C para parar o servidor")
    print("=" * 70)

    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
