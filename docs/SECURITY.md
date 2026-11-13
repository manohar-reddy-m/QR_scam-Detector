# QR Sentinel — Security Hardening & Zero-Execution Policy

## 1. Zero-Execution Architecture

> [!IMPORTANT]
> **Fundamental Security Principle**
> QR Sentinel treats all decoded QR contents and uploaded files as untrusted, potentially hostile data.
> The platform enforces a strict **Zero-Execution, Zero-Auto-Navigation** policy.

### Safeguards Implemented:
1. **No Automatic Browser Navigation:** URLs extracted from QR codes are never opened in a client web view, headless browser, or iframe.
2. **No Remote Content Downloading:** The URL intelligence engine performs strictly offline, static structural analysis. It never makes outbound HTTP requests to the target destination, does not resolve DNS records, and never downloads remote payloads.
3. **No Automatic Financial Execution:** Decoded UPI or banking payloads (e.g., `upi://pay`) are parsed for indicators and displayed as text. No payment apps, deep links, or intents are ever triggered automatically.

---

## 2. Input Validation at System Boundaries

### Optical & File Upload Security:
- **Magic Byte Verification:** File signatures are inspected at the binary level. A text or script file renamed with a `.png` extension is rejected immediately with HTTP 415 (Unsupported Media Type).
- **Upload Size Limit:** Capped at 10 MB per request to prevent Denial-of-Service (DoS) and decompression bombs.
- **Dimension Clamping:** Images exceeding 4096×4096 pixels are rejected before feeding into OpenCV image filters.
- **In-Memory Buffering:** Files are processed as in-memory byte streams (`BytesIO`), preventing path traversal or temporary file leakage on disk.

### URL & Payload Security:
- **String Length Limits:** Target URLs are restricted to 2048 characters to mitigate regex catastrophic backtracking (ReDoS).
- **Control Character & Null Byte Handling:** Strips null bytes (`\x00`) and unprintable control characters before regex matching.

---

## 3. Defense-in-Depth Exception Handling

- **No Stack Trace Leakage:** Production exception handlers catch domain and unexpected errors, returning structured JSON with an ephemeral 8-character `request_id` for auditing without exposing file paths, libraries, or memory addresses.
- **CORS Restriction:** Configurable via `ALLOWED_ORIGINS` in `.env`. Defaults to specific frontend localhost ports.
- **Structured JSON Logging:** Redacts potential PII or authorization tokens from access and application logs.

---

## 4. Responsible Disclosure

If you discover a security vulnerability in QR Sentinel, please open an issue or contact the security team directly. Do not publicly disclose vulnerabilities before a patch has been released.

