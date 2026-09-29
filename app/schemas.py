"""Pydantic request and response models for the API.

Pydantic models define the shape of JSON data going in and out of the API.
FastAPI uses them for automatic validation, serialization, and OpenAPI docs.
"""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Body expected by POST /predict."""

    # Field(...) adds validation rules and metadata to the schema.
    # gt=0 means "greater than 0"; FastAPI returns 422 for 0 or negative values.
    rooms: float = Field(
        gt=0,
        description="Number of rooms. Must be greater than 0.",
        examples=[3.0],
    )


class PredictResponse(BaseModel):
    """Body returned by POST /predict."""

    predicted_price: float
    # Including the version lets clients know which model artifact produced
    # the prediction. In a real system this would match a trained model tag.
    model_version: str = "0.1.0"


class HealthResponse(BaseModel):
    """Body returned by GET /health."""

    status: str = "ok"
    version: str = "0.1.0"


class WebhookPayload(BaseModel):
    """JSON payload sent to the webhook receiver after a prediction."""

    event: str
    input_rooms: float
    predicted_price: float
    model_version: str