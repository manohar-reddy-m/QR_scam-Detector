"""
Threat classifier — ML inference service.
Loads the trained RandomForest/LogisticRegression model from disk.
Exposes a singleton `classifier_service` used by main.py and endpoints.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class ThreatClassifier:
    """Loads and runs ML inference for URL threat classification."""

    def __init__(self):
        self._model = None
        self._pipeline = None
        self._feature_schema: Dict[str, Any] = {}
        self._metrics: Dict[str, Any] = {}
        self.is_loaded = False

    def load(self) -> None:
        """Load model artifacts from the models directory."""
        model_dir = Path(settings.MODEL_DIR)
        model_path = model_dir / settings.MODEL_FILE
        pipeline_path = model_dir / settings.PIPELINE_FILE
        schema_path = model_dir / settings.FEATURE_SCHEMA_FILE
        metrics_path = model_dir / settings.TRAINING_METRICS_FILE

        if not model_path.exists():
            logger.warning("Model file not found", path=str(model_path))
            return

        self._model = joblib.load(model_path)
        logger.info("Loaded threat classifier model", path=str(model_path))

        if pipeline_path.exists():
            self._pipeline = joblib.load(pipeline_path)
            logger.info("Loaded preprocessing pipeline", path=str(pipeline_path))

        if schema_path.exists():
            with open(schema_path) as f:
                self._feature_schema = json.load(f)

        if metrics_path.exists():
            with open(metrics_path) as f:
                self._metrics = json.load(f)

        self.is_loaded = True

    # Alias used by main.py lifespan
    load_model = load

    def predict_proba(self, feature_vector: np.ndarray) -> float:
        """Return probability of malicious class (0–1)."""
        if not self.is_loaded or self._model is None:
            raise RuntimeError("Model is not loaded.")

        X = feature_vector
        # Only apply pipeline if model doesn't include its own scaler
        # (CalibratedClassifierCV wrapping Pipeline handles scaling internally)
        # So we pass raw features directly
        proba = self._model.predict_proba(X)
        # Class 1 = malicious
        return float(proba[0][1])

    def get_info(self) -> Dict[str, Any]:
        return {
            "model_type": self._feature_schema.get("model_type", type(self._model).__name__ if self._model else "unknown"),
            "training_dataset": self._feature_schema.get("dataset_label", "SYNTHETIC_DEMO"),
            "num_features": self._feature_schema.get("num_features", 19),
            "feature_names": self._feature_schema.get("feature_names", []),
            "model_version": self._metrics.get("best_model", "unknown"),
            "training_date": self._metrics.get("models", {}).get(
                self._feature_schema.get("model_type", ""), {}
            ),
        }

    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics


# Global singleton used by endpoints and main.py
classifier_service = ThreatClassifier()
