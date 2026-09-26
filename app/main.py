"""FastAPI application entry point."""

from __future__ import annotations

import logging

from fastapi import BackgroundTasks, FastAPI, status

from app.config import settings
from app.model import HousePriceModel
from app.schemas import (
    HealthResponse,
    PredictRequest,
    PredictResponse,
    WebhookPayload,
)
from app.webhook import send_webhook

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Teaching demo: ML model served with FastAPI, Docker, and webhooks.",
)
model = HousePriceModel()


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    tags=["ops"],
)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.app_version)


@app.get("/model/info", summary="Model metadata", tags=["ml"])
def model_info() -> dict[str, object]:
    return model.metadata()


@app.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict house price",
    tags=["ml"],
)
def predict(
    req: PredictRequest,
    background_tasks: BackgroundTasks,
) -> PredictResponse:
    logger.info("Received prediction request: rooms=%.2f", req.rooms)
    price = model.predict(req.rooms)

    if settings.webhook_url:
        payload = WebhookPayload(
            event="prediction_completed",
            input_rooms=req.rooms,
            predicted_price=price,
            model_version=settings.app_version,
        )
        background_tasks.add_task(
            send_webhook,
            url=settings.webhook_url,
            payload=payload.model_dump(),
            timeout=settings.webhook_timeout,
        )
    else:
        logger.debug("Webhook disabled (WEBHOOK_URL not set).")

    return PredictResponse(
        predicted_price=price,
        model_version=settings.app_version,
    )