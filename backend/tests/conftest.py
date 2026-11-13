"""
pytest configuration and shared fixtures for QR Sentinel tests.
"""
import io
import sys
from pathlib import Path
import pytest
import qrcode
from PIL import Image
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from main import create_app
from services.threat_classifier import classifier_service


@pytest.fixture(scope="session", autouse=True)
def load_ml_model():
    """Ensure ML model is loaded for test suite."""
    classifier_service.load_model()
    return classifier_service


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient fixture."""
    app = create_app()
    # ensure classifier is attached to state
    app.state.classifier = classifier_service
    with TestClient(app) as test_client:
        yield test_client


def _make_qr_png_bytes(data: str) -> bytes:
    """Generate a valid QR code in PNG format in-memory."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def valid_qr_url_png():
    """Fixture providing a benign HTTPS URL QR code."""
    return _make_qr_png_bytes("https://www.google.com/search?q=cybersecurity")


@pytest.fixture
def malicious_qr_url_png():
    """Fixture providing a suspicious URL QR code."""
    return _make_qr_png_bytes("http://192.168.1.100/login/update.php?redirect=http%3A%2F%2Fsteal-creds.tk%2Fauth&token=admin")


@pytest.fixture
def upi_qr_png():
    """Fixture providing a UPI payment QR code."""
    return _make_qr_png_bytes("upi://pay?pa=merchant@okaxis&pn=Merchant%20Name&am=500.00&cu=INR")


@pytest.fixture
def plain_text_qr_png():
    """Fixture providing a plain text QR code."""
    return _make_qr_png_bytes("Meeting room password is: CyberSentinel2026!")


@pytest.fixture
def non_qr_image_png():
    """Fixture providing a valid PNG image that contains NO QR code."""
    img = Image.new("RGB", (200, 200), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

