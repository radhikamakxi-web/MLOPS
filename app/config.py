"""Environment-backed configuration for the MLOps demo."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "MLOps Demo API"
    app_version: str = "0.1.0"
    webhook_url: str = ""
    webhook_timeout: int = 5
    log_level: str = "INFO"


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "MLOps Demo API"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        webhook_url=os.getenv("WEBHOOK_URL", ""),
        webhook_timeout=int(os.getenv("WEBHOOK_TIMEOUT", "5")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


settings = load_settings()