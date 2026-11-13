"""
QR analysis endpoints:
  POST /api/v1/qr/analyze   — decode + full threat analysis
  POST /api/v1/qr/decode    — decode only (no threat analysis)
  POST /api/v1/qr/distort   — robustness / distortion testing
  POST /api/v1/qr/compare   — compare two QR images
"""
import uuid
from typing import Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, File, Form, Request, UploadFile

from core.config import settings
from core.exceptions import FileTooLargeError, InvalidFileTypeError, QRDecodeError
from schemas.qr import (
    QRAnalyzeResponse,
    QRDecodeOnlyResponse,
    QRDecodeResult,
    QRDistortResponse,
    QRPayloadType,
)
from schemas.common import RiskLevel
from services.qr_decoder import QRDecoder
from services.image_preprocessor import ImagePreprocessor
from services.url_analyzer import URLAnalyzer
from services.feature_extractor import FeatureExtractor
from services.risk_engine import RiskEngine
from services.image_robustness import ImageRobustnessTester
from core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

MAGIC_BYTES = {
    b"\x89PNG": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"RIFF": "image/webp",  # partial; full check needs bytes 8–11 == WEBP
}

MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


def _validate_upload(data: bytes, content_type: str) -> str:
    """Validate file size and magic bytes. Returns detected MIME type."""
    if len(data) > MAX_BYTES:
        raise FileTooLargeError(f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.")

    # Magic byte detection
    detected = None
    if data[:4] == b"\x89PNG":
        detected = "image/png"
    elif data[:3] == b"\xff\xd8\xff":
        detected = "image/jpeg"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        detected = "image/webp"

    if detected is None:
        raise InvalidFileTypeError("File magic bytes do not match any supported image format.")
    return detected


def _decode_qr(image_data: bytes) -> QRDecodeResult:
    preprocessor = ImagePreprocessor()
    decoder = QRDecoder()
    images = preprocessor.prepare_variants(image_data)
    for img in images:
        result = decoder.decode(img)
        if result.decoded:
            return result
    return QRDecodeResult(decoded=False, payload=None, payload_type=QRPayloadType.UNKNOWN,
                          confidence=0.0, decoder_used="none")


@router.post("/analyze", response_model=QRAnalyzeResponse, summary="Full QR threat analysis")
async def analyze_qr(request: Request, file: UploadFile = File(...)):
    """Upload a QR code image for full decode + threat analysis."""
    request_id = str(uuid.uuid4())
    image_data = await file.read()
    _validate_upload(image_data, file.content_type or "")

    decode_result = _decode_qr(image_data)

    # Default inconclusive if decode failed
    if not decode_result.decoded or not decode_result.payload:
        from schemas.qr import ThreatAnalysisResult
        threat = ThreatAnalysisResult(
            risk_level=RiskLevel.INCONCLUSIVE,
            risk_score=0.0,
            explanation="QR code could not be decoded.",
            indicators=[],
        )
        return QRAnalyzeResponse(
            request_id=request_id,
            decode=decode_result,
            threat=threat,
            metadata={"filename": file.filename},
        )

    # Threat analysis
    classifier = getattr(request.app.state, "classifier", None)
    ml_score = None
    features = None

    if decode_result.payload_type in (QRPayloadType.URL_HTTP, QRPayloadType.URL_HTTPS):
        analyzer = URLAnalyzer()
        features = analyzer.extract_features(decode_result.payload)
        extractor = FeatureExtractor()
        feature_vector = extractor.to_vector(features)
        if classifier and classifier.is_loaded:
            ml_score = classifier.predict_proba(feature_vector)

    engine = RiskEngine()
    risk_level, risk_score, indicators, explanation = engine.assess(
        features=features,
        ml_score=ml_score,
        decode_result=decode_result,
        raw_payload=decode_result.payload,
    )

    from schemas.qr import ThreatAnalysisResult
    threat = ThreatAnalysisResult(
        risk_level=risk_level,
        risk_score=risk_score,
        ml_score=ml_score,
        indicators=indicators,
        explanation=explanation,
    )

    return QRAnalyzeResponse(
        request_id=request_id,
        decode=decode_result,
        threat=threat,
        metadata={"filename": file.filename, "size_bytes": len(image_data)},
    )


@router.post("/decode", response_model=QRDecodeOnlyResponse, summary="Decode QR code only")
async def decode_qr(file: UploadFile = File(...)):
    """Decode a QR code image without threat analysis."""
    image_data = await file.read()
    _validate_upload(image_data, file.content_type or "")
    decode_result = _decode_qr(image_data)
    return QRDecodeOnlyResponse(decode=decode_result)


@router.post("/distort", response_model=QRDistortResponse, summary="Test QR robustness under distortions")
async def distort_qr(
    file: UploadFile = File(...),
    severity: float = Form(0.5),
):
    """Apply various distortions to a QR image and test decodability."""
    image_data = await file.read()
    _validate_upload(image_data, file.content_type or "")

    # Get original payload
    original_decode = _decode_qr(image_data)
    tester = ImageRobustnessTester()
    results = tester.test_all(image_data, severity)
    decodable_count = sum(1 for r in results if r.still_decodable)
    robustness_score = decodable_count / len(results) if results else 0.0

    return QRDistortResponse(
        original_payload=original_decode.payload,
        distortion_results=results,
        robustness_score=robustness_score,
    )


@router.post("/compare", summary="Compare two QR code images")
async def compare_qr(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    """Compare two QR images: check if they encode the same payload."""
    data1 = await file1.read()
    data2 = await file2.read()
    _validate_upload(data1, file1.content_type or "")
    _validate_upload(data2, file2.content_type or "")

    decode1 = _decode_qr(data1)
    decode2 = _decode_qr(data2)

    same_payload = (
        decode1.decoded and decode2.decoded and decode1.payload == decode2.payload
    )
    return {
        "success": True,
        "same_payload": same_payload,
        "qr1": decode1.model_dump(),
        "qr2": decode2.model_dump(),
    }


class QRGenerateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2048, description="Payload to encode into QR")


def _render_qr_base64(text: str) -> str:
    """Generate a clean PNG QR code and return as data URI."""
    import io
    import base64
    import qrcode

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#070b14", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


@router.post("/generate", summary="Generate a real QR code image from text or URL")
async def generate_qr(body: QRGenerateRequest):
    """Generate a high-contrast PNG QR code as base64 data URI."""
    data_url = _render_qr_base64(body.text)
    return {
        "success": True,
        "payload": body.text,
        "data_url": data_url,
    }


PRESET_SAMPLES = [
    {
        "id": "safe_google",
        "title": "Safe Google Search",
        "category": "LOW RISK",
        "badge_color": "emerald",
        "description": "Legitimate HTTPS URL with established global domain reputation.",
        "payload": "https://www.google.com/search?q=cybersecurity+defense",
    },
    {
        "id": "safe_wiki",
        "title": "Safe Wikipedia Reference",
        "category": "LOW RISK",
        "badge_color": "emerald",
        "description": "Clean HTTPS encyclopedia article with standard URL topology.",
        "payload": "https://en.wikipedia.org/wiki/Computer_security",
    },
    {
        "id": "phish_ip",
        "title": "Raw IP Phishing Portal",
        "category": "HIGH RISK",
        "badge_color": "rose",
        "description": "Bypasses DNS reputation with raw IP host and unencrypted HTTP.",
        "payload": "http://192.168.1.1/admin/login.php?auth_token=steal",
    },
    {
        "id": "quish_tld",
        "title": "Deceptive Free TLD (.tk)",
        "category": "HIGH RISK",
        "badge_color": "rose",
        "description": "Impersonates Apple ID on high-risk free top-level domain without encryption.",
        "payload": "http://login-appleid.verify-alert.tk/update-account",
    },
    {
        "id": "credential_at",
        "title": "Authority Obfuscation (@)",
        "category": "HIGH RISK",
        "badge_color": "rose",
        "description": "Uses '@' delimiter in authority section to deceive users regarding true destination.",
        "payload": "http://paypal-security-check.com@malicious-harvesting.site/verify",
    },
    {
        "id": "legit_upi",
        "title": "Verified Merchant UPI",
        "category": "LOW RISK",
        "badge_color": "emerald",
        "description": "Authentic UPI merchant payment string with official SBI banking PSP handle.",
        "payload": "upi://pay?pa=supermarket@oksbi&pn=FreshMart&am=450&cu=INR",
    },
    {
        "id": "scam_upi",
        "title": "Deceptive UPI Refund Scam",
        "category": "HIGH RISK",
        "badge_color": "rose",
        "description": "Imposter payment requesting money under the guise of an electricity bill refund.",
        "payload": "upi://pay?pa=customercare882@fakebank&pn=ElectricityBillRefund&am=5000",
    },
    {
        "id": "open_wifi",
        "title": "Unencrypted Public WiFi",
        "category": "MEDIUM RISK",
        "badge_color": "amber",
        "description": "Open public hotspot configuration lacking WPA2/WPA3 transport encryption.",
        "payload": "WIFI:S:Airport_Free_WiFi;T:nopass;;",
    },
]


@router.get("/samples", summary="List pre-generated sample QR codes for threat testing")
async def get_sample_qrs():
    """Returns curated test cases with live generated QR code data URLs."""
    samples = []
    for s in PRESET_SAMPLES:
        data_url = _render_qr_base64(s["payload"])
        samples.append({
            **s,
            "data_url": data_url,
        })
    return {
        "success": True,
        "count": len(samples),
        "samples": samples,
    }
