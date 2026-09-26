"""Pydantic request and response models for the API."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    rooms: float = Field(
        gt=0,
        description="Number of rooms. Must be greater than 0.",
        examples=[3.0],
    )


class PredictResponse(BaseModel):
    predicted_price: float
    model_version: str = "0.1.0"


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class WebhookPayload(BaseModel):
    event: str
    input_rooms: float
    predicted_price: float
    model_version: str