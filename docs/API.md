# 📡 QR Sentinel — API Reference

> **Base URL**: `http://localhost:8000`
> **API Version**: `v1`
> **Authentication**: None (v1 — see [Security Notes](#authentication))
> **Content-Type**: `multipart/form-data` for image uploads; `application/json` for URL-only endpoints

---

## Table of Contents

1. [QR Endpoints](#qr-endpoints)
   - [POST /api/v1/qr/analyze](#post-apiv1qranalyze)
   - [POST /api/v1/qr/decode](#post-apiv1qrdecode)
   - [POST /api/v1/qr/distort](#post-apiv1qrdistort)
   - [POST /api/v1/qr/compare](#post-apiv1qrcompare)
2. [URL Endpoints](#url-endpoints)
   - [POST /api/v1/url/analyze](#post-apiv1urlanalyze)
3. [Model Endpoints](#model-endpoints)
   - [GET /api/v1/model/status](#get-apiv1modelstatus)
   - [GET /api/v1/model/metrics](#get-apiv1modelmetrics)
4. [System Endpoints](#system-endpoints)
   - [GET /api/v1/system/health](#get-apiv1systemhealth)
5. [Error Codes](#error-codes)
6. [Rate Limiting](#rate-limiting)
7. [Authentication](#authentication)

---

## QR Endpoints

### POST /api/v1/qr/analyze

Full QR code analysis: decodes the QR, extracts features, runs ML classification, and returns a risk assessment.

**Request**

```
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File (image) | ✅ | QR code image. PNG, JPEG, JPG, or WEBP. Max 10 MB. |

**Response** `200 OK`

```json
{
  "success": true,
  "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "payload": "https://malicious-example.tk/phish?id=abc123",
  "payload_type": "URL_HTTPS",
  "risk_level": "HIGH",
  "threat_score": 0.87,
  "raw_ml_score": 0.82,
  "risk_indicators": [
    "Suspicious TLD (.tk)",
    "Path contains phishing keyword",
    "Query string is unusually long"
  ],
  "recommendation": "Do not visit this URL. It exhibits multiple indicators of a phishing attack.",
  "explanation": "The URL scored HIGH risk. Top contributing factors: suspicious TLD (weight: 0.31), long query string (weight: 0.22), no HTTPS despite HTTPS payload type mismatch (weight: 0.14).",
  "top_features": [
    {"feature": "has_suspicious_tld", "value": 1.0, "importance": 0.31},
    {"feature": "query_length",       "value": 48,  "importance": 0.22},
    {"feature": "url_length",         "value": 72,  "importance": 0.14}
  ],
  "model_version": "1.0.0-synthetic",
  "decode_method": "pyzbar",
  "processing_time_ms": 143
}
```

**curl example**

```bash
curl -X POST http://localhost:8000/api/v1/qr/analyze \
  -F "file=@/path/to/qrcode.png"
```

---

### POST /api/v1/qr/decode

Decodes a QR code image and returns the raw payload **without** ML classification.

**Request**

```
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File (image) | ✅ | QR code image. PNG, JPEG, JPG, or WEBP. Max 10 MB. |

**Response** `200 OK`

```json
{
  "success": true,
  "payload": "https://example.com",
  "payload_type": "URL_HTTPS",
  "decode_method": "pyzbar",
  "bounding_box": [10, 10, 290, 290],
  "processing_time_ms": 28
}
```

**Response** `200 OK` (decode failure)

```json
{
  "success": false,
  "payload": null,
  "payload_type": "UNKNOWN",
  "decode_method": "failed",
  "error": "No QR code detected in image",
  "processing_time_ms": 95
}
```

**curl example**

```bash
curl -X POST http://localhost:8000/api/v1/qr/decode \
  -F "file=@/path/to/qrcode.png"
```

---

### POST /api/v1/qr/distort

Tests QR code readability under a battery of image distortions (blur, noise, compression, rotation, crop).

**Request**

```
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File (image) | ✅ | QR code image. PNG, JPEG, JPG, or WEBP. Max 10 MB. |

**Response** `200 OK`

```json
{
  "original_decoded": true,
  "robustness_score": 0.72,
  "distortion_results": [
    {"distortion": "gaussian_blur_mild",    "decoded": true,  "payload_match": true},
    {"distortion": "gaussian_blur_heavy",   "decoded": false, "payload_match": false},
    {"distortion": "salt_pepper_noise",     "decoded": true,  "payload_match": true},
    {"distortion": "jpeg_compression_q30",  "decoded": true,  "payload_match": true},
    {"distortion": "rotation_15deg",        "decoded": true,  "payload_match": true},
    {"distortion": "rotation_45deg",        "decoded": false, "payload_match": false},
    {"distortion": "center_crop_80pct",     "decoded": true,  "payload_match": true}
  ],
  "summary": "QR code survives 5/7 distortions. Moderate robustness."
}
```

**curl example**

```bash
curl -X POST http://localhost:8000/api/v1/qr/distort \
  -F "file=@/path/to/qrcode.png"
```

---

### POST /api/v1/qr/compare

Compares two QR code images: checks if they decode to the same payload and whether one is a modified/tampered version of the other.

**Request**

```
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_a` | File (image) | ✅ | First QR code image |
| `file_b` | File (image) | ✅ | Second QR code image |

**Response** `200 OK`

```json
{
  "file_a_payload": "https://pay.example.com/invoice/42",
  "file_b_payload": "https://pay.attacker.com/invoice/42",
  "payloads_match": false,
  "payload_similarity": 0.76,
  "risk_note": "Payloads differ — possible substitution attack. Domains differ.",
  "file_a_risk_level": "LOW",
  "file_b_risk_level": "HIGH"
}
```

**curl example**

```bash
curl -X POST http://localhost:8000/api/v1/qr/compare \
  -F "file_a=@original.png" \
  -F "file_b=@suspect.png"
```

---

## URL Endpoints

### POST /api/v1/url/analyze

Analyzes a raw URL string without requiring an image. Useful for testing or integrating URL analysis into other workflows.

**Request**

```
Content-Type: application/json
```

```json
{
  "url": "http://192.168.1.1/phishing?redirect=http%3A%2F%2Fevil.tk%2Fsteal"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | ✅ | URL to analyze (max 2048 characters) |

**Response** `200 OK`

```json
{
  "url": "http://192.168.1.1/phishing?redirect=http%3A%2F%2Fevil.tk%2Fsteal",
  "risk_level": "HIGH",
  "threat_score": 0.91,
  "risk_indicators": [
    "IP address as host (bypasses DNS-based filtering)",
    "URL contains percent-encoded redirect",
    "No HTTPS"
  ],
  "features": {
    "url_length": 67,
    "has_https": 0,
    "has_ip_host": 1,
    "num_percent_encoded": 3
  },
  "recommendation": "This URL exhibits strong phishing indicators. Do not visit.",
  "model_version": "1.0.0-synthetic"
}
```

**curl example**

```bash
curl -X POST http://localhost:8000/api/v1/url/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "http://192.168.1.1/phishing?redirect=http%3A%2F%2Fevil.tk%2Fsteal"}'
```

---

## Model Endpoints

### GET /api/v1/model/status

Returns current model load status, version, and training metadata.

**Response** `200 OK`

```json
{
  "status": "loaded",
  "model_type": "RandomForest",
  "model_version": "1.0.0-synthetic",
  "training_dataset": "SYNTHETIC_DEMO",
  "num_features": 19,
  "trained_at": "2026-11-12T07:00:00Z",
  "warning": "Model trained on SYNTHETIC data only. Do not use for production security decisions."
}
```

**curl example**

```bash
curl http://localhost:8000/api/v1/model/status
```

---

### GET /api/v1/model/metrics

Returns model performance metrics from the training evaluation.

**Response** `200 OK`

```json
{
  "model_type": "RandomForest",
  "dataset": "SYNTHETIC_DEMO",
  "train_samples": 8000,
  "test_samples": 2000,
  "metrics": {
    "accuracy": 0.954,
    "precision": 0.961,
    "recall": 0.948,
    "f1_score": 0.954,
    "roc_auc": 0.991,
    "brier_score": 0.038
  },
  "confusion_matrix": {
    "true_positive": 947,
    "true_negative": 960,
    "false_positive": 40,
    "false_negative": 53
  },
  "warning": "Metrics computed on SYNTHETIC test data. Real-world performance will differ."
}
```

**curl example**

```bash
curl http://localhost:8000/api/v1/model/metrics
```

---

## System Endpoints

### GET /api/v1/system/health

Liveness check. Returns HTTP 200 when the service is running and the model is loaded.

**Response** `200 OK`

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "uptime_seconds": 3621
}
```

**Response** `503 Service Unavailable` (model not loaded)

```json
{
  "status": "degraded",
  "model_loaded": false,
  "detail": "ML model not found. Run: python backend/ml/train.py"
}
```

**curl example**

```bash
curl http://localhost:8000/api/v1/system/health
```

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| `400` | `INVALID_FILE_TYPE` | File MIME type not in allowed list (PNG, JPEG, WEBP) |
| `400` | `FILE_TOO_LARGE` | File exceeds 10 MB limit |
| `400` | `INVALID_IMAGE` | File passes MIME check but cannot be decoded as an image |
| `400` | `INVALID_URL` | URL field is malformed or exceeds max length |
| `422` | `VALIDATION_ERROR` | Request body / form failed Pydantic validation |
| `500` | `MODEL_NOT_LOADED` | Model artifacts missing — run training script |
| `500` | `DECODE_INTERNAL_ERROR` | Unexpected error during QR decoding |
| `503` | `SERVICE_UNAVAILABLE` | Service is starting up or model failed to load |
| `429` | `RATE_LIMIT_EXCEEDED` | Too many requests (see Rate Limiting) |

**Error response body**

```json
{
  "error": "INVALID_FILE_TYPE",
  "detail": "File type 'image/gif' is not supported. Allowed: image/png, image/jpeg, image/webp",
  "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

---

## Rate Limiting

> [!NOTE]
> v1 uses **in-memory** rate limiting (via `slowapi`). Limits reset if the server restarts and are **not** distributed (not suitable for multi-process deployments).

| Endpoint group | Limit |
|----------------|-------|
| `/api/v1/qr/*` | 30 requests / minute per IP |
| `/api/v1/url/analyze` | 60 requests / minute per IP |
| `/api/v1/model/*` | 10 requests / minute per IP |
| `/api/v1/system/health` | Unlimited |

When rate limit is exceeded, the API returns `HTTP 429` with a `Retry-After` header.

---

## Authentication

> [!IMPORTANT]
> **v1 has no authentication.** All endpoints are publicly accessible to anyone who can reach the server.
>
> **Do not expose the backend port to the internet** without adding authentication. Options for future versions:
> - API key via `Authorization: Bearer <key>` header (simplest)
> - OAuth2 / JWT for multi-user deployments
> - mTLS for internal service-to-service calls

---

## Interactive API Docs

FastAPI automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
