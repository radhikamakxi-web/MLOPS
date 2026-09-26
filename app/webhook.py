"""Best-effort HTTP webhook delivery."""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


def send_webhook(url: str, payload: dict[str, object], timeout: int = 5) -> bool:
    """POST JSON to a webhook URL without propagating delivery failures."""
    if not url:
        logger.debug("No webhook URL configured; skipping notification.")
        return False

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        logger.info("Webhook sent: %s | payload=%s", url, payload)
        return True
    except requests.RequestException as exc:
        logger.error("Webhook failed: %s | error=%s", url, exc)
        return False