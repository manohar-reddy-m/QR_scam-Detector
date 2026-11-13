# 🔐 QR Sentinel — Threat Model

> This document describes the security threats QR Sentinel is designed to detect, the threats it cannot detect, and the assumptions underpinning its design.

---

## Threats Addressed

### 1. Quishing (QR Code Phishing)

**Description**: Attackers replace legitimate QR codes with malicious ones that redirect victims to phishing websites designed to steal credentials, PII, or financial information.

**How QR Sentinel helps**:
- Decodes the URL embedded in the QR code
- Applies ML classification and rule-based heuristics to identify phishing URL patterns (suspicious TLDs, IP-based hosts, excessive encoding, etc.)
- Returns a HIGH risk score with explanation

**Example**: A QR code on a restaurant table that leads to `http://pay-xnow.tk/order?session=abc` instead of the legitimate payment portal.

---

### 2. Malicious Redirection Chains

**Description**: A QR code encodes a seemingly innocuous URL that immediately redirects through one or more hops to a malicious destination.

**How QR Sentinel helps**:
- Flags URL shorteners (`is_shortened_url = 1`) as suspicious — shorteners are a common redirection obfuscation technique
- Flags double-slash injection (`has_double_slash`) used to bypass naive URL parsers
- Notes the presence of percent-encoded redirects in query strings

**Limitation**: QR Sentinel **does not follow redirects**. Only the initially encoded URL is analyzed.

---

### 3. Payment Fraud via UPI QR Codes

**Description**: Malicious QR codes encode UPI payment instructions with fraudulent merchant details, redirecting payments to attacker-controlled accounts.

**How QR Sentinel helps**:
- Identifies `upi://` prefix and `pa=` parameter to classify payload as `UPI_PAYMENT`
- Applies payload-type-specific risk rules for UPI QR codes
- Warns user to verify merchant name and UPI ID before completing payment

---

### 4. Homograph / IDN Attacks

**Description**: Domain names that visually resemble legitimate domains using Unicode characters (e.g., `gооgle.com` using Cyrillic 'о').

**How QR Sentinel helps**:
- Flags `has_punycode = 1` when the hostname contains `xn--` (Internationalized Domain Names are punycode-encoded)
- Contributes to elevated risk score

---

### 5. Credential Injection via URL

**Description**: URLs containing `@` character before the hostname (e.g., `https://google.com@evil.com/`) trick users into thinking they are on a legitimate domain.

**How QR Sentinel helps**:
- Counts `num_at` characters — presence of `@` in a URL is a strong phishing indicator
- High `num_at` values elevate risk score significantly

---

### 6. Suspicious TLD Abuse

**Description**: Free or low-cost TLDs (`.tk`, `.ml`, `.ga`, `.cf`, `.gq`, `.xyz`, `.click`, etc.) are disproportionately abused for phishing.

**How QR Sentinel helps**:
- `has_suspicious_tld` feature flags these TLDs
- Among the highest-weight features in the RF model

---

### 7. IP-Address-Based Hosting

**Description**: Phishing sites often use raw IP addresses as hostnames to bypass DNS-based blocklists.

**How QR Sentinel helps**:
- `has_ip_host` feature detects IPv4 and IPv6 addresses as hostnames
- Strong signal elevated by the Risk Engine with a rule-based bonus

---

## Threats NOT Addressed

> [!CAUTION]
> The following threats are **outside QR Sentinel's current scope**. Using it in contexts where these threats are relevant without additional controls is dangerous.

