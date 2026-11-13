"""
QR Sentinel — Industrial-Grade Risk Assessment Engine.
Combines Optical Evidence, Payload Context, Deterministic Signatures,
Combosquatting / Phishing Topology Analysis, and Calibrated ML Inference with Explainable Rationale.
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from schemas.common import RiskIndicator, RiskLevel
from schemas.url import URLFeatures
from schemas.qr import QRDecodeResult, QRPayloadType
from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)

RiskAssessment = Tuple[RiskLevel, float, List[RiskIndicator], str]

# High-reputation benign apex domains
HIGH_REPUTATION_DOMAINS = {
    # Search & Technology
    "google.com", "google.co.in", "google.co.uk", "googleusercontent.com", "gstatic.com", "gmail.com",
    "youtube.com", "youtu.be", "android.com",
    "microsoft.com", "microsoftonline.com", "live.com", "office.com", "azure.com", "windows.net", "bing.com",
    "visualstudio.com", "sharepoint.com", "outlook.com",
    "apple.com", "icloud.com",
    "amazon.com", "amazon.in", "amazon.co.uk", "amazonaws.com",
    # Developer & Open Source
    "github.com", "github.io", "gitlab.com", "bitbucket.org", "stackoverflow.com", "stackexchange.com",
    "python.org", "pypi.org", "npm.im", "npmjs.com", "cloudflare.com", "mozilla.org",
    # Knowledge & Reference
    "wikipedia.org", "wikimedia.org", "nih.gov", "who.int", "cdc.gov",
    # Social & Content
    "reddit.com", "spotify.com", "medium.com", "nytimes.com", "bbc.com", "bbc.co.uk", "cnn.com",
    "slack.com", "zoom.us", "stripe.com", "openai.com", "uber.com", "airbnb.com",
    "walmart.com", "dropbox.com", "adobe.com", "salesforce.com", "shopify.com",
    "twitch.tv", "vimeo.com", "pinterest.com", "quora.com", "tumblr.com", "yahoo.com", "x.com",
    # Financial & Commerce
    "paypal.com", "netflix.com", "facebook.com", "instagram.com", "whatsapp.com"
}

# Typosquat patterns: character & digit substitutions targeting famous brands
_TYPOSQUAT_BRANDS = {
    "paypal": ["paypa1", "paypai", "paypa|", "paypa!"],
    "google": ["g00gle", "g0ogle", "googIe", "g00g1e"],
    "amazon": ["amaz0n", "amazoon", "amаzon"],
    "apple":  ["app1e", "appIe"],
    "microsoft": ["micros0ft", "microsofit", "msft"],
    "netflix": ["netf1ix", "netfl1x"],
    "facebook": ["faceb00k", "facebok"],
    "instagram": ["1nstagram", "instagr4m"],
    "linkedin": ["1inkedin", "linkedln"],
    "twitter": ["twltter", "tw1tter"],
}

# Famous brand keywords frequently abused in combosquatting and subdomain spoofing
_ABUSED_BRAND_NAMES = {
    "paypal", "amazon", "google", "apple", "microsoft", "netflix",
    "facebook", "instagram", "whatsapp", "twitter", "linkedin",
    "bankofamerica", "wellsfargo", "chase", "citibank", "binance",
    "coinbase", "metamask", "steam", "adobe", "dhl", "fedex", "ups",
    "hdfc", "icici", "sbi"
}

# Phishing / social engineering lure keywords
_PHISHING_LURE_KEYWORDS = {
    "login", "signin", "sign-in", "log-in", "verify", "verification",
    "secure", "security", "account", "update", "billing", "confirm",
    "support", "helpdesk", "customercare", "recover", "recovery",
    "wallet", "alert", "portal", "auth", "authorize", "session",
    "service", "kyc", "refund", "password", "credential", "id"
}

# Dangerous file extensions often delivered via malicious QR codes
EXECUTABLE_EXTENSIONS = (
    ".exe", ".apk", ".bat", ".cmd", ".vbs", ".ps1", ".scr", ".msi",
    ".jar", ".hta", ".iso", ".dmg", ".dll"
)

# Known legitimate UPI bank PSP handles
KNOWN_UPI_HANDLES = {
    "okaxis", "okhdfcbank", "oksbi", "okicici", "paytm", "ybl", "ibl", "axl",
    "upi", "apl", "barodampay", "fbl", "idfcbank", "kotak", "indus", "postbank",
    "aubank", "federal", "airtel", "jupiteraxis", "slice"
}

# Keywords frequently abused in UPI fake refund / imposter scams
UPI_SCAM_KEYWORDS = [
    "customercare", "helpdesk", "support", "refund", "lottery", "cashback",
    "kyc", "electricity", "billdesk", "rewards", "bonus", "winner", "survey"
]


class RiskEngine:
    """Multi-stage, reliability-aware threat assessment engine."""

    def assess(
        self,
        features: Optional[URLFeatures],
        ml_score: Optional[float],
        decode_result: Optional[QRDecodeResult] = None,
        raw_payload: Optional[str] = None,
    ) -> RiskAssessment:
        # Determine payload type
        payload_type = decode_result.payload_type if decode_result else QRPayloadType.UNKNOWN
        payload = raw_payload or (decode_result.payload if decode_result else "") or ""

        if payload_type == QRPayloadType.UNKNOWN and payload:
            from services.qr_decoder import _classify_payload
            payload_type = _classify_payload(payload)

        # Case 1: Decoding failed
        if decode_result and not decode_result.decoded:
            return (
                RiskLevel.INCONCLUSIVE,
                0.0,
                [],
                "QR code could not be optically decoded. Image may be excessively blurry, occluded, or distorted.",
            )

        # Case 2: UPI Payment Payload
        if payload_type == QRPayloadType.UPI_PAYMENT or payload.lower().startswith("upi://"):
            return self._assess_upi_payload(payload)

        # Case 3: Explicit non-URL payloads (WiFi, vCard, Email, Phone, or pure non-URL text without features)
        is_explicit_non_url = (
            payload_type in (QRPayloadType.EMAIL, QRPayloadType.PHONE, QRPayloadType.WIFI, QRPayloadType.VCARD)
            or (decode_result is not None and payload_type == QRPayloadType.TEXT and features is None)
        )
        if is_explicit_non_url:
            return self._assess_non_url_payload(payload_type, payload)

        # Case 4: Web URL Payloads (HTTP / HTTPS / Bare Domains)
        if features is None:
            return (
                RiskLevel.INCONCLUSIVE,
                0.0,
                [],
                "No URL structure available for security feature extraction.",
            )

        return self._assess_url_payload(features, ml_score, payload)

    def _assess_url_payload(
        self,
        features: URLFeatures,
        ml_score: Optional[float],
        raw_url: str,
    ) -> RiskAssessment:
        import ipaddress
        indicators: List[RiskIndicator] = []
        parsed = urlparse(raw_url if "://" in raw_url else f"https://{raw_url}")
        hostname = (parsed.hostname or "").lower()
        path = (parsed.path or "").lower()

        # Check for apex domain and trusted status
        host_parts = hostname.split(".")
        apex_domain = ".".join(host_parts[-2:]) if len(host_parts) >= 2 else hostname
        is_known_trusted = (
            apex_domain in HIGH_REPUTATION_DOMAINS
            or hostname in HIGH_REPUTATION_DOMAINS
            or any(hostname == d or hostname.endswith("." + d) for d in HIGH_REPUTATION_DOMAINS)
            or hostname.endswith((".gov", ".mil", ".edu"))
        )

        # --- Rule 1: IP Address Host (CRITICAL for public IP, LOW for private local IP) ---
        is_ip = features.has_ip_host
        is_private_ip = False
        if is_ip:
            try:
                ip_obj = ipaddress.ip_address(hostname)
                is_private_ip = ip_obj.is_private or ip_obj.is_loopback
            except ValueError:
                pass

        indicators.append(RiskIndicator(
            name="IP_HOST",
            description="URL uses a public raw IP address instead of a registered domain name, bypassing DNS reputation",
            severity="HIGH",
            triggered=is_ip and not is_private_ip,
        ))

        indicators.append(RiskIndicator(
            name="LOCAL_NETWORK_IP",
            description="URL targets a private RFC-1918 / loopback local address (e.g. router admin console or local dev server)",
            severity="LOW",
            triggered=is_private_ip,
        ))

        # --- Rule 2: Deceptive @ Symbol (CRITICAL) ---
        has_at = features.num_at > 0
        indicators.append(RiskIndicator(
            name="AT_SYMBOL",
            description="URL contains an '@' symbol in the authority, frequently used to mislead users about destination",
            severity="HIGH",
            triggered=has_at,
        ))

        # --- Rule 3: Punycode / IDN Homograph (CRITICAL) ---
        has_punycode = features.has_punycode
        indicators.append(RiskIndicator(
            name="PUNYCODE_HOMOGRAPH",
            description="Domain contains Punycode ('xn--'), characteristic of character spoofing/homograph attacks",
            severity="HIGH",
            triggered=has_punycode,
        ))

        # --- Rule 4: Suspicious TLD (HIGH) ---
        has_sus_tld = features.has_suspicious_tld
        indicators.append(RiskIndicator(
            name="SUSPICIOUS_TLD",
            description="Domain uses a top-level domain frequently associated with spam, phishing, and malware",
            severity="HIGH",
            triggered=has_sus_tld,
        ))

        # --- Rule 5: Typosquat / Character Substitution (HIGH) ---
        is_typosquat = False
        if not is_known_trusted:
            for brand, variants in _TYPOSQUAT_BRANDS.items():
                if any(hostname == v or hostname.startswith(v + ".") for v in variants):
                    if not (apex_domain.startswith(brand + ".") or apex_domain == brand):
                        is_typosquat = True
                        break
        indicators.append(RiskIndicator(
            name="BRAND_TYPOSQUAT",
            description="Hostname closely mimics a well-known brand through character substitution (e.g. '1' for 'l', '0' for 'o')",
            severity="HIGH",
            triggered=is_typosquat,
        ))

        # --- Rule 6: Brand Name in Subdomain (HIGH) ---
        # e.g. paypal.com.secure.login.ru — apex is 'login.ru', 'paypal' is a subdomain
        is_brand_subdomain = False
        subdomain_part = ".".join(host_parts[:-2]).lower() if len(host_parts) > 2 else ""
        if subdomain_part and not is_known_trusted:
            for b in _ABUSED_BRAND_NAMES:
                if b in subdomain_part and not (apex_domain.startswith(b + ".") or apex_domain == b):
                    is_brand_subdomain = True
                    break
        indicators.append(RiskIndicator(
            name="BRAND_IN_SUBDOMAIN",
            description="A well-known brand name appears as a subdomain of an unrelated apex domain — classic phishing structure",
            severity="HIGH",
            triggered=is_brand_subdomain,
        ))

        # --- Rule 7: Combosquatting / Brand Lure Keyword Stuffing (HIGH) ---
        # e.g. paypal-security-update.com, appleid-verify.com
        is_combosquat = False
        if not is_known_trusted and not is_typosquat:
            for b in _ABUSED_BRAND_NAMES:
                if b in hostname and not (apex_domain.startswith(b + ".") or apex_domain == b):
                    for kw in _PHISHING_LURE_KEYWORDS:
                        if kw in hostname or kw in path:
                            is_combosquat = True
                            break
                    if is_combosquat:
                        break
        indicators.append(RiskIndicator(
            name="COMBOSQUATTING",
            description="Domain combines a brand name with security, verification, or account lure keywords to deceive users",
            severity="HIGH",
            triggered=is_combosquat,
        ))

        # --- Rule 8: Executable / Script Download (HIGH) ---
        has_exec_ext = any(path.endswith(ext) for ext in EXECUTABLE_EXTENSIONS)
        indicators.append(RiskIndicator(
            name="EXECUTABLE_PAYLOAD",
            description="URL targets a direct download of an executable, installer, or script (.exe, .apk, .bat, .iso)",
            severity="HIGH",
            triggered=has_exec_ext,
        ))

        # --- Rule 9: Missing HTTPS Encryption (MEDIUM) ---
        # For known high-reputation domains, modern browsers enforce HSTS automatically
        no_https = not features.has_https and not is_known_trusted and not is_private_ip
        indicators.append(RiskIndicator(
            name="NO_HTTPS",
            description="Connection lacks transport encryption (HTTP only); vulnerable to eavesdropping and credential theft",
            severity="MEDIUM",
            triggered=no_https,
        ))

        # --- Rule 10: URL Shortener (MEDIUM) ---
        is_short = features.is_shortened_url
        indicators.append(RiskIndicator(
            name="URL_SHORTENER",
            description="Destination is hidden behind a URL shortening service (destination cannot be verified offline)",
            severity="MEDIUM",
            triggered=is_short,
        ))

        # --- Rule 11: Double Slash Open Redirect (MEDIUM) ---
        has_double_slash = features.has_double_slash
        indicators.append(RiskIndicator(
            name="DOUBLE_SLASH_REDIRECT",
            description="URL resource path contains '//', characteristic of open-redirect exploitation",
            severity="MEDIUM",
            triggered=has_double_slash,
        ))

        # --- Rule 12: Excessive Subdomains (MEDIUM) ---
        excess_subdomains = features.num_subdomains >= 3 and not is_known_trusted
        indicators.append(RiskIndicator(
            name="EXCESSIVE_SUBDOMAINS",
            description="Hostname contains 3 or more subdomain levels, often used to disguise brand names in FQDN",
            severity="MEDIUM",
            triggered=excess_subdomains,
        ))

        # --- Rule 13: High Obfuscation / Entropy (LOW) ---
        # Trigger only on actual obfuscation: % in hostname, traversal/null-bytes, or extreme ratio
        high_obfuscation = (
            ("%" in hostname)
            or ("%00" in raw_url.lower() or "%2f%2f" in raw_url.lower())
            or (features.num_percent_encoded >= 8)
            or (features.special_char_ratio > 0.20)
        )
        indicators.append(RiskIndicator(
            name="HIGH_OBFUSCATION",
            description="URL contains high density of percent-encoded hexadecimal sequences or special symbols",
            severity="LOW",
            triggered=high_obfuscation,
        ))

        # --- High-Reputation Trust Indicator ---
        if is_known_trusted and not (is_ip and not is_private_ip) and not has_at and not has_double_slash and not has_exec_ext:
            indicators.append(RiskIndicator(
                name="RECOGNIZED_TRUSTED_DOMAIN",
                description=f"Destination '{hostname}' belongs to verified high-reputation domain '{apex_domain}'",
                severity="LOW",
                triggered=False,
            ))
            score = 0.0
            explanation = (
                f"Website '{hostname}' is SAFE (LOW RISK - No threat detected). Threat Score: 0%. "
                f"Verified high-reputation domain '{apex_domain}'. "
                f"No phishing, typosquatting, or deceptive redirect markers identified."
            )
            return RiskLevel.LOW, score, indicators, explanation

        # --- Compute Deterministic Heuristic Risk Score ---
        critical_count = sum(1 for i in indicators if i.triggered and i.severity == "HIGH")
        medium_count = sum(1 for i in indicators if i.triggered and i.severity == "MEDIUM")

        # Heuristic baseline
        if critical_count >= 2:
            heuristic_score = 0.88
        elif critical_count == 1:
            heuristic_score = 0.70
        elif medium_count >= 2:
            heuristic_score = 0.50
        elif medium_count == 1:
            heuristic_score = 0.35
        elif is_private_ip:
            heuristic_score = 0.15
        else:
            # Clean site with no active threat indicators
            heuristic_score = 0.0

        # Adjust heuristic if shortener is present
        if is_short:
            heuristic_score = max(heuristic_score, 0.40)

        # Combine with ML score if available
        if ml_score is not None:
            if critical_count >= 1:
                composite = max(heuristic_score, 0.5 * heuristic_score + 0.5 * ml_score)
            elif medium_count >= 1:
                composite = 0.45 * ml_score + 0.55 * heuristic_score
            elif is_private_ip:
                composite = 0.15
            else:
                # Clean URLs with zero triggers must have 0.0 threat score (no phantom threat)
                composite = 0.0
        else:
            composite = heuristic_score

        composite = round(min(max(composite, 0.0), 1.0), 3)

        # Categorize
        if critical_count >= 1 or composite >= settings.RISK_HIGH_THRESHOLD:
            level = RiskLevel.HIGH
        elif is_short or medium_count >= 1 or composite >= settings.RISK_LOW_THRESHOLD:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
            composite = 0.0

        explanation = self._build_url_explanation(hostname, level, composite, indicators, ml_score, is_known_trusted)
        return level, composite, indicators, explanation

    def _assess_upi_payload(self, payload: str) -> RiskAssessment:
        indicators: List[RiskIndicator] = []
        parsed = urlparse(payload)
        qs = parse_qs(parsed.query)

        pa_list = qs.get("pa", [])
        pn_list = qs.get("pn", [])
        am_list = qs.get("am", [])

        pa = pa_list[0].strip() if pa_list else ""
        pn = pn_list[0].strip() if pn_list else ""
        am = am_list[0].strip() if am_list else None

        # Check VPA format
        has_vpa = "@" in pa
        vpa_parts = pa.split("@") if has_vpa else []
        handle = vpa_parts[1].lower() if len(vpa_parts) == 2 else ""

        is_known_handle = handle in KNOWN_UPI_HANDLES
        name_lower = pn.lower()
        has_scam_keyword = any(kw in name_lower or kw in pa.lower() for kw in UPI_SCAM_KEYWORDS)

        indicators.append(RiskIndicator(
            name="VALID_VPA_SYNTAX",
            description="Payload specifies a syntactically valid Virtual Payment Address (username@handle)",
            severity="MEDIUM",
            triggered=not has_vpa,
        ))

        indicators.append(RiskIndicator(
            name="KNOWN_BANK_PSP_HANDLE",
            description="VPA uses an officially registered Indian banking PSP handle (e.g. oksbi, okhdfcbank, paytm, ybl)",
            severity="LOW",
            triggered=not is_known_handle if has_vpa else False,
        ))

        indicators.append(RiskIndicator(
            name="IMPOSTER_SCAM_KEYWORDS",
            description="Payee name contains deceptive urgency keywords (e.g. 'refund', 'customercare', 'lottery')",
            severity="HIGH",
            triggered=has_scam_keyword,
        ))

        if not has_vpa:
            return (
                RiskLevel.HIGH,
                0.85,
                indicators,
                "Malformed or suspicious UPI payment payload: missing valid Payee VPA address ('pa' parameter).",
            )

        if has_scam_keyword:
            return (
                RiskLevel.HIGH,
                0.78,
                indicators,
                f"High-risk UPI payment destination: Payee name '{pn}' uses known phishing/social-engineering refund keywords.",
            )

        # Standard merchant or P2P payment
        score = 0.15 if is_known_handle else 0.32
        level = RiskLevel.LOW if is_known_handle else RiskLevel.MEDIUM
        explanation = (
            f"Valid UPI payment request to '{pn or pa}' via bank handle '@{handle}'. "
            f"Always inspect the payee identity and requested amount ({'INR ' + am if am else 'unspecified'}) "
            f"in your payment app before entering your UPI PIN."
        )
        return level, score, indicators, explanation

    def _assess_non_url_payload(self, payload_type: QRPayloadType, payload: str) -> RiskAssessment:
        indicators: List[RiskIndicator] = []

        # Check for potential script injection or command execution
        has_script = bool(re.search(r"<\s*script|javascript:|eval\(|powershell|cmd\.exe", payload, re.IGNORECASE))
        if has_script:
            indicators.append(RiskIndicator(
                name="CODE_INJECTION_PATTERN",
                description="Plaintext payload contains command shell or JavaScript script tags",
                severity="HIGH",
                triggered=True,
            ))
            return (
                RiskLevel.HIGH,
                0.80,
                indicators,
                "Plaintext payload contains suspicious script syntax or shell command invocations.",
            )

        if payload_type == QRPayloadType.WIFI:
            is_open_network = "T:nopass" in payload or "T:none" in payload.lower()
            indicators.append(RiskIndicator(
                name="UNENCRYPTED_WIFI",
                description="WiFi network configuration specifies open/unencrypted connection (no WPA2/WPA3 password)",
                severity="MEDIUM",
                triggered=is_open_network,
            ))
            level = RiskLevel.MEDIUM if is_open_network else RiskLevel.LOW
            score = 0.40 if is_open_network else 0.10
            return (
                level,
                score,
                indicators,
                f"WiFi connection configuration. {'Warning: Network is unencrypted (open hotspot).' if is_open_network else 'WPA-secured network profile.'}",
            )

        # Normal text / vCard / email / phone
        return (
            RiskLevel.INCONCLUSIVE,
            0.0,
            indicators,
            f"Payload type is {payload_type}. This is not a web URL; optical decoding succeeded but automated URL threat modeling is not applicable.",
        )

    def _build_url_explanation(
        self,
        hostname: str,
        level: RiskLevel,
        score: float,
        indicators: List[RiskIndicator],
        ml_score: Optional[float],
        is_known_trusted: bool,
    ) -> str:
        triggered = [i.name for i in indicators if i.triggered]
        site_name = hostname or "Target Link"

        if level == RiskLevel.LOW:
            return (
                f"Website '{site_name}' is SAFE (LOW RISK - No threat detected). Threat Score: 0%. "
                f"No phishing, typosquatting, or malicious signatures found. "
                f"Transport encryption and domain topology are clean and verified."
            )
        elif level == RiskLevel.HIGH:
            trig_desc = ", ".join(triggered) if triggered else "Malicious structural anomaly"
            return (
                f"Website '{site_name}' carries HIGH THREAT (DANGEROUS LINK). Threat Score: {int(score * 100)}%. "
                f"CRITICAL: Strong indicators of phishing, quishing, or credential theft ({trig_desc}). "
                f"Do NOT visit or interact with this destination."
            )
        else:
            trig_desc = ", ".join(triggered) if triggered else "Ambiguous link structure"
            return (
                f"Website '{site_name}' requires CAUTION (SUSPICIOUS LINK). Threat Score: {int(score * 100)}%. "
                f"Detected potential risk indicators: {trig_desc}. "
                f"Verify destination authenticity before entering credentials or sensitive data."
            )
