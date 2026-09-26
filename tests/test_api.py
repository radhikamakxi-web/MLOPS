"""In-process API tests; Docker is not required."""

from unittest.mock import Mock

from fastapi.testclient import TestClient

import app.main as main_module
from app.config import Settings

client = TestClient(main_module.app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_model_info_exposes_metadata() -> None:
    response = client.get("/model/info")
    assert response.status_code == 200
    assert response.json()["model_type"] == "LinearRegression"
    assert "rooms" in response.json()["features"]


def test_predict_returns_expected_value() -> None:
    response = client.post("/predict", json={"rooms": 3})
    assert response.status_code == 200
    body = response.json()
    assert abs(body["predicted_price"] - 300.0) < 1e-6
    assert body["model_version"] == "0.1.0"


def test_predict_rejects_zero_rooms() -> None:
    assert client.post("/predict", json={"rooms": 0}).status_code == 422


def test_predict_rejects_negative_rooms() -> None:
    assert client.post("/predict", json={"rooms": -5}).status_code == 422


def test_predict_rejects_missing_field() -> None:
    assert client.post("/predict", json={}).status_code == 422


def test_predict_rejects_wrong_type() -> None:
    assert client.post("/predict", json={"rooms": "three"}).status_code == 422


def test_webhook_is_scheduled_after_prediction(monkeypatch) -> None:
    webhook = Mock(return_value=True)
    monkeypatch.setattr(main_module, "settings", Settings(webhook_url="http://receiver/anything/notify"))
    monkeypatch.setattr(main_module, "send_webhook", webhook)

    response = client.post("/predict", json={"rooms": 3})

    assert response.status_code == 200
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