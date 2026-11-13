"""Quick direct test - no HTTP, calls services directly."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Fix pyzbar DLL path on Windows
if sys.platform == "win32":
    pyzbar_dir = os.path.join(sys.prefix, "Lib", "site-packages", "pyzbar")
    if os.path.isdir(pyzbar_dir) and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(pyzbar_dir)

import io
import cv2
import qrcode
import numpy as np
from PIL import Image

from services.image_preprocessor import ImagePreprocessor
from services.qr_decoder import QRDecoder

preprocessor = ImagePreprocessor()
decoder = QRDecoder()


def make_qr_bytes(data, invert=False, blur_sigma=0, scale=1.0, border=4,
                  error_level=qrcode.constants.ERROR_CORRECT_M):
    qr = qrcode.QRCode(error_correction=error_level, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    fc = 'white' if invert else 'black'
    bc = 'black' if invert else 'white'
    arr = np.array(qr.make_image(fill_color=fc, back_color=bc).convert('L'))
    if blur_sigma > 0:
        arr = cv2.GaussianBlur(arr, (0, 0), blur_sigma)
    if scale != 1.0:
        h, w = arr.shape
        interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
        arr = cv2.resize(arr, (int(w * scale), int(h * scale)), interpolation=interp)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format='JPEG', quality=75)
    return buf.getvalue()


tests = [
    ('Clean HTTPS',       make_qr_bytes('https://www.google.com')),
    ('Clean UPI',         make_qr_bytes('upi://pay?pa=merchant@paytm&pn=Store&am=100')),
    ('Inverted polarity', make_qr_bytes('https://inverted.test', invert=True)),
    ('Blurred (s=3)',     make_qr_bytes('https://blurred.test', blur_sigma=3)),
    ('Blurred (s=5)',     make_qr_bytes('https://very-blurred.test', blur_sigma=5)),
    ('Small (0.4x)',      make_qr_bytes('https://tiny.test', scale=0.4)),
    ('Large (2.5x)',      make_qr_bytes('https://large.test', scale=2.5)),
    ('High ECC (H)',      make_qr_bytes('https://ecc-h.test', error_level=qrcode.constants.ERROR_CORRECT_H)),
    ('Zero quiet zone',   make_qr_bytes('https://zero-border.test', border=0)),
]

passed = 0
print('\n=== Direct Service QR Decode Test ===')
for name, data in tests:
    variants = preprocessor.prepare_variants(data)
    result = None
    for v in variants:
        r = decoder.decode(v)
        if r.decoded:
            result = r
            break
    ok = result is not None and result.decoded
    if ok:
        passed += 1
        payload = (result.payload or '')[:40]
        decoder_name = result.decoder_used
    else:
        payload = 'FAILED'
        decoder_name = 'none'
    print(f'  {"PASS" if ok else "FAIL"}  {name:<25}  decoder={decoder_name:<18}  {payload}')

print(f'\nResult: {passed}/{len(tests)} passed')

