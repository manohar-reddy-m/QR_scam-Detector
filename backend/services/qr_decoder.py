"""
QR code decoder service.
Multi-engine pipeline for maximum real-world decode coverage:
  Engine 1: pyzbar (ZBar C lib — fast, accurate for clean/standard QRs)
  Engine 2: OpenCV QRCodeDetectorAruco (ArUco-based — handles logos, occlusion, perspective)
  Engine 3: OpenCV classic QRCodeDetector (baseline fallback)
Each engine is tried on each preprocessed image variant until one succeeds.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

# Ensure Windows finds pyzbar's native DLLs (libzbar-64.dll + msvcr120.dll)
if sys.platform == "win32":
    try:
        pyzbar_dir = os.path.join(sys.prefix, "Lib", "site-packages", "pyzbar")
        if os.path.isdir(pyzbar_dir) and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(pyzbar_dir)
    except Exception:
        pass

import cv2
import numpy as np

from schemas.qr import QRDecodeResult, QRPayloadType
from core.logging_config import get_logger

logger = get_logger(__name__)

import re

_UPI_PREFIXES = ("upi://", "phonepe://", "gpay://", "paytm://")
_EMAIL_PREFIXES = ("mailto:",)
_PHONE_PREFIXES = ("tel:", "sms:", "smsto:")
_WIFI_PREFIXES = ("wifi:", "WIFI:")
_VCARD_PREFIXES = ("BEGIN:VCARD",)


def _classify_payload(payload: str) -> QRPayloadType:
    """Classify raw QR payload into a type."""
    if not payload:
        return QRPayloadType.UNKNOWN
    lower = payload.lower().strip()
    if any(lower.startswith(p) for p in _UPI_PREFIXES):
        return QRPayloadType.UPI_PAYMENT
    if "pa=" in lower and ("upi" in lower or "vpa" in lower):
        return QRPayloadType.UPI_PAYMENT
    if lower.startswith("https://"):
        return QRPayloadType.URL_HTTPS
    if lower.startswith("http://"):
        return QRPayloadType.URL_HTTP
    if any(lower.startswith(p) for p in _EMAIL_PREFIXES):
        return QRPayloadType.EMAIL
    if any(lower.startswith(p) for p in _PHONE_PREFIXES):
        return QRPayloadType.PHONE
    if any(lower.startswith(p.lower()) for p in _WIFI_PREFIXES):
        return QRPayloadType.WIFI
    if any(lower.startswith(p.lower()) for p in _VCARD_PREFIXES):
        return QRPayloadType.VCARD

    # Bare domain / URL without scheme:
    # 1. IP address host (e.g. 192.168.1.1/admin)
    if re.match(r"^(\d{1,3}\.){3}\d{1,3}(:\d+)?(/.*)?$", lower):
        return QRPayloadType.URL_HTTP

    # 2. Hostname with recognized domain suffix or www. (e.g. www.site.com, site.com/path)
    if re.match(r"^(www\.|[a-z0-9]([a-z0-9\-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9\-]*[a-z0-9])?)*\.[a-z]{2,63}(:\d+)?)(/.*)?$", lower):
        return QRPayloadType.URL_HTTPS

    return QRPayloadType.TEXT


class QRDecoder:
    """Multi-engine QR decoder with pyzbar, QRCodeDetectorAruco, and QRCodeDetector."""

    def __init__(self) -> None:
        self._aruco_detector: Optional[cv2.QRCodeDetectorAruco] = None
        self._classic_detector: Optional[cv2.QRCodeDetector] = None
        try:
            if hasattr(cv2, "QRCodeDetectorAruco"):
                self._aruco_detector = cv2.QRCodeDetectorAruco()
                logger.debug("QRCodeDetectorAruco initialized")
        except Exception as exc:
            logger.debug("QRCodeDetectorAruco init failed", error=str(exc))
        try:
            self._classic_detector = cv2.QRCodeDetector()
        except Exception as exc:
            logger.debug("QRCodeDetector init failed", error=str(exc))

    def decode(self, image: np.ndarray) -> QRDecodeResult:
        """
        Attempt decoding with all three engines in order.
        Returns the first successful result.
        """
        if image is None or image.size == 0:
            return _failed()

        result = self._try_pyzbar(image)
        if result:
            return result

        result = self._try_aruco(image)
        if result:
            return result

        result = self._try_classic(image)
        if result:
            return result

        return _failed()

    # ------------------------------------------------------------------ #
    #  Engine implementations
    # ------------------------------------------------------------------ #

    def _try_pyzbar(self, image: np.ndarray) -> Optional[QRDecodeResult]:
        try:
            from pyzbar.pyzbar import decode as pyzbar_decode
            for obj in pyzbar_decode(image):
                if obj.type == "QRCODE" and obj.data:
                    payload = obj.data.decode("utf-8", errors="replace").strip()
                    if payload:
                        logger.debug("pyzbar decoded", payload_len=len(payload))
                        return _result(payload, 1.0, "pyzbar")
        except Exception as exc:
            logger.debug("pyzbar decode failed", error=str(exc))
        return None

    def _try_aruco(self, image: np.ndarray) -> Optional[QRDecodeResult]:
        if self._aruco_detector is None:
            return None
        try:
            gray = _to_gray(image)
            data, _, _ = self._aruco_detector.detectAndDecode(gray)
            if data and data.strip():
                logger.debug("aruco decoded")
                return _result(data.strip(), 0.92, "opencv_aruco")
        except Exception as exc:
            logger.debug("aruco decode failed", error=str(exc))
        return None

    def _try_classic(self, image: np.ndarray) -> Optional[QRDecodeResult]:
        if self._classic_detector is None:
            return None
        try:
            gray = _to_gray(image)
            data, _, _ = self._classic_detector.detectAndDecode(gray)
            if data and data.strip():
                logger.debug("classic opencv decoded")
                return _result(data.strip(), 0.85, "opencv_classic")
        except Exception as exc:
            logger.debug("classic opencv decode failed", error=str(exc))
        return None


# ------------------------------------------------------------------ #
#  Helpers
# ------------------------------------------------------------------ #

def _to_gray(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image


def _result(payload: str, confidence: float, decoder: str) -> QRDecodeResult:
    return QRDecodeResult(
        decoded=True,
        payload=payload,
        payload_type=_classify_payload(payload),
        confidence=confidence,
        decoder_used=decoder,
    )


def _failed() -> QRDecodeResult:
    return QRDecodeResult(
        decoded=False,
        payload=None,
        payload_type=QRPayloadType.UNKNOWN,
        confidence=0.0,
        decoder_used="none",
    )
