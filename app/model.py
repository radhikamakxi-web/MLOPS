"""Toy linear regression model used by the inference API.

The model is intentionally tiny: five synthetic examples that map room count
to price. This keeps the focus on MLOps tooling (API, Docker, webhooks)
rather than on model complexity.
"""

from __future__ import annotations

import logging

import numpy as np
from sklearn.linear_model import LinearRegression

# __name__ is "app.model" here. Using it creates a logger tied to this module.
logger = logging.getLogger(__name__)


class HousePriceModel:
    """Fit and serve a linear mapping from room count to price."""

    def __init__(self) -> None:
        # Synthetic training data: 1 room -> 100, 2 rooms -> 200, etc.
        # scikit-learn expects a 2-D array for X (one row per sample).
        features = np.array([[1], [2], [3], [4], [5]], dtype=float)
        # y is the target vector (one value per sample).
        prices = np.array([100, 200, 300, 400, 500], dtype=float)

        # LinearRegression().fit(...) finds the best-fit line through the data.
        # Because the toy data is perfectly linear, the coefficient will be 100
        # and the intercept will be 0.
        self._model = LinearRegression().fit(features, prices)
        logger.info("HousePriceModel initialized and fitted on toy data")

    def predict(self, rooms: float) -> float:
        """Return the predicted price for a given number of rooms."""
        # The model expects a 2-D array even for a single prediction.
        prediction = self._model.predict(np.array([[rooms]], dtype=float))
        price = float(prediction[0])
        logger.debug("Predicted price=%.2f for rooms=%.2f", price, rooms)
        return price

    def metadata(self) -> dict[str, object]:
        """Expose model details for the /model/info endpoint."""
        return {
            "model_type": "LinearRegression",
            "features": ["rooms"],
            "target": "price",
            # coef_ and intercept_ are NumPy arrays; cast to float for JSON.
            "coefficient": float(self._model.coef_[0]),
            "intercept": float(self._model.intercept_),
        }