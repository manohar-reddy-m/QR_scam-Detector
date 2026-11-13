import requests

API = 'http://127.0.0.1:8000/api/v1/url/analyze'

tests = [
    ('https://www.google.com',                 'LOW'),
    ('https://www.wikipedia.org/wiki/Python',  'LOW'),
    ('https://github.com/torvalds/linux',      'LOW'),
    ('https://stackoverflow.com/questions/1',  'LOW'),
    ('http://192.168.1.1/admin/login.php',     'HIGH'),
    ('http://10.0.0.1/router/setup',           'HIGH'),
    ('http://free-giftcard.tk/win-now',        'HIGH'),
    ('http://bit.ly/3xAbc12',                  'MEDIUM'),
    ('https://tinyurl.com/abc12345',           'MEDIUM'),
    ('http://xn--80ak6aa92e.com/pay',          'HIGH'),
    ('https://amazon.com.phishing.tk',         'HIGH'),
    ('http://paypal.com.secure.login.ru/auth', 'HIGH'),
    ('http://evil.site/@admin/redirect',       'HIGH'),
    ('https://paypa1.com/secure-login',        'HIGH'),
    ('http://normal-site.com/page',            'MEDIUM'),
]

print()
print(f"  {'URL':<50} {'Expected':<10} {'Got':<10} {'Score':>7}  Result")
print('  ' + '-'*85)
passed = 0
for url, expected in tests:
    try:
        r = requests.post(API, json={'url': url}, timeout=8).json()
        got   = r.get('risk_level', '?')
        score = r.get('risk_score', 0)
        expl  = r.get('explanation', '')[:60]
        ok    = got == expected
        if ok:
            passed += 1
        mark = 'PASS' if ok else 'FAIL'
        print(f"  {url:<50} {expected:<10} {got:<10} {score:>7.3f}  {mark}")
        if not ok:
            print(f"    -> {expl}")
    except Exception as e:
        print(f"  {url:<50} {expected:<10} ERROR: {e}")

print()
print(f"  Result: {passed}/{len(tests)} correct")

