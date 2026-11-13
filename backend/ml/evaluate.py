"""
ML Evaluation Script — QR Sentinel
Evaluates the saved model on a fresh synthetic test set.

Usage:
    python backend/ml/evaluate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)

SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR.parent
MODELS_DIR = BACKEND_DIR / "models"
sys.path.insert(0, str(BACKEND_DIR))

from ml.feature_schema import FEATURE_NAMES
from ml.train import generate_synthetic_dataset


def evaluate():
    print("QR Sentinel — Model Evaluation")
    print("=" * 50)

    model_path = MODELS_DIR / "threat_classifier.joblib"
    pipeline_path = MODELS_DIR / "preprocessing_pipeline.joblib"

    if not model_path.exists():
        print("ERROR: Model not found. Run train.py first.")
        sys.exit(1)

    model = joblib.load(model_path)
    scaler = joblib.load(pipeline_path) if pipeline_path.exists() else None

    # Fresh test set (not seen during training)
    df = generate_synthetic_dataset(n_samples=2000)
    X = df[FEATURE_NAMES].values
    y = df["label"].values

    if scaler is not None:
        X_scaled = scaler.transform(X)
    else:
        X_scaled = X

    y_pred = model.predict(X_scaled)
    y_proba = model.predict_proba(X_scaled)[:, 1]

    f1 = f1_score(y, y_pred)
    auc = roc_auc_score(y, y_proba)

    print(f"Test F1 Score : {f1:.4f}")
    print(f"Test ROC-AUC  : {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y, y_pred, target_names=["Benign", "Malicious"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y, y_pred))
    print("\n⚠️  SYNTHETIC_DEMO — results reflect synthetic test data only.")


if __name__ == "__main__":
    evaluate()
