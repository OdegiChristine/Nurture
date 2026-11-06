from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.send_due_reminders", bind=True, max_retries=3)
def send_due_reminders(self) -> int:
    """TODO: find due reminders (respect quiet hours), send via ChannelGateway, mark sent."""
    return 0
