# 🏗️ QR Sentinel — System Architecture

## Overview

QR Sentinel is a two-tier web application:

- **Frontend** — React SPA (Vite + TypeScript + TailwindCSS) served independently
- **Backend** — Python FastAPI service providing the ML and analysis pipeline

The design follows a **single-service backend** pattern for v1 simplicity, with clear internal service boundaries that allow future decomposition into microservices.

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| API framework | FastAPI | Async support, automatic OpenAPI docs, Pydantic validation |
| ML library | scikit-learn | Mature, well-understood, easy serialization with joblib |
| QR decoding | pyzbar + OpenCV | pyzbar is fast; OpenCV provides fallback for edge cases |
| Frontend | React + Vite | Fast HMR, TypeScript support, modern ecosystem |
| Styling | TailwindCSS + shadcn/ui | Utility-first with accessible components |
| Serialization | joblib | Efficient numpy array serialization for sklearn models |
| Configuration | Pydantic Settings | Type-safe env-var configuration with `.env` support |

---

## Service Decomposition

```
backend/
├── main.py                        ← FastAPI app, middleware, startup
│
├── api/v1/
│   ├── router.py                  ← Route aggregator
│   └── endpoints/
│       ├── qr.py                  ← QR image analysis routes
│       ├── url.py                 ← Raw URL analysis routes
│       ├── model.py               ← Model introspection routes
│       └── system.py             ← Health check
│
├── services/                      ← Business logic (stateless)
│   ├── qr_decoder.py             ← Image → decoded payload
│   ├── image_preprocessor.py     ← Image normalization pipeline
│   ├── url_analyzer.py           ← URL → feature vector
│   ├── feature_extractor.py      ← Composite feature extraction
│   ├── threat_classifier.py      ← Feature vector → ML score
│   ├── risk_engine.py            ← ML score + rules → risk level
│   ├── explainability.py         ← Risk explanation generation
│   └── image_robustness.py       ← Distortion testing
│
├── ml/
│   ├── train.py                   ← Offline training script
│   ├── evaluate.py                ← Offline evaluation script
│   └── feature_schema.py         ← Feature definitions (single source of truth)
│
├── schemas/                       ← Pydantic I/O models
│   ├── qr.py
│   ├── url.py
│   └── common.py
│
├── core/
│   ├── config.py                  ← Pydantic Settings
│   ├── logging_config.py          ← Structured JSON logging
│   └── exceptions.py             ← Custom exception hierarchy
│
└── models/                        ← Generated artifacts (not in git)
    ├── threat_classifier.joblib
    ├── preprocessing_pipeline.joblib
    ├── feature_schema.json
    └── training_metrics.json
```

---

## Data Flow

### Full QR Analysis (`POST /api/v1/qr/analyze`)

```
Client (browser)
      │
      │  multipart/form-data (image file)
      ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI endpoint: qr.py::analyze_qr()                          │
│                                                                  │
│  1. Validate file (magic bytes, size ≤ 10MB, allowed MIME)      │
│  2. Write to NamedTemporaryFile (auto-cleaned)                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  ImagePreprocessor.preprocess()                                  │
│  • Grayscale conversion                                          │
│  • Contrast enhancement (CLAHE)                                  │
│  • Adaptive thresholding                                         │
│  • Resize normalization                                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  QRDecoder.decode()                                              │
│  • Primary: pyzbar.decode()                                      │
│  • Fallback: cv2.QRCodeDetector().detectAndDecode()             │
│  • Returns: payload string, payload type, bounding box          │
└──────────────────────┬──────────────────────────────────────────┘
                       │  payload (URL, UPI, text, etc.)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  FeatureExtractor.extract(payload)                               │
│  • URLAnalyzer extracts 19 URL features                          │
│  • Returns: Dict[str, float | int | bool]                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │  feature vector (19-dimensional)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  ThreatClassifier.predict(features)                              │
│  • Loads preprocessing_pipeline.joblib (impute + scale)         │
│  • Loads threat_classifier.joblib (CalibratedClassifierCV)      │
│  • Returns: threat_score ∈ [0.0, 1.0], model_version           │
└──────────────────────┬──────────────────────────────────────────┘
                       │  threat_score
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  RiskEngine.assess(threat_score, features, payload_type)         │
│  • Apply rule-based adjustments (UPI bonus, HTTPS discount)      │
│  • Thresholds: LOW < 0.3 ≤ MEDIUM < 0.6 ≤ HIGH                 │
│  • INCONCLUSIVE if decode failed or scope out-of-range           │
│  • Returns: risk_level, adjusted_score, risk_indicators[]        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  Explainability.explain(features, risk_level)                    │
│  • Feature importance from RF model                              │
│  • Human-readable explanation per top contributing feature       │
│  • Returns: explanation_text, top_features[]                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
              JSON Response to client
              {risk_level, threat_score, payload,
               payload_type, explanation, indicators,
               top_features, model_version}
```

