"""
Image robustness tester — applies distortions to QR images and tests decodability.
"""
from __future__ import annotations

import io
from typing import List

import cv2
import numpy as np
from PIL import Image, ImageFilter

from schemas.qr import QRDistortResult
from core.logging_config import get_logger

logger = get_logger(__name__)


def _array_to_bytes(arr: np.ndarray) -> bytes:
    _, buf = cv2.imencode(".png", arr)
    return buf.tobytes()


class ImageRobustnessTester:
    """Apply standard distortions and test QR decodability."""

    def test_all(self, image_bytes: bytes, severity: float = 0.5) -> List[QRDistortResult]:
        from services.image_preprocessor import ImagePreprocessor
        from services.qr_decoder import QRDecoder

        preprocessor = ImagePreprocessor()
        decoder = QRDecoder()

        original_arr = preprocessor._bytes_to_array(image_bytes)
        if original_arr is None:
            return []

        distortions = {
            "blur": self._apply_blur,
            "noise": self._apply_noise,
            "rotate": self._apply_rotate,
            "compress": self._apply_compress,
            "brightness": self._apply_brightness,
            "crop": self._apply_crop,
        }

        results: List[QRDistortResult] = []
        for name, fn in distortions.items():
            try:
                distorted = fn(original_arr, severity)
                distorted_bytes = _array_to_bytes(distorted)
                variants = preprocessor.prepare_variants(distorted_bytes)
                decoded_payload = None
                still_decodable = False
                for img in variants:
                    r = decoder.decode(img)
                    if r.decoded:
                        still_decodable = True
                        decoded_payload = r.payload
                        break
                results.append(QRDistortResult(
                    distortion_type=name,
                    severity=severity,
                    still_decodable=still_decodable,
                    decoded_payload=decoded_payload,
                ))
            except Exception as exc:
                logger.warning("Distortion test failed", distortion=name, error=str(exc))
                results.append(QRDistortResult(
                    distortion_type=name,
                    severity=severity,
                    still_decodable=False,
                ))

        return results

    def _apply_blur(self, img: np.ndarray, severity: float) -> np.ndarray:
        ksize = max(1, int(severity * 20))
        if ksize % 2 == 0:
            ksize += 1
        return cv2.GaussianBlur(img, (ksize, ksize), 0)

    def _apply_noise(self, img: np.ndarray, severity: float) -> np.ndarray:
        noise = np.random.normal(0, severity * 50, img.shape).astype(np.int16)
        noisy = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        return noisy

    def _apply_rotate(self, img: np.ndarray, severity: float) -> np.ndarray:
        angle = severity * 45
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        return cv2.warpAffine(img, M, (w, h), borderValue=(255, 255, 255))

    def _apply_compress(self, img: np.ndarray, severity: float) -> np.ndarray:
        quality = max(1, int((1 - severity) * 95) + 5)
        pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        buf = io.BytesIO()
        pil.save(buf, format="JPEG", quality=quality)
        buf.seek(0)
        reloaded = Image.open(buf).convert("RGB")
        return cv2.cvtColor(np.array(reloaded), cv2.COLOR_RGB2BGR)

    def _apply_brightness(self, img: np.ndarray, severity: float) -> np.ndarray:
        factor = 1.0 + (severity - 0.5) * 1.5
        return np.clip(img.astype(np.float32) * factor, 0, 255).astype(np.uint8)

    def _apply_crop(self, img: np.ndarray, severity: float) -> np.ndarray:
        h, w = img.shape[:2]
        margin = int(severity * 0.15 * min(h, w))
        if margin < 1:
            return img
        return img[margin : h - margin, margin : w - margin]
