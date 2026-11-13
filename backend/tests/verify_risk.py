"""Verification script to test RiskEngine with benign and malicious URLs and UPI payloads."""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from services.risk_engine import RiskEngine
from services.url_analyzer import URLAnalyzer
from services.feature_extractor import FeatureExtractor
from services.threat_classifier import ThreatClassifier

def test_engine():
    risk_engine = RiskEngine()
    url_analyzer = URLAnalyzer()
    extractor = FeatureExtractor()
    classifier = ThreatClassifier()
    classifier.load()

    cases = [
        # (payload, expected_risk_category, description)
        ("https://www.google.com/search?q=cybersecurity+defense", "LOW", "Safe Google query"),
        ("https://en.wikipedia.org/wiki/Phishing", "LOW", "Safe Wikipedia article"),
        ("https://github.com/torvalds/linux", "LOW", "Safe GitHub repository"),
        ("http://192.168.1.1/admin/login.php", "HIGH", "Phishing IP host"),
        ("http://login-appleid.verify-alert.tk/update", "HIGH", "Phishing .tk with deceptive subdomain"),
        ("http://bank-secure-login.com@phishing.site/account", "HIGH", "Credential @ obfuscation"),
        ("upi://pay?pa=merchant@oksbi&pn=Supermarket&am=250&cu=INR", "LOW", "Legitimate UPI merchant payment"),
        ("upi://pay?pa=scammer882@fakebank&pn=KycVerification&am=5000", "HIGH", "UPI scam with KYC/lottery keyword"),
        ("WIFI:S:HomeNet;T:WPA;P:SecretPass123;;", "LOW", "WPA secured WiFi"),
        ("WIFI:S:PublicAirport;T:nopass;;", "MEDIUM", "Unencrypted open WiFi"),
        ("Hello, this is a plain text greeting.", "INCONCLUSIVE", "Plain text message"),
    ]

    all_passed = True
    print(f"{'Description':<38} | {'Category':<12} | {'Score':<6} | {'Status'}")
    print("-" * 75)

    for payload, expected_cat, desc in cases:
        url_feats = url_analyzer.extract_features(payload)
        ml_score = None
        if classifier.is_loaded:
            vec = extractor.to_vector(url_feats)
            ml_score = classifier.predict_proba(vec)

        level, score, indicators, explanation = risk_engine.assess(url_feats, ml_score, raw_payload=payload)
        passed = (level.value == expected_cat)
        status_str = "PASS" if passed else f"FAIL (Expected {expected_cat})"
        if not passed:
            all_passed = False
        print(f"{desc:<38} | {level.value:<12} | {score:.2f}   | {status_str}")
        triggered = [i.name for i in indicators if i.triggered]
        if triggered:
            print(f"   -> Flags: {', '.join(triggered)}")

    print("-" * 75)
    print(f"Overall Result: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    return all_passed

if __name__ == "__main__":
    success = test_engine()
    sys.exit(0 if success else 1)
