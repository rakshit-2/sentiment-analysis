"""
Celery application configuration for background task processing.
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
celery_app = Celery(
    "sentiment_analysis",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.analysis_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic task schedule (Celery Beat)
celery_app.conf.beat_schedule = {
    "analyze-transcripts-every-2-hours": {
        "task": "app.tasks.analysis_tasks.analyze_unprocessed_transcripts",
        "schedule": crontab(minute=0, hour="*/2"),  # Every 2 hours
        "options": {"expires": 3600},  # Expires after 1 hour if not executed
    },
}

if __name__ == "__main__":
    celery_app.start()
