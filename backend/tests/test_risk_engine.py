"""
Unit tests for RiskEngine service.
"""
import pytest
from services.risk_engine import RiskEngine
from services.url_analyzer import URLAnalyzer
from schemas.common import RiskLevel
from schemas.qr import QRDecodeResult, QRPayloadType


def test_risk_low_for_benign_url():
    analyzer = URLAnalyzer()
    engine = RiskEngine()
    features = analyzer.extract_features("https://www.google.com/search")
    level, score, indicators, explanation = engine.assess(features, ml_score=0.05)
    assert level == RiskLevel.LOW
    assert score < 0.3
    assert "LOW" in explanation


def test_risk_high_for_malicious_url():
    analyzer = URLAnalyzer()
    engine = RiskEngine()
    features = analyzer.extract_features("http://user@45.33.32.156/admin/login")
    level, score, indicators, explanation = engine.assess(features, ml_score=0.92)
    assert level == RiskLevel.HIGH
    assert score >= 0.6
    assert any(i.name == "IP_HOST" and i.triggered for i in indicators)
    assert any(i.name == "AT_SYMBOL" and i.triggered for i in indicators)


def test_risk_inconclusive_for_non_decoded_qr():
    engine = RiskEngine()
    decode_result = QRDecodeResult(
        decoded=False,
        payload=None,
        payload_type=QRPayloadType.UNKNOWN,
        confidence=0.0,
        decoder_used="none",
    )
    level, score, indicators, explanation = engine.assess(None, None, decode_result)
    assert level == RiskLevel.INCONCLUSIVE
    assert "decoded" in explanation.lower()


def test_risk_inconclusive_for_plain_text_qr():
    engine = RiskEngine()
    decode_result = QRDecodeResult(
        decoded=True,
        payload="Hello World",
        payload_type=QRPayloadType.TEXT,
        confidence=1.0,
        decoder_used="pyzbar",
    )
    level, score, indicators, explanation = engine.assess(None, None, decode_result)
    assert level == RiskLevel.INCONCLUSIVE
    assert "url" in explanation.lower()

