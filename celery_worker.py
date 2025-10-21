"""
Celery Worker - Processa tasks em background
"""

from tasks import celery_app

if __name__ == "__main__":
    # Iniciar worker
    celery_app.worker_main(["worker", "--loglevel=info", "--pool=solo"])  # Para Windows
