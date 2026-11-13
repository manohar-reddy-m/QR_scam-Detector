"""
Image preprocessing service.
Generates comprehensive multi-pass image variants for robust QR decoding.

Handles:
  - High-res phone photos (>1000px) → downscale to 800px
  - Low-res thumbnails (<400px) → upscale 3x
  - Tightly cropped images (no quiet zone) → white border padding
  - Dark-mode / inverted QRs (white code on dark bg) → polarity flip
  - Uneven lighting, shadows, glare → CLAHE normalization
  - WhatsApp/JPEG compression blur → sharpening kernel
  - Printed noise → morphological open
  - Binarization → Otsu + Adaptive Gaussian
  - Colored backgrounds → individual color channel extraction
"""
from __future__ import annotations

import io
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image, ImageEnhance

from core.logging_config import get_logger

logger = get_logger(__name__)


class ImagePreprocessor:
    """
    Generate ordered preprocessing variants of a raw image for QR decoding.
    Fast/most-common variants come first to minimize latency on clean images.
    """

    def prepare_variants(self, image_bytes: bytes) -> List[np.ndarray]:
        """Return an ordered list of numpy image arrays to try decoding."""
        variants: List[np.ndarray] = []

        try:
            original = self._bytes_to_array(image_bytes)
            if original is None:
                return []

            h, w = original.shape[:2]
            max_dim = max(h, w)

            # 1. Original BGR
            variants.append(original)

            # 2. Standard grayscale
            gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY) if len(original.shape) == 3 else original.copy()
            variants.append(gray)

            # 3. Quiet zone padding (critical for tightly cropped WhatsApp screenshots)
            pad = max(30, int(min(h, w) * 0.08))
            padded = cv2.copyMakeBorder(gray, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)
            variants.append(padded)

            # 4. Downscale for high-res phone photos (pyzbar fails on very large modules)
            if max_dim > 1000:
                s = 800.0 / max_dim
                small = cv2.resize(gray, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
                variants.append(small)
                variants.append(cv2.copyMakeBorder(small, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=255))

            # 5. Upscale for small thumbnails
            if max_dim < 400:
                s = min(3.0, 600.0 / max_dim)
                large = cv2.resize(gray, (int(w * s), int(h * s)), interpolation=cv2.INTER_CUBIC)
                variants.append(large)
                variants.append(cv2.copyMakeBorder(large, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=255))

            # 6. Inverted polarity (white-on-dark QR codes, dark mode screenshots)
            variants.append(cv2.bitwise_not(gray))
            variants.append(cv2.bitwise_not(padded))

            # 7. CLAHE — repairs shadows, glare, uneven phone lighting
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
            variants.append(clahe)
            variants.append(cv2.copyMakeBorder(clahe, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=255))

            # 8. Sharpening — counteracts JPEG/WhatsApp compression blur
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
            sharpened = cv2.filter2D(gray, -1, kernel)
            variants.append(sharpened)

            # 9. Otsu binarization
            _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append(otsu)
            variants.append(cv2.bitwise_not(otsu))  # inverted Otsu

            # 10. Adaptive Gaussian (handles uneven illumination better than global Otsu)
            adaptive = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            variants.append(adaptive)

            # 11. Morphological denoising (removes speckles from noisy prints/scans)
            k = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            variants.append(cv2.morphologyEx(gray, cv2.MORPH_OPEN, k))

            # 12. Individual color channels (for colored QR codes / tinted backgrounds)
            if len(original.shape) == 3 and original.shape[2] == 3:
                b, g_ch, r = cv2.split(original)
                variants.append(g_ch)   # green channel — best contrast in most camera sensors
                variants.append(r)

        except Exception as exc:
            logger.warning("Image preprocessing error", error=str(exc))

        return variants

    def _bytes_to_array(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Decode raw bytes into a numpy BGR array via PIL (handles EXIF rotation)."""
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))

            # Apply EXIF orientation so rotated phone photos decode correctly
            try:
                from PIL import ImageOps
                pil_img = ImageOps.exif_transpose(pil_img)
            except Exception:
                pass

            # Flatten transparency to white background
            if pil_img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                if pil_img.mode == "P":
                    pil_img = pil_img.convert("RGBA")
                if "A" in pil_img.mode:
                    bg.paste(pil_img, mask=pil_img.split()[-1])
                else:
                    bg.paste(pil_img)
                pil_img = bg
            elif pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")

            arr = np.array(pil_img)
            return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        except Exception as exc:
            logger.warning("Failed to open image bytes", error=str(exc))
            return None
