"""Best-effort HTTP webhook delivery.

A webhook is an HTTP callback: after a prediction is produced, the API posts
a JSON payload to a configured URL. This implementation is "best-effort"
because failures are logged but never returned to the client.
"""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


def send_webhook(url: str, payload: dict[str, object], timeout: int = 5) -> bool:
    """POST JSON to a webhook URL without propagating delivery failures.

    Args:
        url: The webhook endpoint. If empty, the function does nothing.
        payload: The JSON-serializable dictionary to send.
        timeout: Maximum seconds to wait for the HTTP response.

    Returns:
        True if the webhook returned a 2xx status, False otherwise.
    """
    # Guard against an empty WEBHOOK_URL. This keeps the endpoint simple:
    # the same code path works whether webhooks are enabled or not.
    if not url:
        logger.debug("No webhook URL configured; skipping notification.")
        return False

    try:
        # requests.post(..., json=...) serializes the dict and sets the
        # Content-Type header to application/json automatically.
        response = requests.post(url, json=payload, timeout=timeout)
        # raise_for_status() turns 4xx/5xx responses into an exception.
        response.raise_for_status()
        logger.info("Webhook sent: %s | payload=%s", url, payload)
        return True
    except requests.RequestException as exc:
        # Catch all requests errors (DNS, connection, timeout, HTTP errors).
        # Returning False instead of raising keeps the API response stable.
        logger.error("Webhook failed: %s | error=%s", url, exc)
        return False