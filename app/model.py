"""Toy linear regression model used by the inference API."""

from __future__ import annotations

import logging

import numpy as np
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)


class HousePriceModel:
    """Fit and serve a linear mapping from room count to price."""

    def __init__(self) -> None:
        features = np.array([[1], [2], [3], [4], [5]], dtype=float)
        prices = np.array([100, 200, 300, 400, 500], dtype=float)
        self._model = LinearRegression().fit(features, prices)
        logger.info("HousePriceModel initialized and fitted on toy data")

    def predict(self, rooms: float) -> float:
        prediction = self._model.predict(np.array([[rooms]], dtype=float))
        price = float(prediction[0])
        logger.debug("Predicted price=%.2f for rooms=%.2f", price, rooms)
        return price

    def metadata(self) -> dict[str, object]:
        return {
            "model_type": "LinearRegression",
            "features": ["rooms"],
            "target": "price",
            "coefficient": float(self._model.coef_[0]),
            "intercept": float(self._model.intercept_),
        }