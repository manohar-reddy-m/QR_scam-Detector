# 🤖 QR Sentinel — ML Pipeline

> [!CAUTION]
> ## ⚠️ CRITICAL DISCLAIMER — SYNTHETIC TRAINING DATA
>
> **This model was trained exclusively on SYNTHETICALLY GENERATED data.**
>
> - No real phishing URLs, no real benign URLs, no real QR threat intelligence was used.
> - The synthetic dataset was algorithmically constructed to resemble what malicious/benign URLs might look like based on documented heuristics.
> - **Performance on real-world QR code threats is UNKNOWN and likely to be significantly lower than reported metrics.**
> - **Do NOT use this model as the sole or primary defense mechanism for production security decisions.**
> - Treat the reported accuracy/F1 scores as "performance on synthetic test data" only.
>
> See [DATASET.md](DATASET.md) for details on how the synthetic data was constructed.

---

## Pipeline Overview

```
Synthetic Dataset (CSV)
        │
        ▼
┌───────────────────────┐
│  Feature Engineering  │  ← url_analyzer.py extracts 19 features
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  Preprocessing        │  ← Imputation (median) + StandardScaler
│  Pipeline (sklearn)   │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────────────────────────────────────┐
│  Model Training — both models trained, best selected  │
│                                                       │
│  ┌──────────────────────┐  ┌────────────────────────┐ │
│  │  RandomForestClassi- │  │  LogisticRegression    │ │
│  │  fier (n=100 trees)  │  │  (C=1.0, lbfgs)        │ │
│  └──────────┬───────────┘  └──────────┬─────────────┘ │
│             └──────────┬──────────────┘               │
│                        ▼                              │
│           Evaluate on validation set (20%)            │
│           Select model with higher F1 score           │
└──────────────────────────┬────────────────────────────┘
                           │  winning model
                           ▼
┌───────────────────────────────────────────────────────┐
│  Calibration                                          │
│  CalibratedClassifierCV(method="isotonic", cv=5)      │
│  → probability scores are reliable (Brier score opt.) │
└──────────────────────────┬────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────┐
│  Persistence                                          │
│  • threat_classifier.joblib       (calibrated model)  │
│  • preprocessing_pipeline.joblib  (imputer + scaler)  │
│  • feature_schema.json            (feature metadata)  │
│  • training_metrics.json          (evaluation report) │
└───────────────────────────────────────────────────────┘
```

---

## Feature List and Descriptions

All 19 features are extracted from the decoded URL string.

| # | Feature Name | Type | Description |
|---|---|---|---|
| 1 | `url_length` | int | Total character count of the full URL |
| 2 | `hostname_length` | int | Character count of the hostname portion only |
| 3 | `num_subdomains` | int | Number of dot-separated labels in hostname minus 2 (root + TLD) |
| 4 | `has_https` | bool→float | 1.0 if scheme is `https`, 0.0 otherwise |
| 5 | `has_ip_host` | bool→float | 1.0 if hostname is a raw IPv4 or IPv6 address |
| 6 | `num_dots` | int | Total `.` characters in the full URL |
| 7 | `num_hyphens` | int | Total `-` characters in the full URL |
| 8 | `num_at` | int | Total `@` characters (credential injection indicator) |
| 9 | `num_question_marks` | int | Count of `?` characters |
| 10 | `num_ampersands` | int | Count of `&` characters (query parameter count proxy) |
| 11 | `num_percent_encoded` | int | Count of `%XX` percent-encoding sequences |
| 12 | `path_length` | int | Character count of the URL path component |
| 13 | `query_length` | int | Character count of the query string (after `?`) |
| 14 | `is_shortened_url` | bool→float | 1.0 if hostname matches known URL shortener list |
| 15 | `has_suspicious_tld` | bool→float | 1.0 if TLD is in suspicious list (`.tk`, `.ml`, `.ga`, `.cf`, `.gq`, `.xyz`, `.top`, `.click`, `.loan`, `.work`, ...) |
| 16 | `has_punycode` | bool→float | 1.0 if hostname contains `xn--` (internationalized domain — common in homograph attacks) |
| 17 | `has_double_slash` | bool→float | 1.0 if URL path contains `//` (bypass indicator) |
| 18 | `special_char_ratio` | float | Fraction of characters that are non-alphanumeric (excluding `.`, `/`, `:`) |
| 19 | `digit_ratio` | float | Fraction of characters in hostname that are digits |

Non-URL payloads (UPI, TEXT, EMAIL, etc.) receive a zeroed feature vector, and the Risk Engine applies payload-type-specific rules instead of relying on ML output.

---

## Training Procedure

The training script (`backend/ml/train.py`) is fully self-contained:

