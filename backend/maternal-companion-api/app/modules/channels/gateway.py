"""Outbound messaging abstraction. Business logic depends on this Protocol, not on a provider.

TODO: implement `AfricasTalkingSmsGateway` and `WhatsAppCloudGateway` (template sends for
reminders outside the 24-hour window) -- check each provider's current API docs when you do.
"""

from typing import Protocol

import structlog

log = structlog.get_logger()


class ChannelGateway(Protocol):
    async def send_text(self, to_msisdn: str, body: str) -> None: ...

    async def send_template(self, to_msisdn: str, template: str, params: list[str]) -> None: ...


class LoggingGateway:
    """Local/dev gateway: records that a send happened, never the number or content."""

    async def send_text(self, to_msisdn: str, body: str) -> None:
        log.info("gateway_send_text", length=len(body))

    async def send_template(self, to_msisdn: str, template: str, params: list[str]) -> None:
        log.info("gateway_send_template", template=template, n_params=len(params))
