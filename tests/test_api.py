"""In-process API tests; Docker is not required.

These tests use FastAPI's TestClient to exercise the endpoints directly in
memory. They run quickly and are ideal for CI because they do not need a
running server or container.
"""

from unittest.mock import Mock

from fastapi.testclient import TestClient

import app.main as main_module
from app.config import Settings

# TestClient wraps the FastAPI app so requests are handled in-process.
# The model is trained once when this module imports app.main.
client = TestClient(main_module.app)


def test_health_returns_ok() -> None:
    """GET /health should report the service is up and return the version."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_model_info_exposes_metadata() -> None:
    """GET /model/info should describe the trained linear model."""
    response = client.get("/model/info")
    assert response.status_code == 200
    assert response.json()["model_type"] == "LinearRegression"
    assert "rooms" in response.json()["features"]


def test_predict_returns_expected_value() -> None:
    """POST /predict with 3 rooms should return a price close to 300."""
    response = client.post("/predict", json={"rooms": 3})
    assert response.status_code == 200
    body = response.json()
    # Allow a tiny floating-point tolerance rather than exact equality.
    assert abs(body["predicted_price"] - 300.0) < 1e-6
    assert body["model_version"] == "0.1.0"


def test_predict_rejects_zero_rooms() -> None:
    """Zero rooms violates the gt=0 Pydantic constraint -> HTTP 422."""
    assert client.post("/predict", json={"rooms": 0}).status_code == 422


def test_predict_rejects_negative_rooms() -> None:
    """Negative rooms also violates gt=0 -> HTTP 422."""
    assert client.post("/predict", json={"rooms": -5}).status_code == 422


def test_predict_rejects_missing_field() -> None:
    """The required 'rooms' field must be present -> HTTP 422."""
    assert client.post("/predict", json={}).status_code == 422


def test_predict_rejects_wrong_type() -> None:
    """A string value for rooms cannot be parsed as float -> HTTP 422."""
    assert client.post("/predict", json={"rooms": "three"}).status_code == 422


def test_webhook_is_scheduled_after_prediction(monkeypatch) -> None:
    """When WEBHOOK_URL is set, /predict should schedule send_webhook."""
    # Mock the webhook sender so the test does not make real HTTP calls.
    webhook = Mock(return_value=True)

    # Override settings and the webhook function inside the app module for the
    # duration of this test. monkeypatch automatically restores them after.
    monkeypatch.setattr(
        main_module,
        "settings",
        Settings(webhook_url="http://receiver/anything/notify"),
    )
    monkeypatch.setattr(main_module, "send_webhook", webhook)

    response = client.post("/predict", json={"rooms": 3})

    assert response.status_code == 200
    # Assert the webhook was called exactly once with the expected arguments.
    webhook.assert_called_once_with(
        url="http://receiver/anything/notify",
        payload={
            "event": "prediction_completed",
            "input_rooms": 3.0,
            "predicted_price": response.json()["predicted_price"],
            "model_version": "0.1.0",
        },
        timeout=5,
    )