| Threat | Why Not Addressed | Mitigation Suggestion |
|---|---|---|
| **Destination page content** | QR Sentinel never fetches or renders the destination URL | Integrate a URL sandbox (e.g., VirusTotal, URLScan.io) |
| **Multi-hop redirects** | Only the first URL is analyzed; redirects are not followed | Use a redirect-following proxy before analysis |
| **DNS-based detection** | No DNS lookups are performed | Integrate with DNS RPZ or threat-feed DNS resolver |
| **QR code steganography** | Hidden data embedded within the QR image is not extracted | Advanced image analysis tools required |
| **Physical tampering detection** | Cannot tell if a QR code sticker was placed over a legitimate one | Physical inspection; tamper-evident QR mounts |
| **Legitimate-but-compromised domains** | A clean domain with a good reputation that hosts malicious content scores LOW | Integrate real-time domain reputation feeds |
| **Zero-day phishing domains** | New domains with no prior signals score based on structural features only | Combine with real-time threat intelligence |
| **Social engineering context** | QR codes in context (email, flyer) may carry social engineering; context is not analyzed | User education and policy controls |
| **Encrypted/obfuscated payloads** | QR codes encoding base64 or encrypted blobs that decode to URLs are not analyzed further | Layer with decryption / deobfuscation preprocessing |
| **QR codes in video or streams** | Static images only; no video frame extraction | Pre-process video frames before uploading |
| **Bluetooth/WiFi QR codes (beyond flagging)** | WIFI QR codes are identified but credentials are not validated | Manual credential review |
| **Non-URL non-UPI payloads (deep analysis)** | TEXT, EMAIL, PHONE payloads are decoded but not deeply analyzed | Extend feature extraction for these types |

---

## Security Assumptions

1. **Input is an image file** — the system assumes inputs are image files and validates this with MIME type checking and magic byte inspection. It does not parse arbitrary binary blobs.

2. **Network is untrusted** — the backend never makes outbound network requests. All analysis is local.

3. **Model artifacts are trusted** — `backend/models/` artifacts are assumed to be unmodified. If an attacker can replace `threat_classifier.joblib`, they control classification outcomes. Protect the models directory.

4. **Deployment is non-public (v1)** — the API has no authentication. It is assumed to run on `localhost` or a trusted internal network, not exposed to the internet.

5. **Users review results** — QR Sentinel provides risk guidance, not automated blocking. It assumes a human reviews the result before acting.

---

## Trust Boundaries

```
┌──────────────────────────────────────────────────┐
│  UNTRUSTED ZONE                                  │
│  • User-supplied image files                     │
│  • QR code payload content (ANY string)          │
│  • URL parameters embedded in QR codes           │
└────────────────────────┬─────────────────────────┘
                         │  sanitized via:
                         │  • Magic byte check
                         │  • File size limit
                         │  • NamedTemporaryFile isolation
                         │  • Pydantic schema validation
                         ▼
┌──────────────────────────────────────────────────┐
│  TRUSTED ZONE                                    │
│  • FastAPI application code                      │
│  • ML model artifacts (backend/models/)          │
│  • Feature extraction logic                      │
│  • Risk Engine rules                             │
└──────────────────────────────────────────────────┘
```

---

## Attack Surface Analysis

| Attack Vector | Surface | Mitigation in Place |
|---|---|---|
| Malformed image file | File upload endpoint | Magic byte check; OpenCV handles corrupt gracefully |
| Oversized file (DoS) | File upload endpoint | 10 MB hard limit |
| Path traversal via filename | File storage | `NamedTemporaryFile` with no user-controlled path |
| XSS via QR payload reflected in response | JSON response | Payload is JSON-encoded string; never rendered as HTML by backend |
| Model poisoning | Model artifacts | Out of scope for v1; protect models/ directory |
| Resource exhaustion (CPU-heavy QR decode) | Decode service | Rate limiting (30 req/min per IP) |
| SSRF (server fetching malicious URLs) | URL analyzer | The system never makes outbound HTTP requests |
| Pickle deserialization attacks | joblib model load | Models directory must be write-protected |

---

## Limitations and Caveats

1. **This is a demonstration tool**, not a certified security product.
2. ML scores are probabilities, not verdicts. A HIGH score means "strongly associated with known malicious patterns" — not "definitively malicious."
3. A LOW score does **not** mean safe — it means the URL structure does not match known malicious patterns in the synthetic training data.
4. **QR Sentinel cannot detect malicious intent** — only structural URL features that correlate with malicious behavior in historical data.
5. Attackers aware of the feature set can craft URLs that score LOW while still being malicious (adversarial evasion).
6. The model has not been adversarially tested.
7. **Do not auto-open URLs** based on a LOW risk score. Always have a human verify high-value actions.
