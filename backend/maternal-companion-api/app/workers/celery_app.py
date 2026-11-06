"""Celery worker (install with `pip install -e ".[workers]"`).

Run:  celery -A app.workers.celery_app worker -B -l info

Starter only. Real tasks to add: send_due_reminders (quiet hours, East Africa Time),
notify_chp_of_alert with retries/DLQ and supervisor escalation, flag_disengaged_mothers.
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("maternal", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    timezone="UTC",  # store/schedule in UTC; convert to EAT only when choosing send times
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
celery_app.conf.beat_schedule = {
    "send-due-reminders": {"task": "app.workers.tasks.send_due_reminders", "schedule": 300.0},
}
celery_app.autodiscover_tasks(["app.workers"])
