from celery import Celery
from datetime import datetime
import redis
import json
import os

# Inicializar Celery
celery_app = Celery("devops_monitor")
celery_app.config_from_object("config.Config", namespace="CELERY")

# Conexão Redis via variável de ambiente (Docker usa 'redis', local usa 'localhost')
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(REDIS_URL)


@celery_app.task(name="tasks.save_metrics_to_redis")
def save_metrics_to_redis(metrics):
    """
    Salva métricas no Redis de forma assíncrona
    """
    try:
        timestamp = datetime.now().isoformat()
        key = f"metrics:{timestamp}"

        # Salvar no Redis com TTL de 1 hora
        redis_client.setex(key, 3600, json.dumps(metrics))  # 1 hora

        print(f"✅ Métricas salvas no Redis: {key}")
        return {"status": "success", "key": key}

    except Exception as e:
        print(f"❌ Erro ao salvar métricas: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="tasks.send_alert")
def send_alert(alert_data):
    """
    Envia alerta (placeholder para email/slack/teams)
    """
    try:
        print(f"🚨 ALERTA DISPARADO:")
        print(f"   Tipo: {alert_data.get('type')}")
        print(f"   Nível: {alert_data.get('level')}")
        print(f"   Mensagem: {alert_data.get('message')}")
        # Aqui você pode adicionar integração real com:
        # - Email (SMTP)
        # - Slack (webhook)
        # - Microsoft Teams (webhook)
        return {"status": "sent", "alert": alert_data}
    except Exception as e:
        print(f"❌ Erro ao enviar alerta: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="tasks.cleanup_old_metrics")
def cleanup_old_metrics():
    """
    Limpa métricas antigas do Redis
    """
    try:
        # Buscar todas as chaves de métricas
        keys = redis_client.keys("metrics:*")
        # Deletar chaves mais antigas que 24h
        deleted = 0
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl < 0:  # Sem TTL ou expirada
                redis_client.delete(key)
                deleted += 1
        print(f"🧹 Limpeza concluída: {deleted} métricas antigas removidas")
        return {"status": "success", "deleted": deleted}
    except Exception as e:
        print(f"❌ Erro na limpeza: {e}")
        return {"status": "error", "message": str(e)}
