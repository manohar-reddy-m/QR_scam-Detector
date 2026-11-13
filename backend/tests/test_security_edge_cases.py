"""
Security edge cases and defensive hardening tests.
"""
import pytest
from core.exceptions import FileTooLargeError, InvalidFileTypeError


def test_reject_fake_image_magic_bytes(client):
    """A file ending in .png but containing plain ASCII text must be rejected."""
    fake_png_data = b"This is just malicious plain text pretending to be an image"
    response = client.post(
        "/api/v1/qr/analyze",
        files={"file": ("fake.png", fake_png_data, "image/png")},
    )
    # Backend returns error response (415 Unsupported Media Type or handled error)
    assert response.status_code in (400, 415, 422, 500)
    data = response.json()
    assert "error" in data or "detail" in data


def test_reject_empty_image_upload(client):
    """An empty 0-byte file upload must be rejected safely."""
    response = client.post(
        "/api/v1/qr/analyze",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code in (400, 415, 422, 500)


def test_path_traversal_filename_sanitization(client, valid_qr_url_png):
    """Uploaded filename with directory traversal must be handled without path escape."""
    response = client.post(
        "/api/v1/qr/analyze",
        files={"file": ("../../../../etc/passwd.png", valid_qr_url_png, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_url_with_null_bytes(client):
    """URL containing null bytes or control characters must not cause server crash."""
    response = client.post(
        "/api/v1/url/analyze",
        json={"url": "https://example.com/test\x00malicious"},
    )
    # Should either validate, handle cleanly, or reject with 422
    assert response.status_code in (200, 422)


def test_non_qr_image_returns_inconclusive(client, non_qr_image_png):
    """Image with no QR code must safely return INCONCLUSIVE without error."""
    response = client.post(
        "/api/v1/qr/analyze",
        files={"file": ("blank.png", non_qr_image_png, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decode"]["decoded"] is False
    assert data["threat"]["risk_level"] == "INCONCLUSIVE"
