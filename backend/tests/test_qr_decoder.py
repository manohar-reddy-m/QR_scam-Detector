"""
Unit tests for QR detection and decoding service.
"""
import io
import pytest
import numpy as np
import cv2
from PIL import Image

from services.qr_decoder import QRDecoder, _classify_payload
from services.image_preprocessor import ImagePreprocessor
from schemas.qr import QRPayloadType


def test_classify_payload_types():
    assert _classify_payload("https://github.com") == QRPayloadType.URL_HTTPS
    assert _classify_payload("http://insecure-site.org") == QRPayloadType.URL_HTTP
    assert _classify_payload("upi://pay?pa=test@upi&pn=Test") == QRPayloadType.UPI_PAYMENT
    assert _classify_payload("mailto:security@company.com") == QRPayloadType.EMAIL
    assert _classify_payload("tel:+1234567890") == QRPayloadType.PHONE
    assert _classify_payload("WIFI:S:MyNetwork;T:WPA;P:Secret123;;") == QRPayloadType.WIFI
    assert _classify_payload("BEGIN:VCARD\nVERSION:3.0\nFN:John Doe\nEND:VCARD") == QRPayloadType.VCARD
    assert _classify_payload("Just a plain text message") == QRPayloadType.TEXT


def test_decode_valid_qr(valid_qr_url_png):
    preprocessor = ImagePreprocessor()
    decoder = QRDecoder()
    images = preprocessor.prepare_variants(valid_qr_url_png)
    assert len(images) > 0
    
    decoded = False
    for img in images:
        result = decoder.decode(img)
        if result.decoded:
            decoded = True
            assert "google.com" in result.payload
            assert result.payload_type == QRPayloadType.URL_HTTPS
            assert result.confidence > 0.0
            break
    assert decoded, "Valid QR code should be successfully decoded"


def test_decode_non_qr_image(non_qr_image_png):
    preprocessor = ImagePreprocessor()
    decoder = QRDecoder()
    images = preprocessor.prepare_variants(non_qr_image_png)
    
    for img in images:
        result = decoder.decode(img)
        assert not result.decoded
        assert result.payload is None
        assert result.payload_type == QRPayloadType.UNKNOWN


def test_decode_upi_qr(upi_qr_png):
    preprocessor = ImagePreprocessor()
    decoder = QRDecoder()
    images = preprocessor.prepare_variants(upi_qr_png)
    
    decoded = False
    for img in images:
        result = decoder.decode(img)
        if result.decoded:
            decoded = True
            assert result.payload_type == QRPayloadType.UPI_PAYMENT
            assert "merchant@okaxis" in result.payload
            break
    assert decoded, "UPI QR code should be decoded and typed correctly"

