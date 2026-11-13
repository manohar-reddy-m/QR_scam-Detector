"""
ML Training Script — QR Sentinel Threat Classifier
====================================================
⚠️  SYNTHETIC_DEMO DATASET — NOT real-world data.
    This dataset is generated algorithmically for demonstration and
    development purposes only. Do NOT use this model in production
    without retraining on verified, real-world labeled data.

Usage:
    python backend/ml/train.py
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    f1_score,
    roc_auc_score,
    accuracy_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR.parent
MODELS_DIR = BACKEND_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(BACKEND_DIR))
from ml.feature_schema import FEATURE_NAMES, NUM_FEATURES

# ---------------------------------------------------------------------------
# Synthetic Dataset Generation with Realistic Distributions
# ---------------------------------------------------------------------------
DATASET_LABEL = "SYNTHETIC_DEMO"
N_SAMPLES = 5000
RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)


def _safe_url(n: int = 1) -> np.ndarray:
    """Generate feature rows for benign (safe) URLs with realistic variation."""
    rows = []
    for _ in range(n):
        # Benign URLs can be short (25 chars) or long search/wiki queries (up to 250 chars)
        url_length = int(rng.normal(90, 45))
        url_length = max(20, min(300, url_length))
        hostname_length = int(rng.normal(16, 6))
        hostname_length = max(6, min(40, hostname_length))
        num_subdomains = int(rng.choice([0, 1, 2], p=[0.6, 0.35, 0.05]))
        has_https = int(rng.random() < 0.92)  # 92% of benign web is HTTPS
        has_ip_host = 0  # Safe consumer URLs don't use raw IPs
        num_dots = int(rng.choice([1, 2, 3, 4], p=[0.4, 0.4, 0.15, 0.05]))
        num_hyphens = int(rng.choice([0, 1, 2], p=[0.65, 0.25, 0.10]))
        num_at = 0  # No @ symbol in benign web URLs
        num_question_marks = int(rng.choice([0, 1], p=[0.65, 0.35]))
        num_ampersands = int(rng.choice([0, 1, 2, 3], p=[0.6, 0.25, 0.10, 0.05]))
        num_percent_encoded = int(rng.choice([0, 1, 2], p=[0.8, 0.15, 0.05]))
        path_length = int(rng.normal(25, 15))
        path_length = max(0, min(120, path_length))
        query_length = int(rng.normal(15, 20)) if num_question_marks > 0 else 0
        query_length = max(0, min(100, query_length))
        is_shortened_url = int(rng.random() < 0.03)  # Occasional legit shortener
        has_suspicious_tld = 0  # Benign URLs use mainstream TLDs
        has_punycode = 0
        has_double_slash = 0
        special_char_ratio = float(rng.beta(1.5, 25))
        digit_ratio = float(rng.beta(1, 15))

        rows.append([
            url_length, hostname_length, num_subdomains, has_https, has_ip_host,
            num_dots, num_hyphens, num_at, num_question_marks, num_ampersands,
            num_percent_encoded, path_length, query_length, is_shortened_url,
            has_suspicious_tld, has_punycode, has_double_slash, special_char_ratio,
            digit_ratio,
        ])
    return np.array(rows, dtype=float)


def _malicious_url(n: int = 1) -> np.ndarray:
    """Generate feature rows for malicious/phishing URLs."""
    rows = []
    for _ in range(n):
        # Diverse attack archetypes: IP host, free TLD phishing, shortener quish, punycode, credential theft
        attack_type = rng.choice(["ip_host", "suspicious_tld", "shortener", "punycode", "credential_at", "deep_subdomain"])

        has_ip_host = 1 if attack_type == "ip_host" or rng.random() < 0.20 else 0
        has_suspicious_tld = 1 if (not has_ip_host and (attack_type == "suspicious_tld" or rng.random() < 0.35)) else 0
        is_shortened_url = 1 if attack_type == "shortener" or rng.random() < 0.22 else 0
        has_punycode = 1 if attack_type == "punycode" or rng.random() < 0.12 else 0
        num_at = 1 if attack_type == "credential_at" or rng.random() < 0.15 else 0

        # Malicious URLs can be very short (e.g. http://1.2.3.4 or bit.ly) or very long
        if is_shortened_url or (has_ip_host and rng.random() < 0.5):
            url_length = int(rng.normal(35, 12))
        else:
            url_length = int(rng.normal(140, 50))
        url_length = max(15, min(400, url_length))

        hostname_length = int(rng.normal(26, 10))
        hostname_length = max(8, min(65, hostname_length))

        num_subdomains = int(rng.choice([0, 1, 2, 3, 4], p=[0.15, 0.25, 0.30, 0.20, 0.10]))
        if attack_type == "deep_subdomain":
            num_subdomains = int(rng.choice([3, 4, 5]))

        has_https = int(rng.random() < 0.38)  # High prevalence of unencrypted HTTP in quishing
        num_dots = int(rng.normal(4.5, 1.8))
        num_dots = max(1, min(12, num_dots))
        num_hyphens = int(rng.choice([0, 1, 2, 3, 4], p=[0.25, 0.30, 0.25, 0.12, 0.08]))
        num_question_marks = int(rng.choice([0, 1, 2], p=[0.4, 0.45, 0.15]))
        num_ampersands = int(rng.choice([0, 1, 2, 3, 4], p=[0.3, 0.3, 0.2, 0.15, 0.05]))
        num_percent_encoded = int(rng.choice([0, 1, 2, 4, 6], p=[0.3, 0.25, 0.2, 0.15, 0.1]))

        path_length = int(rng.normal(45, 25))
        path_length = max(0, min(180, path_length))
        query_length = int(rng.normal(35, 30)) if num_question_marks > 0 else 0
        query_length = max(0, min(150, query_length))

        has_double_slash = int(rng.random() < 0.18)
        special_char_ratio = float(rng.beta(2.5, 12))
        digit_ratio = float(rng.beta(2, 8))

        rows.append([
            url_length, hostname_length, num_subdomains, has_https, has_ip_host,
            num_dots, num_hyphens, num_at, num_question_marks, num_ampersands,
            num_percent_encoded, path_length, query_length, is_shortened_url,
            has_suspicious_tld, has_punycode, has_double_slash, special_char_ratio,
            digit_ratio,
        ])
    return np.array(rows, dtype=float)


def generate_synthetic_dataset(n_samples: int = N_SAMPLES) -> pd.DataFrame:
    """Generate balanced synthetic dataset."""
    n_safe = n_samples // 2
    n_mal = n_samples - n_safe

    X_safe = _safe_url(n_safe)
    y_safe = np.zeros(n_safe, dtype=int)

    X_mal = _malicious_url(n_mal)
    y_mal = np.ones(n_mal, dtype=int)

    X = np.vstack([X_safe, X_mal])
    y = np.concatenate([y_safe, y_mal])

    df = pd.DataFrame(X, columns=FEATURE_NAMES)
    df["label"] = y
    df["dataset"] = DATASET_LABEL

    # Shuffle
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Training Pipeline
# ---------------------------------------------------------------------------

def train() -> Dict[str, Any]:
    print("=" * 60)
    print("QR Sentinel — ML Training Pipeline")
    print(f"Dataset: {DATASET_LABEL}")
    print("=" * 60)

    # 1. Generate dataset
    print(f"\n[1/5] Generating balanced synthetic dataset ({N_SAMPLES} samples)...")
    df = generate_synthetic_dataset(N_SAMPLES)
    X = df[FEATURE_NAMES].values
    y = df["label"].values
    print(f"       Safe: {(y == 0).sum()}, Malicious: {(y == 1).sum()}")

    # 2. Train/val split (80/20)
    print("[2/5] Splitting train/validation sets (80/20)...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    # 3. Preprocessing pipeline (StandardScaler)
    print("[3/5] Building preprocessing pipeline...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    # 4. Train candidate models
    print("[4/5] Training RandomForest and LogisticRegression...")
    candidates = {
        "RandomForest": RandomForestClassifier(
            n_estimators=80,
            max_depth=10,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=1,
        ),
        "LogisticRegression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            C=1.0,
        ),
    }

    best_name = None
    best_f1 = -1.0
    best_model = None
    all_metrics: Dict[str, Any] = {}

    for name, clf in candidates.items():
        if name == "LogisticRegression":
            clf.fit(X_train_scaled, y_train)
            y_pred = clf.predict(X_val_scaled)
            y_proba = clf.predict_proba(X_val_scaled)[:, 1]
        else:
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_val)
            y_proba = clf.predict_proba(X_val)[:, 1]

        f1 = f1_score(y_val, y_pred)
        auc = roc_auc_score(y_val, y_proba)
        acc = accuracy_score(y_val, y_pred)
        report = classification_report(y_val, y_pred, output_dict=True)

        all_metrics[name] = {
            "f1": round(f1, 4),
            "roc_auc": round(auc, 4),
            "accuracy": round(acc, 4),
            "classification_report": report,
        }
        print(f"       {name}: F1={f1:.4f}, AUC={auc:.4f}, Acc={acc:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = clf

    print(f"\n       Best model: {best_name} (F1={best_f1:.4f})")

    # 5. Calibrate probabilities using Isotonic / Sigmoid
    print("[5/5] Calibrating and persisting model artifacts...")
    if best_name == "LogisticRegression":
        raw_clf = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_SEED)
        calibrated = CalibratedClassifierCV(raw_clf, method="sigmoid", cv=3)
        calibrated.fit(X_train_scaled, y_train)
    else:
        calibrated = CalibratedClassifierCV(best_model, method="isotonic", cv=3)
        calibrated.fit(X_train, y_train)

    # Save artifacts
    model_path = MODELS_DIR / "threat_classifier.joblib"
    joblib.dump(calibrated, model_path)
    print(f"       Saved model → {model_path}")

    pipeline_path = MODELS_DIR / "preprocessing_pipeline.joblib"
    joblib.dump(scaler, pipeline_path)
    print(f"       Saved pipeline → {pipeline_path}")

    schema = {
        "dataset_label": DATASET_LABEL,
        "model_type": best_name,
        "num_features": NUM_FEATURES,
        "feature_names": FEATURE_NAMES,
        "calibration_method": "isotonic" if best_name == "RandomForest" else "sigmoid",
        "train_samples": int(X_train.shape[0]),
        "val_samples": int(X_val.shape[0]),
        "warning": "SYNTHETIC_DEMO — retrain on verified threat feeds before production use.",
    }
    with open(MODELS_DIR / "feature_schema.json", "w") as f:
        json.dump(schema, f, indent=2)

    metrics = {
        "dataset_label": DATASET_LABEL,
        "best_model": best_name,
        "best_f1": round(best_f1, 4),
        "models": all_metrics,
        "warning": "SYNTHETIC_DEMO — metrics reflect synthetic validation set only.",
    }
    with open(MODELS_DIR / "training_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Training complete! Model: {best_name} (F1={best_f1:.4f})")
    print("=" * 60)
    return metrics


if __name__ == "__main__":
    train()
