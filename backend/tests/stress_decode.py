import io, requests, qrcode, numpy as np, cv2
from PIL import Image

API = 'http://127.0.0.1:8000/api/v1/qr/analyze'

def make_qr_bytes(data, invert=False, blur_sigma=0, scale=1.0, border=4, error_level=qrcode.constants.ERROR_CORRECT_M):
    qr = qrcode.QRCode(error_correction=error_level, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    fc = 'white' if invert else 'black'
    bc = 'black' if invert else 'white'
    arr = np.array(qr.make_image(fill_color=fc, back_color=bc).convert('L'))
    if blur_sigma > 0:
        arr = cv2.GaussianBlur(arr, (0,0), blur_sigma)
    if scale != 1.0:
        h, w = arr.shape
        interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
        arr = cv2.resize(arr, (int(w*scale), int(h*scale)), interpolation=interp)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format='JPEG', quality=75)
    return buf.getvalue()

tests = [
    ('Clean HTTPS',       make_qr_bytes('https://www.google.com')),
    ('Clean UPI',         make_qr_bytes('upi://pay?pa=merchant@paytm&pn=Store&am=100')),
    ('Inverted polarity', make_qr_bytes('https://inverted.test', invert=True)),
    ('Blurred (sigma=3)', make_qr_bytes('https://blurred.test', blur_sigma=3)),
    ('Blurred (sigma=5)', make_qr_bytes('https://very-blurred.test', blur_sigma=5)),
    ('Small (0.4x)',      make_qr_bytes('https://tiny.test', scale=0.4)),
    ('Large (2.5x)',      make_qr_bytes('https://large.test', scale=2.5)),
    ('High ECC level H',  make_qr_bytes('https://ecc-h.test', error_level=qrcode.constants.ERROR_CORRECT_H)),
    ('Zero quiet zone',   make_qr_bytes('https://zero-border.test', border=0)),
]

passed = 0
print('\n=== QR Decode Stress Test ===')
for name, data in tests:
    try:
        r = requests.post(API, files={'file': ('qr.jpg', data, 'image/jpeg')}, timeout=10)
        j = r.json()
        ok = j.get('qr', {}).get('decoded', False)
        payload = j.get('qr', {}).get('payload', 'N/A')[:40] if ok else 'FAILED'
        decoder = j.get('qr', {}).get('decoder_used', '?')
        status = 'PASS' if ok else 'FAIL'
        if ok:
            passed += 1
        print(f'  {status}  {name:<25}  decoder={decoder:<15}  {payload}')
    except Exception as e:
        print(f'  ERR   {name:<25}  {e}')

print(f'\nResult: {passed}/{len(tests)} passed')

