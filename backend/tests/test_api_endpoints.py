"""
API Integration tests using FastAPI TestClient.
"""
import io
import pytest
from schemas.common import RiskLevel
from schemas.qr import QRPayloadType


def test_system_health(client):
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "QR Sentinel"
    assert "version" in data


def test_model_status_and_metrics(client):
    status_resp = client.get("/api/v1/model/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["loaded"] is True
    assert status_data["model_type"] in ("RandomForest", "LogisticRegression")
    assert status_data["num_features"] == 19

    metrics_resp = client.get("/api/v1/model/metrics")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    assert metrics_data["available"] is True
    assert "metrics" in metrics_data


def test_url_analyze_endpoint_benign(client):
    response = client.post(
        "/api/v1/url/analyze",
        json={"url": "https://www.wikipedia.org/wiki/Computer_security"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["risk_level"] in ("LOW", "MEDIUM")
    assert "features" in data
    assert data["features"]["has_https"] is True


def test_url_analyze_endpoint_malicious(client):
    response = client.post(
        "/api/v1/url/analyze",
        json={"url": "http://192.168.1.50/verify-account.tk/index.html"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["risk_level"] in ("MEDIUM", "HIGH")
    assert data["features"]["has_ip_host"] is True


def test_qr_analyze_endpoint(client, valid_qr_url_png):
    response = client.post(
        "/api/v1/qr/analyze",
        files={"file": ("test_qr.png", valid_qr_url_png, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["decode"]["decoded"] is True
    assert "google.com" in data["decode"]["payload"]
    assert data["decode"]["payload_type"] == "URL_HTTPS"
    assert data["threat"]["risk_level"] in ("LOW", "MEDIUM")


def test_qr_decode_only_endpoint(client, valid_qr_url_png):
    response = client.post(
        "/api/v1/qr/decode",
        files={"file": ("test_qr.png", valid_qr_url_png, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["decode"]["decoded"] is True
    assert data["decode"]["payload"] is not None


def test_qr_distort_endpoint(client, valid_qr_url_png):
    response = client.post(
        "/api/v1/qr/distort",
        files={"file": ("test_qr.png", valid_qr_url_png, "image/png")},
        data={"severity": "0.4"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["distortion_results"]) > 0
    assert 0.0 <= data["robustness_score"] <= 1.0


def test_qr_compare_endpoint_same(client, valid_qr_url_png):
    response = client.post(
        "/api/v1/qr/compare",
        files={
            "file1": ("qr1.png", valid_qr_url_png, "image/png"),
            "file2": ("qr2.png", valid_qr_url_png, "image/png"),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["same_payload"] is True


def test_qr_generate_endpoint(client):
    resp = client.post("/api/v1/qr/generate", json={"text": "https://cybersecurity.example.org"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["payload"] == "https://cybersecurity.example.org"
    assert data["data_url"].startswith("data:image/png;base64,")


def test_qr_samples_endpoint(client):
    resp = client.get("/api/v1/qr/samples")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["count"] >= 5
    assert len(data["samples"]) == data["count"]
    assert "data_url" in data["samples"][0]
    assert data["samples"][0]["data_url"].startswith("data:image/png;base64,")

