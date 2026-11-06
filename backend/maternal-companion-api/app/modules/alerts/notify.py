"""Delivery of CHP notifications.

Starter implementation only logs. Replace with: SMS/WhatsApp-template send through a
ChannelGateway, run from a Celery task with retries + dead-letter queue, and an escalation
timer (e.g. re-notify the supervisor if an Emergency alert is unacknowledged for N minutes).
A silent failure here is a clinical risk: alert on it.
"""

import uuid

import structlog

log = structlog.get_logger()


async def notify_chp_of_alert(alert_id: uuid.UUID) -> None:
    log.info("alert_notification_queued", alert_id=str(alert_id))
