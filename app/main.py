"""FastAPI application entry point.

This module creates the FastAPI app, loads configuration, instantiates the
machine-learning model, and defines the HTTP endpoints. When uvicorn loads
this module, the model is trained automatically (see HousePriceModel.__init__).
"""

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

# Configure Python's logging system once at startup. The level comes from the
# LOG_LEVEL environment variable (default INFO). The format includes a
# timestamp, level, logger name, and message.
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI application. The metadata here appears in the automatic
# OpenAPI documentation at /docs and /openapi.json.
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Teaching demo: ML model served with FastAPI, Docker, and webhooks.",
)

# Instantiate the model at module load time. This is the "automatic training"
# step: HousePriceModel.__init__ calls LinearRegression().fit(...) immediately,
# so the model is ready before the first request arrives.
model = HousePriceModel()


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    tags=["ops"],
)
def health() -> HealthResponse:
    """Return service health and version.

    Load balancers and orchestrators (like Kubernetes) use this endpoint to
    decide whether the container is alive and should receive traffic.
    """
    return HealthResponse(status="ok", version=settings.app_version)


@app.get("/model/info", summary="Model metadata", tags=["ml"])
def model_info() -> dict[str, object]:
    """Return model type, features, target, coefficient, and intercept."""
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
    """Predict a house price from the number of rooms.

    FastAPI validates the request body against PredictRequest before this
    function runs. If validation fails, the client receives HTTP 422.
    """
    logger.info("Received prediction request: rooms=%.2f", req.rooms)

    # Use the pre-trained model to compute the price.
    price = model.predict(req.rooms)

    # If a webhook URL is configured, schedule the notification as a
    # background task. BackgroundTasks runs the function after the response
    # has already been sent, so webhook latency does not delay the client.
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
            # model_dump() converts the Pydantic model to a plain dictionary
            # that requests can serialize as JSON.
            payload=payload.model_dump(),
            timeout=settings.webhook_timeout,
        )
    else:
        logger.debug("Webhook disabled (WEBHOOK_URL not set).")

    # Return the prediction to the client. The response is validated against
    # PredictResponse and serialized to JSON automatically.
    return PredictResponse(
        predicted_price=price,
        model_version=settings.app_version,
    )