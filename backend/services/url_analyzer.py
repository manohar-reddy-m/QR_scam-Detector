"""
URL feature extraction service.
Extracts the 19 ML features from a URL string.
"""
from __future__ import annotations

import ipaddress
import re
from typing import Optional
from urllib.parse import urlparse

from core.config import settings
from schemas.url import URLFeatures


class URLAnalyzer:
    """Extract URLFeatures from a raw URL or QR payload string."""

    def extract_features(self, raw: str) -> URLFeatures:
        raw_clean = raw.strip()

        # Detect if user explicitly specified http:// or https://
        lower_raw = raw_clean.lower()
        explicit_http = lower_raw.startswith("http://")
        explicit_https = lower_raw.startswith("https://")

        if lower_raw.startswith("//"):
            url = "https:" + raw_clean
        elif not lower_raw.startswith(("http://", "https://", "upi://", "mailto:", "tel:")):
            # Default unspecified web destinations to https:// (standard modern browser convention)
            url = "https://" + raw_clean
        else:
            url = raw_clean

        try:
            parsed = urlparse(url)
        except Exception:
            parsed = urlparse("https://invalid.example")

        hostname = (parsed.hostname or "").lower()
        path = parsed.path or ""
        query = parsed.query or ""

        # has_ip_host
        has_ip_host = False
        try:
            ipaddress.ip_address(hostname)
            has_ip_host = True
        except ValueError:
            pass

        # subdomains
        hostname_parts = hostname.split(".")
        num_subdomains = max(0, len(hostname_parts) - 2) if len(hostname_parts) > 2 else 0

        # TLD check — matches any suspicious TLD at end of hostname
        has_suspicious_tld = any(
            hostname.endswith(t.lower()) or hostname.endswith(t.lower() + ":")
            for t in settings.SUSPICIOUS_TLDS
        )

        # URL shortener check — EXACT hostname or subdomain match (not broad substring)
        is_shortened_url = any(
            hostname == svc or hostname.endswith("." + svc)
            for svc in settings.URL_SHORTENERS
        )

        # punycode
        has_punycode = "xn--" in hostname

        # double slash in path
        has_double_slash = "//" in path

        # character ratios
        url_chars = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
        special_chars = re.findall(r"[^a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]", url_chars)
        special_char_ratio = len(special_chars) / max(len(url_chars), 1)
        digits = re.findall(r"\d", url_chars)
        digit_ratio = len(digits) / max(len(url_chars), 1)

        # HTTPS determination:
        # 1. Explicit https:// scheme
        # 2. Or a valid recognized domain structure without explicit http://
        is_domain = bool(hostname and "." in hostname and not re.search(r"[^a-zA-Z0-9.\-]", hostname))
        has_https = explicit_https or (is_domain and not explicit_http)

        return URLFeatures(
            url_length=len(url),
            hostname_length=len(hostname),
            num_subdomains=num_subdomains,
            has_https=has_https,
            has_ip_host=has_ip_host,
            num_dots=url.count("."),
            num_hyphens=url.count("-"),
            # RFC 3986 credential/authority spoofing: @ must be in netloc (authority), not in path/query
            # Path @ (e.g. youtube.com/@TED, medium.com/@author) is standard modern creator/channel handle
            num_at=parsed.netloc.count("@"),
            num_question_marks=url.count("?"),
            num_ampersands=url.count("&"),
            num_percent_encoded=url.count("%"),
            path_length=len(path),
            query_length=len(query),
            is_shortened_url=is_shortened_url,
            has_suspicious_tld=has_suspicious_tld,
            has_punycode=has_punycode,
            has_double_slash=has_double_slash,
            special_char_ratio=round(special_char_ratio, 4),
            digit_ratio=round(digit_ratio, 4),
        )
