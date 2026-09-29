"""Environment-backed configuration for the MLOps demo.

This module centralizes every setting that can change between environments
(development, Docker, Compose, CI). Values are read from environment
variables so the same code can run locally and inside a container without
modification.
"""

from dataclasses import dataclass
import os


# frozen=True makes the settings object immutable after creation. This is a
# small safety measure: once loaded, configuration should not change at runtime.
@dataclass(frozen=True)
class Settings:
    # Human-readable name shown in the FastAPI docs.
    app_name: str = "MLOps Demo API"
    # Version reported by /health and /predict. Override with APP_VERSION.
    app_version: str = "0.1.0"
    # URL where prediction events are posted as webhooks. Empty string disables
    # webhook delivery. In Compose this is set to the httpbin receiver service.
    webhook_url: str = ""
    # Seconds to wait for the webhook HTTP POST before giving up.
    webhook_timeout: int = 5
    # Python logging level: DEBUG, INFO, WARNING, ERROR, or CRITICAL.
    log_level: str = "INFO"


def load_settings() -> Settings:
    """Build a Settings instance from environment variables.

    os.getenv reads a variable; the second argument is the default used when
    the variable is not set. This lets the app start with sensible defaults
    while still allowing overrides through the environment.
    """
    return Settings(
        app_name=os.getenv("APP_NAME", "MLOps Demo API"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        webhook_url=os.getenv("WEBHOOK_URL", ""),
        # WEBHOOK_TIMEOUT comes in as a string, so convert it to int.
        webhook_timeout=int(os.getenv("WEBHOOK_TIMEOUT", "5")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


# Load settings once when this module is imported. main.py imports this object
# so the rest of the application can read configuration without reloading it.
settings = load_settings()