```bash
# Activate venv first
python backend/ml/train.py
```

Steps performed:

1. **Synthetic dataset generation** — creates 10,000 labelled samples (5,000 benign, 5,000 malicious) using parameterized URL generators
2. **Train/validation/test split** — 70% / 15% / 15% stratified split
3. **Preprocessing pipeline** — `SimpleImputer(median)` + `StandardScaler`, fitted on training set only
4. **Model training** — fits both `RandomForestClassifier(n_estimators=100, random_state=42)` and `LogisticRegression(max_iter=1000, random_state=42)`
5. **Model selection** — compares F1 score on validation set; best model wins
6. **Calibration** — wraps winning model in `CalibratedClassifierCV(method="isotonic", cv=5)`, refits on train+validation
7. **Evaluation** — final metrics computed on held-out test set
8. **Persistence** — saves artifacts to `backend/models/`

Expected runtime: **< 60 seconds** on a modern laptop.

---

## Model Selection Rationale

| Criterion | RandomForest | LogisticRegression |
|---|---|---|
| Interpretability | Medium (feature importances) | High (coefficients) |
| Performance on tabular URL features | Generally higher | Competitive baseline |
| Non-linearity | Handles naturally | Requires feature engineering |
| Calibration need | Moderate (RF probabilities are overconfident) | Low (already probabilistic) |
| Speed at inference | ~2 ms | ~0.1 ms |

RandomForest typically wins on the synthetic dataset due to non-linear interactions (e.g., `has_ip_host AND no_https` is especially malicious). Logistic Regression serves as a sanity-check baseline.

---

## Calibration Approach

Raw classifier probabilities — especially from RandomForest — are often overconfident (e.g., RF may output 0.95 when the true probability is 0.75). We apply **isotonic regression calibration** (`CalibratedClassifierCV(method="isotonic", cv=5)`):

- **Isotonic regression** is a non-parametric, monotone calibration method
- More flexible than Platt scaling (sigmoid) for high-capacity models like RF
- Evaluated using **Brier Score** (lower = better calibrated): target < 0.05 on synthetic data
- Reliability diagrams (calibration curves) are logged during training

Well-calibrated probabilities matter because the Risk Engine uses `threat_score` to make threshold decisions:
- score < 0.3 → LOW
- 0.3 ≤ score < 0.6 → MEDIUM
- score ≥ 0.6 → HIGH

Poor calibration would cause systematic misclassification at the thresholds.

---

## Evaluation Metrics Explained

| Metric | Formula | What it means in this context |
|---|---|---|
| **Accuracy** | (TP+TN)/(TP+TN+FP+FN) | Overall fraction correct — misleading on imbalanced sets |
| **Precision** | TP/(TP+FP) | Of URLs flagged as threats, how many actually are? (False alarm rate) |
| **Recall** | TP/(TP+FN) | Of actual threats, how many did we catch? (Miss rate) |
| **F1 Score** | 2·P·R/(P+R) | Harmonic mean — balances precision and recall |
| **ROC-AUC** | Area under ROC curve | Model's ability to rank threats above benign (1.0 = perfect) |
| **Brier Score** | mean((p̂ - y)²) | Calibration quality (0.0 = perfectly calibrated, 0.25 = random) |

For a security tool, **Recall** is typically more important than Precision — missing a real threat (false negative) is usually worse than a false alarm (false positive). Consider tuning the LOW/HIGH thresholds to favour recall in deployment.

---

## How to Retrain with Real Data

> [!IMPORTANT]
> Replacing synthetic training data with real threat intelligence data is essential before any production use.

### Step 1: Prepare your dataset

Create a CSV file with one row per URL:

```csv
url,label
https://www.google.com,0
http://phish-site.tk/steal?id=abc,1
...
```

Where `label` is `0` (benign) or `1` (malicious).

### Step 2: Edit `train.py`

Replace the synthetic data generation section with your CSV loader:

```python
# Replace this:
df = generate_synthetic_dataset(n_samples=10000)

# With this:
import pandas as pd
df = pd.read_csv("path/to/your/real_dataset.csv")
# df must have columns: 'url' (str) and 'label' (0 or 1)
```

### Step 3: Retrain

```bash
python backend/ml/train.py
```

The script will re-extract features from your real URLs, retrain both models, and save new artifacts.

### Step 4: Evaluate

```bash
python backend/ml/evaluate.py
```

Review the confusion matrix and ROC curve. For a production security tool, aim for:
- Recall ≥ 0.90 (catch 90%+ of real threats)
- Precision ≥ 0.80 (tolerable false alarm rate)
- Brier Score < 0.10

### Suggested Real Datasets

See [DATASET.md](DATASET.md) for a curated list of real URL threat datasets.
