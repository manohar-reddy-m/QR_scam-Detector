"""
Model status and metrics endpoints.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from core.config import settings

router = APIRouter()


class ModelStatusResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    loaded: bool
    model_type: Optional[str] = None
    training_dataset: Optional[str] = None
    num_features: Optional[int] = None
    feature_names: Optional[list] = None


class ModelMetricsResponse(BaseModel):
    available: bool
    metrics: Optional[Dict[str, Any]] = None


@router.get("/status", response_model=ModelStatusResponse, summary="ML model load status")
async def model_status(request: Request):
    """Returns whether the ML model is loaded and its metadata."""
    classifier = getattr(request.app.state, "classifier", None)
    if classifier is None or not classifier.is_loaded:
        return ModelStatusResponse(loaded=False)

    info = classifier.get_info()
    return ModelStatusResponse(
        loaded=True,
        model_type=info.get("model_type"),
        training_dataset=info.get("training_dataset"),
        num_features=info.get("num_features"),
        feature_names=info.get("feature_names"),
    )


@router.get("/metrics", response_model=ModelMetricsResponse, summary="Training metrics")
async def model_metrics():
    """Returns the training metrics from the last training run."""
    metrics_path = Path(settings.MODEL_DIR) / settings.TRAINING_METRICS_FILE
    if not metrics_path.exists():
        return ModelMetricsResponse(available=False)
    try:
        with open(metrics_path) as f:
            metrics = json.load(f)
        return ModelMetricsResponse(available=True, metrics=metrics)
    except Exception:
        return ModelMetricsResponse(available=False)