---

## Interface Contracts

### QRDecoder → FeatureExtractor

```python
@dataclass
class DecodeResult:
    success: bool
    payload: str | None          # Raw decoded string
    payload_type: PayloadType    # Enum: URL_HTTPS, UPI_PAYMENT, etc.
    bounding_box: list[int] | None
    decode_method: str           # "pyzbar" | "opencv" | "failed"
    error: str | None
```

### FeatureExtractor → ThreatClassifier

```python
# 19-feature ordered dict (matches feature_schema.json)
features: dict[str, float] = {
    "url_length": ...,
    "hostname_length": ...,
    "num_subdomains": ...,
    "has_https": ...,           # 0.0 or 1.0
    "has_ip_host": ...,         # 0.0 or 1.0
    "num_dots": ...,
    "num_hyphens": ...,
    "num_at": ...,
    "num_question_marks": ...,
    "num_ampersands": ...,
    "num_percent_encoded": ...,
    "path_length": ...,
    "query_length": ...,
    "is_shortened_url": ...,    # 0.0 or 1.0
    "has_suspicious_tld": ...,  # 0.0 or 1.0
    "has_punycode": ...,        # 0.0 or 1.0
    "has_double_slash": ...,    # 0.0 or 1.0
    "special_char_ratio": ...,
    "digit_ratio": ...,
}
```

### ThreatClassifier → RiskEngine

```python
@dataclass
class ClassificationResult:
    threat_score: float          # 0.0 (safe) → 1.0 (malicious)
    model_version: str
    model_type: str              # "RandomForest" | "LogisticRegression"
    feature_importances: dict[str, float] | None
```

### RiskEngine → Response

```python
@dataclass
class RiskAssessment:
    risk_level: RiskLevel        # Enum: LOW, MEDIUM, HIGH, INCONCLUSIVE
    threat_score: float          # Adjusted score
    raw_ml_score: float
    risk_indicators: list[str]   # Human-readable flags
    recommendation: str
```

---

## Extension Points

| Extension | How to Add |
|---|---|
| **New payload type** | Add to `PayloadType` enum in `schemas/qr.py`; add detection logic in `qr_decoder.py` |
| **New ML feature** | Add to `feature_schema.py`; implement extraction in `url_analyzer.py`; retrain |
| **New risk rule** | Add rule function in `risk_engine.py::_apply_rules()` |
| **New decoder** | Implement `decode(image_path) → DecodeResult` and register in `qr_decoder.py` |
| **External threat feed** | Add a `ThreatFeedService` and query it in `risk_engine.py` before scoring |
| **Persistent audit log** | Add SQLAlchemy model + write in endpoint after assessment |
| **Authentication** | Add FastAPI `Depends(verify_api_key)` to any route; configure key in `.env` |
| **New endpoint version** | Add `api/v2/` package; register in `main.py` with prefix `/api/v2` |
